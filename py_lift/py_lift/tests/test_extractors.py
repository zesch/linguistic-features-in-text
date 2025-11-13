import pytest
from util import load_lift_typesystem, construct_cas
from cassis import load_cas_from_xmi
from extractors import FE_EasyWordRatio, FE_AbstractnessStats
from lift_fixtures import *
from dkpro import T_FEATURE
from annotators.lists import SE_EasyWordAnnotator
from annotators.misc import SE_AbstractnessAnnotator

def test_abstractness_extractor():
    ts = load_lift_typesystem()
    gold_tokens = ["Demokratie", "ist", "eher", "abstrakt", ".", "Leben", "ist", "konkret", "."]
    gold_lemmas = ["Demokratie", "sein", "eher", "abstrakt", ".", "Leben", "sein", "konkret", "."]
    gold_pos = ["NN", "VAFIN", "ADV", "ADJD", "$.", "NN", "VAFIN", "ADJD", "$."]    
    cas = construct_cas(ts, gold_tokens, gold_lemmas, gold_pos)
    
    SE_AbstractnessAnnotator("de").process(cas)
    FE_AbstractnessStats().extract(cas)

    i = 0
    for feature in cas.select(T_FEATURE):
        print(feature)
        if feature.get('name') == 'org.lift.type.AbstractnessConcreteness_mean':
            assert pytest.approx(feature.value) == 3.3868571428571426
            i += 1
        elif feature.get('name') == 'org.lift.type.AbstractnessConcreteness_min':
            assert pytest.approx(feature.value) == 2.502
            i += 1
        elif feature.get('name') == 'org.lift.type.AbstractnessConcreteness_max':
            assert pytest.approx(feature.value) == 4.036
            i += 1
        else :
            pytest.fail('Unexpected feature: ' + str(feature.get('name')))

    assert i == 3

def test_easy_word_extractor(cas_en_simple):
    SE_EasyWordAnnotator("en").process(cas_en_simple)
    FE_EasyWordRatio().extract(cas_en_simple)

    i = 0
    for feature in cas_en_simple.select(T_FEATURE):
        assert feature.get('name') == 'EasyWord_PER_Token'
        assert feature.value == 7/9
        i += 1

    assert i == 1