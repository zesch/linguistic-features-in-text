import pytest
from util import load_lift_typesystem
from cassis import Cas, load_cas_from_xmi
from extractors import FE_TokensPerSentence, FEL_AnnotationCounter, FE_EasyWordRatio
from lift_fixtures import *
from dkpro import T_TOKEN, T_POS, T_LEMMA, T_SENT, T_FEATURE
from annotators import SE_EasyWordAnnotator

def test_ratio_extractors():
    ts = load_lift_typesystem('data/TypeSystem.xml')
    cas = Cas(typesystem=ts)
    cas.sofa_string = "This is a test. A small one."

    # TODO can we take more convenient way to test CASes from Cassis?
    T = ts.get_type(T_TOKEN)
    t1 = T(begin=0, end=4)
    t2 = T(begin=5, end=7)
    t3 = T(begin=8, end=9)
    t4 = T(begin=10, end=14)
    t5 = T(begin=14, end=15)
    t6 = T(begin=16, end=17)
    t7 = T(begin=18, end=23)
    t8 = T(begin=24, end=27)
    t9 = T(begin=27, end=28)
    cas.add_all([t1, t2, t3, t4, t5, t6, t7, t8, t9])

    S = ts.get_type(T_SENT)
    s1 = S(begin=0, end=15)
    s2 = S(begin=16, end=27)
    cas.add_all([s1, s2])

    FE_TokensPerSentence().extract(cas)

    i = 0
    for feature in cas.select(T_FEATURE):
        assert feature.get('name') == T_TOKEN + '_PER_' + T_SENT
        assert feature.value == 4.5
        i += 1

    assert i == 1

def test_easy_word_extractor():
    ts = load_lift_typesystem('data/TypeSystem.xml')
    cas = Cas(typesystem=ts)
    cas.sofa_string = "This is a test. A small one."

    T = ts.get_type(T_TOKEN)
    t1 = T(begin=0, end=4)
    t2 = T(begin=5, end=7)
    t3 = T(begin=8, end=9)
    t4 = T(begin=10, end=14)
    t5 = T(begin=14, end=15)
    t6 = T(begin=16, end=17)
    t7 = T(begin=18, end=22)
    t8 = T(begin=23, end=26)
    t9 = T(begin=26, end=27)
    cas.add_all([t1, t2, t3, t4, t5, t6, t7, t8, t9])

    L = ts.get_type(T_LEMMA)
    l1 = L(begin=0, end=4, value="this")
    l2 = L(begin=5, end=7, value="be")
    l3 = L(begin=8, end=9, value="a")
    l4 = L(begin=10, end=14, value="test")
    l5 = L(begin=14, end=15, value=".")
    l6 = L(begin=16, end=17, value="a")
    l7 = L(begin=18, end=22, value="small")
    l8 = L(begin=23, end=26, value="one")
    l9 = L(begin=26, end=27, value=".")
    cas.add_all([l1, l2, l3, l4, l5, l6, l7, l8, l9])

    S = ts.get_type(T_SENT)
    s1 = S(begin=0, end=15)
    s2 = S(begin=16, end=27)
    cas.add_all([s1, s2])
    SE_EasyWordAnnotator("en").process(cas)
    FE_EasyWordRatio().extract(cas)

    i = 0
    for feature in cas.select(T_FEATURE):
        assert feature.get('name') == 'EasyWord_PER_Token'
        assert feature.value == 7/9
        i += 1

    assert i == 1

def test_count_extractor():
    ts = load_lift_typesystem('data/TypeSystem.xml')
    cas = Cas(typesystem=ts)
    cas.sofa_string = "test is a test. a small one."

    # TODO can we take more convenient way to test CASes from Cassis?
    T = ts.get_type(T_TOKEN)
    t1 = T(begin=0, end=4)
    t2 = T(begin=5, end=7)
    t3 = T(begin=8, end=9)
    t4 = T(begin=10, end=14)
    t5 = T(begin=14, end=15)
    t6 = T(begin=16, end=17)
    t7 = T(begin=18, end=23)
    t8 = T(begin=24, end=27)
    t9 = T(begin=27, end=28)
    cas.add_all([t1, t2, t3, t4, t5, t6, t7, t8, t9])

    counter = FEL_AnnotationCounter(T_TOKEN)
    counter.extract(cas)

    counter_unique = FEL_AnnotationCounter(T_TOKEN, unique=True)
    counter_unique.extract(cas)
    
    i = 0
    for feature in cas.select(T_FEATURE):
        if feature.get('name') == 'COUNT_UNIQUE_' + T_TOKEN:
            assert feature.value == 6
        elif feature.get('name') == 'COUNT_' + T_TOKEN:
            assert feature.value == 9
        i += 1

    assert i == 2

def test_count_extractor_feature_path():
    ts = load_lift_typesystem('data/TypeSystem.xml')
    with open('data/hagen.txt.xmi', 'rb') as f:
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
    
    ts = load_lift_typesystem('data/TypeSystem.xml')
    with open('data/hagen.txt.xmi', 'rb') as f:
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