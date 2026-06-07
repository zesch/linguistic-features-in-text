"""Shared fixture builder for the stage-annotation tests.

Builds a CAS with a single German sentence on a ``ctok`` view, carrying the
layers the stage pipeline consumes (Token, Lemma, UD-POS, STTS-POS,
UDependency, topological field). The sentence is a canonical V2 declarative,
``"Das Kind sieht den Hund ."`` (subject in VF, finite verb in LK, object in
MF), which the rule engine classifies as SVO.

Built programmatically (not via the spaCy preprocessor) because the dakoda
layers — UDependency and topological fields — are not produced by spaCy.
"""
import cassis

from py_lift.dkpro import (
    T_LEMMA,
    T_POS,
    T_SENT,
    T_TOKEN,
    T_TOPOFIELD,
    T_UDEP,
    T_UPOS,
)
from py_lift.util import load_lift_typesystem

SENTENCE = "Das Kind sieht den Hund ."

# form, begin, end, STTS, UD-POS, lemma, deprel, governor ordinal (1-based)
_ROWS = [
    ("Das",    0,  3, "ART",   "DET",   "d",     "det",   2),
    ("Kind",   4,  8, "NN",    "NOUN",  "Kind",  "nsubj", 3),
    ("sieht",  9, 14, "VVFIN", "VERB",  "sehen", "root",  3),
    ("den",   15, 18, "ART",   "DET",   "d",     "det",   5),
    ("Hund",  19, 23, "NN",    "NOUN",  "Hund",  "obj",   3),
    (".",     24, 25, "$.",    "PUNCT", ".",     "punct", 3),
]
_TOPO = ["VF", "VF", "LK", "MF", "MF", "null"]


def build_german_ctok_cas(view_name: str = "ctok") -> cassis.Cas:
    """Return a CAS whose ``view_name`` view holds the annotated sentence."""
    ts = load_lift_typesystem()
    cas = cassis.Cas(typesystem=ts)
    cas.sofa_string = SENTENCE  # default view, harmless
    view = cas.create_view(view_name)
    view.sofa_string = SENTENCE

    Token = ts.get_type(T_TOKEN)
    Lemma = ts.get_type(T_LEMMA)
    Stts = ts.get_type(T_POS)
    Upos = ts.get_type(T_UPOS)
    Sentence = ts.get_type(T_SENT)
    Topo = ts.get_type(T_TOPOFIELD)
    UDep = ts.get_type(T_UDEP)

    view.add(Sentence(begin=0, end=len(SENTENCE)))

    tokens = []
    for i, (form, b, e, stts, upos, lemma, deprel, _gov) in enumerate(_ROWS, start=1):
        tok = Token(begin=b, end=e, id=str(i), syntacticFunction=deprel)
        view.add(tok)
        tokens.append(tok)
        view.add(Lemma(begin=b, end=e, value=lemma))
        view.add(Stts(begin=b, end=e, PosValue=stts))
        view.add(Upos(begin=b, end=e, PosValue=upos))
        view.add(Topo(begin=b, end=e, FieldValue=_TOPO[i - 1]))

    for i, (form, b, e, stts, upos, lemma, deprel, gov) in enumerate(_ROWS):
        view.add(
            UDep(
                begin=b,
                end=e,
                Governor=tokens[gov - 1],
                Dependent=tokens[i],
                DependencyType=deprel,
                flavor="basic",
            )
        )

    return cas
