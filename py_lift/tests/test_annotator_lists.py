
import pytest
from util import load_lift_typesystem, construct_cas, assert_annotations
from cassis import Cas
from annotators.lists import SE_FiniteVerbAnnotator

def test_finite_verbs_annotator():
    ts = load_lift_typesystem()
    cas = Cas(typesystem=ts)
    cas.sofa_string = "Ich bin ein Beispiel und sehe gut aus."

    tokens = ["Ich", "bin", "ein", "Beispiel", "und", "sehe", "gut", "aus", "."]
    lemmas = ["Ich", "sein", "ein", "Beispiel", "und", "sehen", "gut", "aus", "."]
    # TODO correct POS tags
    pos_tags = ["NN", "VAFIN", "DET", "NN", "CC", "VVFIN", "ADJ", "PTK", "PUNCT"]

    cas = construct_cas(ts, tokens, lemmas, pos_tags)

    SE_FiniteVerbAnnotator("de").process(cas)

    assert len(cas.select("org.lift.type.Structure")) == 2
    results = [
        ("bin", "FiniteVerb"),
        ("sehe", "FiniteVerb")
    ]     
    assert_annotations(
        expected=results,
        annotations=cas.select("org.lift.type.Structure"),
        key_attr="get_covered_text",
        value_attr="name"
    )
    