
import pytest
from cassis.typesystem import TypeNotFoundError
from py_lift.preprocessing import Spacy_Preprocessor
from py_lift.annotators.misc import SE_SpellErrorAnnotator, SE_RWSE_Annotator
from py_lift.dkpro import T_ANOMALY, T_RWSE
from py_lift.tests.lift_fixtures import *
from py_lift.util import construct_cas

def test_spelling_annotator_de():
    text = "Das iste einex Biespeil fürr Texxt mit viehle Feler."
    spacy = Spacy_Preprocessor(language='de')
    cas = spacy.run(text)
    SE_SpellErrorAnnotator("de").process(cas)

    for anomaly in cas.select(T_ANOMALY):
        print(f"Anomaly: {anomaly.get_covered_text()}")
        for suggestion in anomaly.suggestions.elements:
            print(f"  Suggestion: {suggestion}")

    # the example has more errors, but the current implementation only detects 4
    assert len(cas.select(T_ANOMALY)) == 4

def test_spelling_annotator_en(cas_en_simple_with_errors):
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

def test_spelling_annotator_unknown_language(cas_en_simple):
    with pytest.raises(ValueError):
        SE_SpellErrorAnnotator("xy").process(cas_en_simple)

def test_rwse():
    ts = load_lift_typesystem()
    cas = Cas(typesystem=ts)
    cas.sofa_string = "Ich bin ein Besenstiel und sehe glut aus."

    tokens = ["Ich", "bin", "ein", "Besenstiel", "und", "sehe", "glut", "aus", "."]
    lemmas = ["Ich", "sein", "ein", "Besenstiel", "und", "sehen", "glut", "aus", "."]
    pos_tags = ["PPER", "VAFIN", "ART", "NN", "KON", "VVFIN", "ADJD", "PTKVZ", "$."]

    cas = construct_cas(ts, tokens, lemmas, pos_tags)
    
    S = ts.get_type(T_SENT)
    cas.add(S(begin=0, end=len(cas.sofa_string)))

    confusion_sets = [["Beispiel","Besenstiel"],["gut","glut"]]
    SE_RWSE_Annotator(model_name="bert-base-multilingual-uncased", confusion_sets=confusion_sets).process(cas)

    try:
        ts.get_type(T_RWSE)
    except TypeNotFoundError:
        print("RWSE type not found. Creating...")
        ts.create_type(T_RWSE)
        
    assert len(cas.select(T_RWSE)) == 2