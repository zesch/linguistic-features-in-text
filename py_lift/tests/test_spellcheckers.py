import pytest
from annotators import SE_SpellErrorAnnotator
from lift_fixtures import *

T_ANOMALY = 'de.tudarmstadt.ukp.dkpro.core.api.anomaly.type.SpellingAnomaly'

def test_extractors(cas_simple):
    SE_SpellErrorAnnotator("en").process(cas_simple)
    for anomaly in cas_simple.select(T_ANOMALY):
        t_str = anomaly.get_covered_text()
        assert t_str in ["tast", "smoll"]
        suggestions = anomaly.get('suggestions')
        for element in suggestions.get('elements'):
            replacement = element.get('replacement')
            if t_str == 'tast':
                assert replacement == 'last'
            elif t_str == 'smoll':
                assert replacement == 'small'

def test_unknown_language(cas_simple):
    with pytest.raises(ValueError) as e_info:
        SE_SpellErrorAnnotator("xy").process(cas_simple)
