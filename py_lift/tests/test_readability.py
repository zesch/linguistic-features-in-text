import pytest
from util import load_lift_typesystem
from cassis import Cas
from readability import FE_FleschIndex

def test_readability():
    ts = load_lift_typesystem('data/TypeSystem.xml')
    cas = Cas(typesystem=ts)
    cas.sofa_string = "Das ist ein etwas längerer Satz, es gibt Nebensätze und Kommata, sodass er möglichst lang wird. Ein zweiter Satz ist auch dabei, hurra!"
    FE_FleschIndex().extract(cas)

    i = 0
    for feature in cas.select("org.lift.type.FeatureAnnotationNumeric"):
        assert feature.get('name') == 'Readability_Score_Flesch_Kincaid_Lang_de'
        assert pytest.approx(feature.value, 0.1) == 76.9
        i += 1

    assert i == 1
