import pytest
from util import load_typesystem
from cassis import Cas
from frequency import SE_WordFrequency
from lift_fixtures import *

def test_frequency(cas_simple):
    SE_WordFrequency("de").process(cas_simple)

    values = [4.51, 5.25, 5.78, 4.74, 5.78, 3.67, 4.65]

    T_TOKEN = 'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token'

    i = 0
    for token in cas_simple.select(T_TOKEN):
        for feature in cas_simple.select_covered("org.lift.type.Frequency", token):
            assert feature.value == values[i]
            i += 1

    assert i == 7
