import pytest
from util import load_typesystem
from cassis import Cas
from extractors import FE_TokensPerSentence, FE_EasyWordRatio
from annotators import SE_EasyWordAnnotator

T_TOKEN = 'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token'
T_SENTENCE = 'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence'
T_FEATURE = 'org.lift.type.FeatureAnnotationNumeric'
T_EASYWORD = 'org.lift.type.EasyWord'
T_LEMMA = 'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Lemma'

def test_extractors():
    ts = load_typesystem('data/TypeSystem.xml')
    cas = Cas(typesystem=ts)
    cas.sofa_string = "This is a test. A small one."

    # TODO can we take more convenient way to test CASes from Cassis?
    T = ts.get_type(T_TOKEN)
    t1 = T(begin=0, end=4)
    t2 = T(begin=5, end=7)
    t3 = T(begin=8, end=9)
    t4 = T(begin=10, end=14)
    t5 = T(begin=14, end=5)
    t6 = T(begin=16, end=17)
    t7 = T(begin=18, end=22)
    t8 = T(begin=23, end=26)
    t9 = T(begin=26, end=27)
    cas.add_all([t1, t2, t3, t4, t5, t6, t7, t8, t9])

    S = ts.get_type(T_SENTENCE)
    s1 = S(begin=0, end=15)
    s2 = S(begin=16, end=27)
    cas.add_all([s1, s2])

    FE_TokensPerSentence().extract(cas)

    i = 0
    for feature in cas.select(T_FEATURE):
        assert feature.name == T_TOKEN + '_PER_' + T_SENTENCE
        assert feature.value == 4.5
        i += 1

    assert i == 1

def test_easy_word_extractor():
    ts = load_typesystem('data/TypeSystem.xml')
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

    S = ts.get_type(T_SENTENCE)
    s1 = S(begin=0, end=15)
    s2 = S(begin=16, end=27)
    cas.add_all([s1, s2])
    SE_EasyWordAnnotator("en").process(cas)
    FE_EasyWordRatio().extract(cas)

    i = 0
    for feature in cas.select(T_FEATURE):
        assert feature.name == T_EASYWORD + '_PER_' + T_TOKEN
        assert feature.value == 7/9
        i += 1

    assert i == 1







    
