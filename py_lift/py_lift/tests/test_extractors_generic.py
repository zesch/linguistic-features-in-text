import pytest
from util import load_lift_typesystem
from cassis import load_cas_from_xmi
from extractors import FE_TokensPerSentence, FEL_AnnotationCounter
from lift_fixtures import *
from dkpro import T_TOKEN, T_POS, T_LEMMA, T_FEATURE

def test_ratio_extractors(cas_en_simple):

    FE_TokensPerSentence().extract(cas_en_simple)

    i = 0
    for feature in cas_en_simple.select(T_FEATURE):
        assert feature.get('name') == 'Token_PER_Sentence'
        assert feature.value == 4.5
        i += 1

    assert i == 1

def test_count_extractor(cas_en_simple):
    FEL_AnnotationCounter(T_TOKEN).extract(cas_en_simple)
    FEL_AnnotationCounter(T_TOKEN, unique=True).extract(cas_en_simple)
    
    i = 0
    for feature in cas_en_simple.select(T_FEATURE):
        if feature.get('name') == 'COUNT_UNIQUE_Token':
            assert feature.value == 6
        elif feature.get('name') == 'COUNT_Token':
            assert feature.value == 9
        i += 1

    assert i == 2

def test_count_extractor_feature_path():
    ts = load_lift_typesystem()
    with open('py_lift/data/hagen.txt.xmi', 'rb') as f:
        cas = load_cas_from_xmi(f, ts)

    counter_unique = FEL_AnnotationCounter(
        T_POS, 
        unique=True, 
        feature_path='PosValue', 
        allowed_feature_values=['NN','ADV']
    )
    counter_unique.extract(cas)
    
    for feature in cas.select(T_FEATURE):
        if feature.get('name') == T_POS + 'COUNT_UNIQUE_PosValue_NN_ADV':
            assert feature.value == 33

def test_count_extractor_custom_to_string():
    def _lemma_to_string(anno):
        return anno.get('value')
    
    ts = load_lift_typesystem()
    with open('py_lift/data/hagen.txt.xmi', 'rb') as f:
        cas = load_cas_from_xmi(f, ts)

    counter_unique = FEL_AnnotationCounter(
        T_LEMMA, 
        unique=True, 
        custom_to_string=_lemma_to_string
    )

    counter_unique.extract(cas)
    
    for feature in cas.select(T_FEATURE):
        if feature.get('name') == T_LEMMA + '_COUNT_UNIQUE':
            assert feature.value == 101