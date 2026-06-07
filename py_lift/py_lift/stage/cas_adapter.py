"""Adapter: turn a CAS view into a udapi ``Document`` the stage engine consumes.

The rule-based stage engine (:mod:`py_lift.stage.parser`) operates on udapi
``Node`` objects and expects, per token: ``form``, ``lemma``, ``upos``,
``xpos`` (STTS — finite verbs are detected via ``xpos.endswith("FIN")``),
``deprel``, ``head`` and ``misc["TopoField"]``.

This module reads those from the separate CAS annotation layers on a single
view (default ``ctok``) and emits a CoNLL-U string, which udapi parses into a
tree.  Token offsets in the CAS are carried through MISC as ``CasBegin`` /
``CasEnd`` so a later writer can anchor new annotations back onto the exact
source tokens.  Sentence-relative ordinals (1-based) are used as CoNLL-U IDs, 
so ``node.ord`` in the engine output matches the ordinals we record on 
output annotations.
"""
from __future__ import annotations

import re
from typing import Dict, Optional

import udapi
from cassis import Cas

from py_lift.dkpro import (
    T_LEMMA,
    T_POS,        # STTS (fine) POS  -> XPOS
    T_SENT,
    T_TOKEN,
    T_TOPOFIELD,
    T_UDEP,
    T_UPOS,       # Universal POS    -> UPOS
)

#: Default view to annotate.
DEFAULT_VIEW = "ctok"


def _by_begin(view: Cas, type_name: str, sent) -> Dict[int, object]:
    """Map begin-offset -> first annotation of ``type_name`` covered by ``sent``.

    The token, lemma, POS and topological-field layers carry one annotation per
    token at identical spans, so begin-offset is a reliable join key.
    """
    out: Dict[int, object] = {}
    for anno in view.select_covered(type_name, sent):
        out.setdefault(anno.begin, anno)
    return out


def _clean_form(text: str) -> str:
    """A CoNLL-U FORM must be a single non-empty field with no tab/newline."""
    form = re.sub(r"\s+", " ", text).strip()
    return form or "_"


def cas_view_to_conllu(view: Cas, view_name: str = DEFAULT_VIEW) -> str:
    """Serialise one CAS view to a CoNLL-U string (one block per Sentence)."""
    sofa = view.sofa_string
    sentences = sorted(view.select(T_SENT), key=lambda s: s.begin)
    blocks = []

    # UDependency feature structures carry no begin/end (they are pure
    # relations), so they cannot be fetched with offset-based select_covered.
    # Construct a global Dependent-token -> basic-dependency map once via select().
    dep_by_dependent: Dict[int, object] = {}
    for dep in view.select(T_UDEP):
        if getattr(dep, "flavor", "basic") not in (None, "basic"):
            continue
        dep_by_dependent.setdefault(dep.Dependent.xmiID, dep)

    for sent in sentences:
        tokens = sorted(view.select_covered(T_TOKEN, sent), key=lambda t: t.begin)
        if not tokens:
            continue

        # Sentence-relative ordinal (1-based, in text order). Equal to Token.id.
        ord_by_xmiid = {tok.xmiID: i for i, tok in enumerate(tokens, start=1)}

        lemma_at = _by_begin(view, T_LEMMA, sent)
        upos_at = _by_begin(view, T_UPOS, sent)
        xpos_at = _by_begin(view, T_POS, sent)
        topo_at = _by_begin(view, T_TOPOFIELD, sent)

        lines = [
            f"# sent_id = {view_name}_{sent.begin}_{sent.end}",
            "# text = " + _clean_form(sofa[sent.begin:sent.end]),
        ]

        for i, tok in enumerate(tokens, start=1):
            form = _clean_form(sofa[tok.begin:tok.end])
            le = lemma_at.get(tok.begin)
            up = upos_at.get(tok.begin)
            xp = xpos_at.get(tok.begin)
            tf = topo_at.get(tok.begin)

            lemma = (le.value if le else None) or "_"
            upos = (up.PosValue if up else None) or "_"
            xpos = (xp.PosValue if xp else None) or "_"
            topo: Optional[str] = tf.FieldValue if tf else None

            dep = dep_by_dependent.get(tok.xmiID)
            if dep is not None:
                gov_id = dep.Governor.xmiID
                if gov_id == tok.xmiID or gov_id not in ord_by_xmiid:
                    head, deprel = 0, "root"
                else:
                    head, deprel = ord_by_xmiid[gov_id], (dep.DependencyType or "dep")
            else:
                # No UDependency: keep the token in the tree as a root with its
                # own labelled function (better than dropping it).
                head = 0
                deprel = getattr(tok, "syntacticFunction", None) or "dep"

            misc_parts = []
            if topo is not None:
                misc_parts.append(f"TopoField={topo}")
            misc_parts.append(f"CasBegin={tok.begin}")
            misc_parts.append(f"CasEnd={tok.end}")
            misc = "|".join(misc_parts)

            # ID FORM LEMMA UPOS XPOS FEATS HEAD DEPREL DEPS MISC
            lines.append(
                "\t".join(
                    [str(i), form, lemma, upos, xpos, "_", str(head), deprel, "_", misc]
                )
            )

        blocks.append("\n".join(lines))

    # Terminate every sentence block with a blank line (canonical CoNLL-U).
    # udapi splits on "\n\n", so having a single trailing newline would 
    # otherwise glue an empty line onto the last block and mess up its reader.
    return "".join(block + "\n\n" for block in blocks)


def cas_view_to_udapi_doc(view: Cas, view_name: str = DEFAULT_VIEW) -> udapi.Document:
    """Build a udapi ``Document`` (one bundle per Sentence) from a CAS view."""
    doc = udapi.Document()
    doc.from_conllu_string(cas_view_to_conllu(view, view_name))
    return doc
