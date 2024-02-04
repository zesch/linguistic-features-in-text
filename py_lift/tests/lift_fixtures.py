import pytest
from cassis import *

T_TOKEN = 'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token'
T_SENTENCE = 'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence'

@pytest.fixture
def typesystem_xml():
    with open("data/TypeSystem.xml", "r") as f:
        return f.read()

@pytest.fixture
def tokens_en(typesystem_xml):
    ts = load_typesystem(typesystem_xml)
    T = ts.get_type(T_TOKEN)
    tokens = [
        T(begin=0, end=4),
        T(begin=5, end=7),
        T(begin=8, end=9),
        T(begin=10, end=14),
        T(begin=16, end=17),
        T(begin=18, end=23),
        T(begin=24, end=27)
    ]
    # cas.add_all(tokens)

    return tokens

@pytest.fixture
def sentences_en(typesystem_xml):
    ts = load_typesystem(typesystem_xml)
    S = ts.get_type(T_SENTENCE)
    
    sentences = [
        S(begin=0, end=15, id="0"),
        S(begin=16, end=27, id="1")
    ]

    return sentences

@pytest.fixture
def cas_no_annotations(typesystem_xml):
    ts = load_typesystem(typesystem_xml)
    cas = Cas(ts)
    cas.sofa_string = "This is a tast. A smoll one."

    return cas

@pytest.fixture
def cas_en_simple(typesystem_xml, tokens_en, sentences_en):
    ts = load_typesystem(typesystem_xml)
    cas = Cas(ts)
    cas.sofa_string = "This is a test. A small one."

    cas.add_all(tokens_en)
    cas.add_all(sentences_en)

    return cas

@pytest.fixture
def cas_en_simple_with_errors(typesystem_xml, tokens_en, sentences_en):
    ts = load_typesystem(typesystem_xml)
    cas = Cas(ts)
    cas.sofa_string = "This is a tast. A smoll one."

    cas.add_all(tokens_en)
    cas.add_all(sentences_en)

    return cas