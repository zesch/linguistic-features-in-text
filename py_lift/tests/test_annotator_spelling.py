
import pytest
from preprocessing import Spacy_Preprocessor
from annotators import SE_SpellErrorAnnotator
from dkpro import T_ANOMALY

def test_spelling_annotator():
    text = "Das iste einex Biespeil fürr Texxt mit viehle Feler."
    spacy = Spacy_Preprocessor(language='de')
    cas = spacy.run(text)
    SE_SpellErrorAnnotator("de").process(cas)

    for anomaly in cas.select(T_ANOMALY):
        print(f"Anomaly: {anomaly.get_covered_text()}")
        for suggestion in anomaly.suggestions.elements:
            print(f"  Suggestion: {suggestion}")

    assert len(cas.select(T_ANOMALY)) == 7