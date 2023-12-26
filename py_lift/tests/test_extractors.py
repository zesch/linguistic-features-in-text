import pytest
from util import load_typesystem
from cassis import Cas
from extractors import FE_TokensPerSentence

T_TOKEN = 'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token'
T_SENTENCE = 'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence'
T_FEATURE = 'org.lift.type.FeatureAnnotationNumeric'

def test_extractors():
    ts = load_typesystem('data/TypeSystem.xml')
    cas = Cas(typesystem=ts)
    cas.sofa_string = "This is a test."

    T = ts.get_type(T_TOKEN)
    t1 = T(begin=0, end=4)
    t2 = T(begin=5, end=7)
    t3 = T(begin=8, end=9)
    t4 = T(begin=10, end=14)
    t5 = T(begin=14, end=14)
    cas.add_all([t1, t2, t3, t4, t5])

    S = ts.get_type(T_SENTENCE)
    s1 = S(begin=0, end=15)
    cas.add_all([s1])

    FE_TokensPerSentence().extract(cas)

    i = 0
    for feature in cas.select(T_FEATURE):
        assert feature.name == T_TOKEN + '_PER_' + T_SENTENCE
        assert feature.value == 5.0
        i += 1

    assert i == 1