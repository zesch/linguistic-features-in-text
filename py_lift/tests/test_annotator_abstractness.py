
import pytest
from util import load_lift_typesystem, construct_cas, assert_annotations
from cassis import Cas
from annotators import SE_AbstractnessAnnotator

def test_abstractness_annotator():
    ts = load_lift_typesystem()
    cas = Cas(typesystem=ts)
    cas.sofa_string = "Demokratie ist eher abstrakt. Leben ist konkret."

    tokens = ["Demokratie", "ist", "eher", "abstrakt", "." "Leben", "ist", "konkret", "."]
    lemmas = ["Demokratie", "sein", "eher", "abstrakt", "." "Leben", "sein", "konkret", "."]
    pos_tags = ["NN", "AUX", "ADV", "ADJ", "PUNCT", "NN", "AUX", "ADJ", "PUNCT"]

    cas = construct_cas(ts, tokens, lemmas, pos_tags)

    SE_AbstractnessAnnotator("de").process(cas)

    # TODO why are double values returned as strings?
    results = [
        ("Demokratie", "4.036"),
        ("ist", "3.731"),
        ("eher", "2.502"),
        ("abstrakt", "3.181"),
        ("ist", "3.731"),
        ("konkret", "2.848")
    ]    
    
    assert_annotations(
        expected=results,
        annotations=cas.select("org.lift.type.AbstractnessConcreteness"),
        key_attr="get_covered_text",
        value_attr="value"
    )


    
