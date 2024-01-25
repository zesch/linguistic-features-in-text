

import pytest
from util import load_typesystem as lt
from cassis import *
from extractors import SE_SpellErrorAnnotator

T_TOKEN = 'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token'
T_SENTENCE = 'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence'
T_ANNOTATION = 'de.tudarmstadt.ukp.dkpro.core.api.anomaly.type.SpellingAnomaly'
S_SUGGESTION = 'de.tudarmstadt.ukp.dkpro.core.api.anomaly.type.SuggestedAction'

def test_extractors():
    ts = lt('data/TypeSystem.xml')
    cas = Cas(typesystem=ts)
    cas.sofa_string = "This is a tast. A smoll one."

    # TODO can we take more convenient way to test CASes from Cassis?
    T = ts.get_type(T_TOKEN)
    t1 = T(begin=0, end=4)
    t2 = T(begin=5, end=7)
    t3 = T(begin=8, end=9)
    t4 = T(begin=10, end=14)
    t5 = T(begin=16, end=17)
    t6 = T(begin=18, end=23)
    t7 = T(begin=24, end=27)
    cas.add_all([t1, t2, t3, t4, t5, t6, t7])

    S = ts.get_type(T_SENTENCE)
    s1 = S(begin=0, end=15)
    s2 = S(begin=16, end=27)
    cas.add_all([s1, s2])

    SE_SpellErrorAnnotator().process(cas)
    for tok in cas.select(T_ANNOTATION):
        assert tok.get_covered_text() in ["tast", "smoll"]
    for tok in cas.select(S_SUGGESTION):
        assert tok.replacement in ["last", "small"]                



