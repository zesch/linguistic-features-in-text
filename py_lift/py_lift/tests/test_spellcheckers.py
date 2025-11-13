import pytest
from annotators.misc import SE_SpellErrorAnnotator
from dkpro import T_ANOMALY
from lift_fixtures import *

def test_extractors(cas_en_simple_with_errors):
    SE_SpellErrorAnnotator("en").process(cas_en_simple_with_errors)
    for anomaly in cas_en_simple_with_errors.select(T_ANOMALY):
        t_str = anomaly.get_covered_text()
        assert t_str in ["tast", "smoll"]
        suggestions = anomaly.get('suggestions')
        for element in suggestions.get('elements'):
            replacement = element.get('replacement')
            if t_str == 'tast':
                assert replacement == 'last'
            elif t_str == 'smoll':
                assert replacement == 'small'

def test_unknown_language(cas_en_simple):
    with pytest.raises(ValueError) as e_info:
        SE_SpellErrorAnnotator("xy").process(cas_en_simple)
