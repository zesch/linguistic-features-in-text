"""Rule-based German verb-placement stage annotator for py_lift.

For each target view (``ctok`` by default; ``*_th1`` etc. allowed; ``spacy_*``
views refused), this annotator:

1. converts the view's Token / Lemma / UD-POS / STTS-POS / UDependency /
   topological-field layers into a udapi document
   (:mod:`py_lift.stage.cas_adapter`),
2. runs the vendored rule engine (:func:`py_lift.stage.parser.analyze_single_document`),
3. writes results back onto the same view:

   * one ``org.dakoda.Stage`` per stage with a non-zero fine label
     (``name`` = coarse stage stem ADV/SVO/INV/SEP/VEND; ``fine`` = the
     fine-grained label such as ``SVO_core``/``SVO_peri``/``SVO_noev``/``NO_SEP``/``!SVO``;
     a stage is "fired" / coarse-positive iff ``fine`` ends in ``_core`` or ``_peri``),
   * one ``org.dakoda.StagedVerb`` per finite verb with clause-level info.

Predicted annotations carry ``origin="rule_based"`` so they are distinguishable
from gold ``Stage`` annotations (which have no ``origin``); ``overwrite=True``
removes only previously written annotations with the same ``origin``.
"""
from __future__ import annotations

import logging
from typing import List, Optional, Sequence

from cassis import Cas

from py_lift.annotators.api import SEL_BaseAnnotator
from py_lift.decorators import requires_types, supported_languages
from py_lift.dkpro import (
    T_LEMMA,
    T_POS,
    T_SENT,
    T_STAGE,
    T_STAGED_VERB,
    T_TOKEN,
    T_TOPOFIELD,
    T_UDEP,
    T_UPOS,
)
from py_lift.stage.cas_adapter import cas_view_to_udapi_doc
from py_lift.stage.parser import analyze_single_document

logger = logging.getLogger(__name__)

#: The five coarse developmental stages.
COARSE_STAGES = ("ADV", "SVO", "INV", "SEP", "VEND")

#: Topological fields whose token ordinals are recorded on StagedVerb by default.
DEFAULT_TOPOLOGY_FIELDS = ("VF", "MF", "NF")

#: Views with this prefix are learner-text re-tokenisations we never label.
SPACY_VIEW_PREFIX = "spacy"


@supported_languages("de")
@requires_types(
    T_SENT, T_TOKEN, T_LEMMA, T_POS, T_UPOS, T_TOPOFIELD, T_UDEP, T_STAGE, T_STAGED_VERB
)
class SE_StageAnnotator(SEL_BaseAnnotator):
    """Annotate German finite-verb placement stages on one or more CAS views."""

    def __init__(
        self,
        language: str = "de",
        views: Optional[Sequence[str]] = None,
        *,
        topology_fields: Sequence[str] = DEFAULT_TOPOLOGY_FIELDS,
        origin: str = "rule_based",
        overwrite: bool = False,
        strict: bool = True,
    ):
        super().__init__(language, strict=strict)
        self.views = tuple(views) if views else ("ctok",)
        self.topology_fields = tuple(topology_fields)
        self.origin = origin
        self.overwrite = overwrite
        self.Stage = self.get_type(T_STAGE)
        self.StagedVerb = self.get_type(T_STAGED_VERB)

    # -- entry point ----------------------------------------------------

    def _process(self, cas: Cas) -> bool:
        available = {sofa.sofaID for sofa in cas.sofas}
        added_any = False
        for view_name in self.views:
            if view_name.startswith(SPACY_VIEW_PREFIX):
                logger.warning("Refusing to label spaCy view %r", view_name)
                continue
            if view_name not in available:
                logger.warning("View %r not found in CAS; skipping", view_name)
                continue
            added_any |= self._process_view(cas.get_view(view_name), view_name)
        return added_any

    # -- per view -------------------------------------------------------

    def _process_view(self, view: Cas, view_name: str) -> bool:
        if self.overwrite:
            self._remove_previous(view)

        doc = cas_view_to_udapi_doc(view, view_name)
        clauses = analyze_single_document(doc, view_name)
        logger.info("View %r: %d finite-verb clauses", view_name, len(clauses))

        added = False
        for clause in clauses:
            if self._write_clause(view, clause):
                added = True
        return added

    def _remove_previous(self, view: Cas) -> None:
        for type_name in (T_STAGE, T_STAGED_VERB):
            for fs in list(view.select(type_name)):
                if getattr(fs, "origin", None) == self.origin:
                    view.remove(fs)

    # -- writing one clause --------------------------------------------

    def _write_clause(self, view: Cas, clause: dict) -> bool:
        verb = clause["finite_verb"]
        begin = verb.misc.get("CasBegin")
        end = verb.misc.get("CasEnd")
        if begin is None or end is None:
            logger.warning(
                "Finite verb %r lacks CAS offsets; skipping", clause["finite_verb_form"]
            )
            return False
        begin, end = int(begin), int(end)

        # StagedVerb: one per finite verb.
        gov = clause.get("clausal_governor")
        staged_verb = self.StagedVerb(
            begin=begin,
            end=end,
            clauseType=clause["clause_type"],
            finiteVerbIsSemroot=bool(clause["finite_verb_is_semroot"]),
            separatedVerbPrefix=bool(clause["separated_verb_prefix"]),
            topology=self._topology_string(clause),
            semrootOrd=int(clause["semroot_index"]),
            clausalGovernorOrd=int(gov.ord) if gov is not None else 0,
            origin=self.origin,
        )
        view.add(staged_verb)

        # Stage: one per stage with a non-zero fine label.
        stages = clause["stages"]
        for stage in COARSE_STAGES:
            fine = stages[f"fine_{stage}"]
            if fine.endswith("_zero"):
                continue
            view.add(
                self.Stage(begin=begin, end=end, name=stage, fine=fine, origin=self.origin)
            )
        return True

    def _topology_string(self, clause: dict) -> str:
        """``"VF:1|MF:3,4|NF:9"`` over the configured fields, by token ordinal."""
        topology = clause["topology"]
        parts: List[str] = []
        for field in self.topology_fields:
            nodes = topology.get(field) or []
            if nodes:
                ords = ",".join(str(n.ord) for n in sorted(nodes, key=lambda n: n.ord))
                parts.append(f"{field}:{ords}")
        return "|".join(parts)
