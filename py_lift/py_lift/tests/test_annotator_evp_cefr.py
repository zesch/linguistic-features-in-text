import pytest
from py_lift.util import load_lift_typesystem, construct_cas
from py_lift.annotators.misc import SE_EvpCefrAnnotator
from py_lift.dkpro import T_FEATURE

def test_evp_cefr_annotator():
    ts = load_lift_typesystem()
    
    cas = construct_cas(
        ts, 
        " ".split("This is a test . A minimal metaphor . Fake . Fake ."),
        " ".split("this be a test . a minimal metaphor . Fake . Fake ."),
        ["NN VB DT NN . DT JJ NN . JJ . NN ."]
    )
    
    SE_EvpCefrAnnotator("en").process(cas)

    words = ["This", "is", "a", "test", "A", "minimal", "metaphor", "Fake", "Fake"]
    labels_cefr = [1, 1, 1, 1, 1, 5, 6, 5, 6]

    words_with_level = {word: level for word, level in zip(words, labels_cefr)}

    for feature in cas.select(T_FEATURE):
        if feature.get_covered_text() in words:
            assert feature.level == words_with_level[feature.get_covered_text()]
        else:
            pytest.fail('Unexpected token: ' + feature.get_covered_text())
