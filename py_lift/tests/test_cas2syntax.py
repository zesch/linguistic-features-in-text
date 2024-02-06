import pytest
import sys
from util import load_typesystem
from cassis import Cas, load_cas_from_xmi
from syntax import FE_CasToTree #FE_TokensPerSentence
import udapi

T_TOKEN = 'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token'
T_SENTENCE = 'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence'
T_FEATURE = 'org.lift.type.FeatureAnnotationNumeric'

# def test_extractors():
#     ts = load_typesystem('data/TypeSystem.xml')
#     cas = Cas(typesystem=ts)
#     cas.sofa_string = "This is a test. A small one."

#     # TODO can we take more convenient way to test CASes from Cassis?
#     T = ts.get_type(T_TOKEN)
#     t1 = T(begin=0, end=4)
#     t2 = T(begin=5, end=7)
#     t3 = T(begin=8, end=9)
#     t4 = T(begin=10, end=14)
#     t5 = T(begin=14, end=14)
#     t6 = T(begin=16, end=17)
#     t7 = T(begin=18, end=22)
#     t8 = T(begin=23, end=26)
#     t9 = T(begin=26, end=27)
#     cas.add_all([t1, t2, t3, t4, t5, t6, t7, t8, t9])

#     S = ts.get_type(T_SENTENCE)
#     s1 = S(begin=0, end=15)
#     s2 = S(begin=16, end=27)
#     cas.add_all([s1, s2])

#     FE_TokensPerSentence().extract(cas)

#     i = 0
#     for feature in cas.select(T_FEATURE):
#         assert feature.name == T_TOKEN + '_PER_' + T_SENTENCE
#         assert feature.value == 4.5
#         i += 1

#     assert i == 1

# test_extractors()
ts = load_typesystem('data/TypeSystem.xml')


infile = "data/1023_0001416.xmi"
# infile = "data/1091_0000266.xmi"
# infile = "data/1023_0001416.xmi"
myview = "_InitialView" # learner layer
with open(infile, 'rb') as f:
    cas = load_cas_from_xmi(f, typesystem=ts)
    fe2cas= FE_CasToTree(myview,ts)
    fe2cas.extract(cas)
