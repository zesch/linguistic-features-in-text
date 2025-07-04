import pytest
from cassis import Cas
from util import load_lift_typesystem
from dkpro import T_TOKEN, T_SENT

@pytest.fixture
def typesystem_xml():
    with open("data/TypeSystem.xml", "r") as f:
        return f.read()
    
@pytest.fixture
def typesystem():
    return load_lift_typesystem("data/TypeSystem.xml")

@pytest.fixture
def tokens_en(typesystem):
    cas = Cas(typesystem)
    cas.sofa_string = "This is a test. A small one."

    T = typesystem.get_type(T_TOKEN)
    tokens = [
        T(begin=0, end=4),
        T(begin=5, end=7),
        T(begin=8, end=9),
        T(begin=10, end=14),
        T(begin=16, end=17),
        T(begin=18, end=23),
        T(begin=24, end=27)
    ]
    
    # add tokens to cas so that sofa property is set 
    # and get_covered_text can be used
    cas.add_all(tokens)

    return tokens

@pytest.fixture
def sentences_en(typesystem):
    cas = Cas(typesystem)
    cas.sofa_string = "This is a test. A small one."
    
    S = typesystem.get_type(T_SENT)
    
    sentences = [
        S(begin=0, end=15, id="0"),
        S(begin=16, end=27, id="1")
    ]

    # add tokens to cas so that sofa property is set 
    # and get_covered_text can be used
    cas.add_all(sentences)

    return sentences

@pytest.fixture
def cas_no_annotations(typesystem):
    cas = Cas(typesystem)
    cas.sofa_string = "This is a test. A small one."

    return cas

@pytest.fixture
def cas_en_simple(typesystem, tokens_en, sentences_en):
    cas = Cas(typesystem)
    cas.sofa_string = "This is a test. A small one."

    cas.add_all(tokens_en)
    cas.add_all(sentences_en)

    return cas

@pytest.fixture
def cas_en_simple_with_errors(typesystem, tokens_en, sentences_en):
    cas = Cas(typesystem)
    cas.sofa_string = "This is a tast. A smoll one."

    cas.add_all(tokens_en)
    cas.add_all(sentences_en)

    return cas