import pytest
from lift_fixtures import *
from util import load_lift_typesystem
from cassis import Cas
from readability import *

def test_readability():
    ts = load_lift_typesystem()
    cas = Cas(typesystem=ts)
    cas.sofa_string = "Das ist ein etwas längerer Satz, es gibt Nebensätze und Kommata, sodass er möglichst lang wird. Ein zweiter Satz ist auch dabei, hurra!"
    FE_TextstatFleschIndex('de').extract(cas)

    i = 0
    for feature in cas.select("org.lift.type.FeatureAnnotationNumeric"):
        assert feature.get('name') == 'Readability_Score_FleschKincaid_de'
        assert pytest.approx(feature.value, 0.1) == 76.9
        i += 1

    assert i == 1

def test_textstat(cas_en_simple):
    FE_TextstatAutomatedReadabilityIndex('en').extract(cas_en_simple)
    FE_TextstatColemanLiauIndex('en').extract(cas_en_simple)
    FE_TextstatCrawford('es').extract(cas_en_simple)
    FE_TextstatDaleChallReadabilityScore('en').extract(cas_en_simple)
    FE_TextstatFernandezHuerta('es').extract(cas_en_simple)
    FE_TextstatFleschIndex('en').extract(cas_en_simple)
    FE_TextstatFleschKincaidGrade('en').extract(cas_en_simple)
    FE_TextstatGulpeaseIndex('it').extract(cas_en_simple)
    FE_TextstatGunningFog('en').extract(cas_en_simple)
    FE_TextstatGutierrezPolini('es').extract(cas_en_simple)
    FE_TextstatLinsearWriteFormula('en').extract(cas_en_simple)
    FE_TextstatMcAlpineEFLAW('en').extract(cas_en_simple)
    FE_TextstatOsman('ar').extract(cas_en_simple)
    FE_TextstatSmogIndex('en').extract(cas_en_simple)
    FE_TextstatSpacheReadability('en').extract(cas_en_simple)
    FE_TextstatSzigrisztPazos('es').extract(cas_en_simple)
    FE_TextstatWienerSachtextformel_1('de').extract(cas_en_simple)

def test_unsupported_language_extractor(): 
    with pytest.raises(ValueError) as excinfo:
        FE_TextstatFleschIndex("jp")
    
    assert "jp is not a supported language." in str(excinfo.value)