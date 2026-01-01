
import pytest
from pathlib import Path
from py_lift.annotators.api import UnsupportedLanguageError
from py_lift.preprocessing import Spacy_Preprocessor
from py_lift.util import load_lift_typesystem
from py_lift.tests.util import construct_cas, assert_annotations
from py_lift.tests.lift_fixtures import *
from cassis import Cas
from py_lift.annotators.lists import SE_FiniteVerbAnnotator, SE_EasyWordAnnotator, SEL_ListReader, SE_OOV_Annotator

def test_finite_verbs_annotator():
    ts = load_lift_typesystem()
    cas = Cas(typesystem=ts)
    cas.sofa_string = "Ich bin ein Beispiel und sehe gut aus."

    tokens = ["Ich", "bin", "ein", "Beispiel", "und", "sehe", "gut", "aus", "."]
    lemmas = ["Ich", "sein", "ein", "Beispiel", "und", "sehen", "gut", "aus", "."]
    pos_tags = ["PPER", "VAFIN", "ART", "NN", "KON", "VVFIN", "ADJD", "PTKVZ", "$."]

    cas = construct_cas(ts, tokens, lemmas, pos_tags)

    SE_FiniteVerbAnnotator("de").process(cas)

    assert len(cas.select("org.lift.type.Structure")) == 2
    results = [
        ("bin", "FiniteVerb"),
        ("sehe", "FiniteVerb")
    ]     
    assert_annotations(
        expected=results,
        annotations=cas.select("org.lift.type.Structure"),
        key_attr="get_covered_text",
        value_attr="name"
    )
    
def test_easy_words_annotator(cas_en_simple):

    SE_EasyWordAnnotator("en").process(cas_en_simple)

    assert len(cas_en_simple.select("org.lift.type.EasyWord")) == 7

def test_easy_words_annotator_unsupported_language():
    with pytest.raises(UnsupportedLanguageError) as excinfo:
        SE_EasyWordAnnotator("de")
    
    assert " language 'de' is not supported" in str(excinfo.value)

def test_list_reader():
    dict_txt = Path(__file__).parent / "data" / "dict_de.txt"
    dict_zip = Path(__file__).parent / "data" / "dict_de.zip"
    dict_gz = Path(__file__).parent / "data" / "dict_de.gz"

    reader_txt = SEL_ListReader(dict_txt)
    reader_zip = SEL_ListReader(dict_zip)
    reader_gz = SEL_ListReader(dict_gz)

    assert reader_txt.read_list() == {'Test', 'ist', 'ein', 'Das'}
    assert reader_zip.read_list() == {'Test', 'ist', 'ein', 'Das'}
    assert reader_gz.read_list() == {'Test', 'ist', 'ein', 'Das'}

def test_oov_annotator():
    text = "Das iste einex Biespeil fürr Texxt mit viehle Feler."
    spacy = Spacy_Preprocessor(language='de')
    cas = spacy.run(text)
    SE_OOV_Annotator("de").process(cas)

    assert len(cas.select("org.lift.type.Structure")) == 7