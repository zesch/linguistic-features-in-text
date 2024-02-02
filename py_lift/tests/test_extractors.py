import pytest
from util import load_typesystem
from cassis import Cas
from extractors import FE_TokensPerSentence, FE_FleschIndex

T_TOKEN = 'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token'
T_SENTENCE = 'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence'
T_FEATURE = 'org.lift.type.FeatureAnnotationNumeric'

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
    t5 = T(begin=14, end=14)
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

#def test_readability():
#    ts = load_typesystem('data/TypeSystem.xml')
#    cas = load_cas_from_xmi('data/testcas.xmi', typesystem=ts)
    
#    #FE_FleschIndex().extract(cas, 'learner')
#    FE_FleschIndex().extract(cas, 'TH1')

#    i = 0
#    for feature in cas.select(T_FEATURE):
#        assert feature.name == 'Readability_Score_Flesch_Kincaid_Lang_de'
#        assert feature.value == 61.7
#        i += 1

#    assert i == 1





    
