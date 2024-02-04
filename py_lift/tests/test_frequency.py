import pytest
from util import load_typesystem
from cassis import Cas
from frequency import SE_WordFrequency
from lift_fixtures import *

def test_frequency(cas_en_simple):
    SE_WordFrequency("en").process(cas_en_simple)

    values = [6.82, 7.07, 7.36, 5.19, 7.36, 5.51, 6.47]

    T_TOKEN = 'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token'

    i = 0
    for token in cas_en_simple.select(T_TOKEN):
        for feature in cas_en_simple.select_covered("org.lift.type.Frequency", token):
            assert feature.value == values[i]
            i += 1

    assert i == 7