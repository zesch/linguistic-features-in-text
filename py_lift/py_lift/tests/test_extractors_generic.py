import pytest
from py_lift.util import load_lift_typesystem, construct_cas
from cassis import load_cas_from_xmi
from py_lift.extractors import FE_TokensPerSentence, FEL_AnnotationCounter, FEL_Length, FEL_FeatureValueCounter
from py_lift.tests.lift_fixtures import *
from py_lift.dkpro import T_TOKEN, T_POS, T_LEMMA, T_FEATURE

def test_length_extractors(cas_en_simple):

    FEL_Length(T_TOKEN).extract(cas_en_simple)

    i = 0
    for feature in cas_en_simple.select(T_FEATURE):
        if feature.get('name') == 'TOKEN_length_mean':
            assert feature.value == 3.5
        elif feature.get('name') == 'TOKEN_length_min':
            assert feature.value == 2
        elif feature.get('name') == 'TOKEN_length_max':
            assert feature.value == 6
        i += 1

    assert i == 3

def test_ratio_extractor(cas_en_simple):

    FE_TokensPerSentence().extract(cas_en_simple)

    i = 0
    for feature in cas_en_simple.select(T_FEATURE):
        assert feature.get('name') == 'Token_COUNT_PER_Sentence_COUNT'
        assert feature.value == 4.5
        i += 1

    assert i == 1

def test_ratio_exception(cas_no_annotations):

    extractor = FE_TokensPerSentence()
    extractor.strict = True  
    with pytest.raises(ZeroDivisionError):
        extractor.extract(cas_no_annotations)

    extractor.strict = False
    extractor.extract(cas_no_annotations)
    
    i = 0
    for feature in cas_no_annotations.select(T_FEATURE):
        assert feature.get('name') == 'Token_COUNT_PER_Sentence_COUNT'
        assert feature.value == 0
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

def test_count_extractor_custom_to_string():
    def _lemma_to_string(anno):
        return anno.get('value')

    lemma_counter = FEL_AnnotationCounter(
        T_LEMMA
    )

    lemma_counter_unique = FEL_AnnotationCounter(
        T_LEMMA, 
        unique=True, 
        custom_to_string=_lemma_to_string
    )

    ts = load_lift_typesystem()
    tokens = ["is", "test", "tests", "simple", "simpler", "simplest"]
    lemmas = ["be", "test", "test", "simple", "simple", "simple"]
    pos = ["V", "N", "N", "A", "A", "A"]
    cas = construct_cas(ts, tokens, lemmas, pos)

    lemma_counter.extract(cas)
    lemma_counter_unique.extract(cas)
    
    for feature in cas.select(T_FEATURE):
        if feature.get('name') == T_LEMMA + '_COUNT_UNIQUE':
            assert feature.value == 3
        elif feature.get('name') == T_LEMMA + '_COUNT':
            assert feature.value == 6

def test_count_extractor_feature_path():
    ts = load_lift_typesystem()
    with open('py_lift/data/hagen.txt.xmi', 'rb') as f:
        cas = load_cas_from_xmi(f, ts)

    counter_NN = FEL_FeatureValueCounter(
        T_POS, 
        feature_path='PosValue', 
        feature_values=['NN']
    )

    counter_NN_ADV = FEL_FeatureValueCounter(
        T_POS, 
        feature_path='PosValue', 
        feature_values=['NN','ADV']
    )
    counter_NN.extract(cas)
    counter_NN_ADV.extract(cas)

    for feature in cas.select(T_FEATURE):
        if feature.get('name') == T_POS + '_FEATURECOUNT_PosValue_NN_ADV':
            assert feature.value == 37
        elif feature.get('name') == T_POS + '_FEATURECOUNT_PosValue_NN':
            assert feature.value == 35

