
import pytest
from util import load_lift_typesystem, construct_cas, assert_annotations
from lift_fixtures import *
from cassis import Cas
from annotators.lists import SE_FiniteVerbAnnotator, SE_EasyWordAnnotator

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
    
def test_easy_words_annotator(cas_en_simple):

    SE_EasyWordAnnotator("en").process(cas_en_simple)

    assert len(cas_en_simple.select("org.lift.type.EasyWord")) == 2

def test_easy_words_annotator_unsupported_language():
    with pytest.raises(ValueError) as excinfo:
        SE_EasyWordAnnotator("de")
    
    assert "de is not a supported language." in str(excinfo.value)