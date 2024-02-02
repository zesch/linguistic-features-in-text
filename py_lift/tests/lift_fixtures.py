import pytest
from cassis import *

T_TOKEN = 'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token'
T_SENTENCE = 'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence'

@pytest.fixture
def typesystem_xml():
    with open("data/TypeSystem.xml", "r") as f:
        return f.read()

@pytest.fixture
def tokens(typesystem_xml):
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
def sentences(typesystem_xml):
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
def cas_simple(typesystem_xml, tokens, sentences):
    ts = load_typesystem(typesystem_xml)
    cas = Cas(ts)
    cas.sofa_string = "This is a tast. A smoll one."

    cas.add_all(tokens)
    cas.add_all(sentences)

    return cas