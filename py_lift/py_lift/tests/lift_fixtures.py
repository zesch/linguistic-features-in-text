import pytest
from cassis import Cas
from py_lift.util import load_lift_typesystem
from py_lift.dkpro import T_TOKEN, T_SENT, T_LEMMA, T_POS

@pytest.fixture
def typesystem_xml():
    with open("data/TypeSystem.xml", "r") as f:
        return f.read()
    
@pytest.fixture
def typesystem():
    return load_lift_typesystem()

@pytest.fixture
def tokens_en(typesystem, pos_en):
    T = typesystem.get_type(T_TOKEN)
    tokens = [
        T(begin=0, end=4, pos=pos_en[0]),
        T(begin=5, end=7, pos=pos_en[1]),
        T(begin=8, end=9, pos=pos_en[2]),
        T(begin=10, end=14, pos=pos_en[3]),
        T(begin=14, end=15, pos=pos_en[4]),
        T(begin=16, end=17, pos=pos_en[5]),
        T(begin=18, end=23, pos=pos_en[6]),
        T(begin=24, end=27, pos=pos_en[7]),
        T(begin=27, end=28, pos=pos_en[8])
    ]
    return tokens

@pytest.fixture
def lemmas_en(typesystem):
    L = typesystem.get_type(T_LEMMA)
    lemmas = [
        L(begin=0, end=4, value="this"),
        L(begin=5, end=7, value="be"),
        L(begin=8, end=9, value="a"),
        L(begin=10, end=14, value="test"),
        L(begin=14, end=15, value="."),
        L(begin=16, end=17, value="a"),
        L(begin=18, end=23, value="small"),
        L(begin=24, end=27, value="one"),
        L(begin=27, end=28, value=".")
    ]
    return lemmas

@pytest.fixture
def pos_en(typesystem):
    P = typesystem.get_type(T_POS)
    pos_tags = [
        P(begin=0, end=4, PosValue="DT"),
        P(begin=5, end=7, PosValue="VBZ"),
        P(begin=8, end=9, PosValue="DT"),
        P(begin=10, end=14, PosValue="NN"),
        P(begin=14, end=15, PosValue="."),
        P(begin=16, end=17, PosValue="DT"),
        P(begin=18, end=23, PosValue="JJ"),
        P(begin=24, end=27, PosValue="NN"),
        P(begin=27, end=28, PosValue=".")
    ]
    return pos_tags

@pytest.fixture
def sentences_en(typesystem):  
    S = typesystem.get_type(T_SENT)
    
    sentences = [
        S(begin=0, end=15, id="0"),
        S(begin=16, end=28, id="1")
    ]

    return sentences

@pytest.fixture
def cas_no_annotations(typesystem):
    cas = Cas(typesystem)
    cas.sofa_string = "This is a test. A small one."

    return cas

@pytest.fixture
def cas_en_simple(typesystem, tokens_en, lemmas_en, pos_en, sentences_en):
    cas = Cas(typesystem)
    cas.sofa_string = "This is a test. A small one."

    cas.add_all(tokens_en)
    cas.add_all(lemmas_en)
    cas.add_all(pos_en)
    cas.add_all(sentences_en)

    return cas

@pytest.fixture
def cas_en_simple_with_errors(typesystem, tokens_en, pos_en, lemmas_en, sentences_en):
    cas = Cas(typesystem)
    cas.sofa_string = "This is a tast. A smoll one."
    lemmas_en[3].value = "tast"  # introduce error in lemma
    lemmas_en[6].value = "smoll"  # introduce error in lemma

    cas.add_all(tokens_en)
    cas.add_all(lemmas_en)
    cas.add_all(pos_en)
    cas.add_all(sentences_en)

    return cas