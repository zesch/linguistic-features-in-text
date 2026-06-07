import pytest
from py_lift.annotators.misc import SE_SpellErrorAnnotator
from py_lift.extractors import FEL_AnnotationCounter, FEL_AnnotationRatio
from py_lift.readability import FE_TextstatFleschIndex
from py_lift.tests.lift_fixtures import *
from py_lift.util import df_features, get_all_subclasses, detect_language

def test_extractors(cas_en_simple_with_errors):
    SE_SpellErrorAnnotator('en').process(cas_en_simple_with_errors)
    FE_TextstatFleschIndex('en').extract(cas_en_simple_with_errors)
    FEL_AnnotationCounter('SpellingAnomaly').extract(cas_en_simple_with_errors)

    df = df_features(cas_en_simple_with_errors)
    print(df)
    assert df.shape == (2, 2)

def test_subclass_finding():
    import py_lift.extractors
    assert len(get_all_subclasses(py_lift.extractors, FEL_AnnotationCounter)) == 1
    assert len(get_all_subclasses(py_lift.extractors, FEL_AnnotationRatio)) == 3

def test_language_detection():
    assert detect_language("Parlez-vous français?") == "fr"
    assert detect_language("Ich spreche Französisch nur ein bisschen.") == "de"
    assert detect_language("A little bit is better than nothing.") == "en"