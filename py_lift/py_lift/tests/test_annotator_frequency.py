import pytest
from py_lift.annotators.frequency import SE_TokenZipfFrequency
from py_lift.dkpro import T_TOKEN
from py_lift.tests.lift_fixtures import *

def test_frequency(cas_en_simple):
    SE_TokenZipfFrequency("en").process(cas_en_simple)

    values = [6.82, 7.07, 7.36, 5.19, 0.0, 7.36, 5.51, 6.47, 0.0]

    i = 0
    for token in cas_en_simple.select(T_TOKEN):
        print(token.get_covered_text())
        for feature in cas_en_simple.select_covered("org.lift.type.Frequency", token):
            assert feature.value == values[i]
            i += 1

    assert i == 9