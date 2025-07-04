import pytest
from annotators import SE_SpellErrorAnnotator
from extractors import FEL_AnnotationCounter
from readability import FE_FleschIndex
from lift_fixtures import *
from util import df_features

def test_extractors(cas_en_simple_with_errors):
    SE_SpellErrorAnnotator("en").process(cas_en_simple_with_errors)
    FE_FleschIndex().extract(cas_en_simple_with_errors)
    FEL_AnnotationCounter('SpellingAnomaly').extract(cas_en_simple_with_errors)

    df = df_features(cas_en_simple_with_errors)
    print(df)
    assert df.shape == (2, 2)
