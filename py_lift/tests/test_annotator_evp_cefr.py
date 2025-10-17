import pytest
from util import load_lift_typesystem
from cassis import Cas
from annotators.misc import SE_EvpCefrAnnotator
from dkpro import T_TOKEN, T_POS, T_LEMMA, T_FEATURE

def test_evp_cefr_annotator():
    ts = load_lift_typesystem()
    cas = Cas(typesystem=ts)
    cas.sofa_string = "This is a test. A minimal metaphor. Fake. Fake."

    # TODO can we take more convenient way to test CASes from Cassis?
    T = ts.get_type(T_TOKEN)
    t1 = T(begin=0, end=4)
    t2 = T(begin=5, end=7)
    t3 = T(begin=8, end=9)
    t4 = T(begin=10, end=14)
    t5 = T(begin=14, end=15)
    t6 = T(begin=16, end=17)
    t7 = T(begin=18, end=22)
    t8 = T(begin=23, end=30)
    t9 = T(begin=31, end=32)
    t10 = T(begin=33, end=37)
    t11 = T(begin=38, end=39)
    t12 = T(begin=40, end=44)
    t13 = T(begin=45, end=46)
    cas.add_all([t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12, t13])

    L = ts.get_type(T_LEMMA)
    l1 = L(begin=0, end=4, value="this")
    l2 = L(begin=5, end=7, value="be")
    l3 = L(begin=8, end=9, value="a")
    l4 = L(begin=10, end=14, value="test")
    l5 = L(begin=14, end=15, value=".")
    l6 = L(begin=16, end=17, value="a")
    l7 = L(begin=18, end=22, value="minimal")
    l8 = L(begin=23, end=30, value="metaphor")
    l9 = L(begin=31, end=32, value=".")
    l10 = L(begin=33, end=37, value="Fake")
    l11 = L(begin=38, end=39, value=".")
    l12 = L(begin=40, end=44, value="Fake")
    l13 = L(begin=45, end=46, value=".")
    cas.add_all([l1, l2, l3, l4, l5, l6, l7, l8, l9, l10, l11, l12, l13])

    POS = ts.get_type(T_POS)
    pos1 = POS(begin=0, end=4, PosValue="NN")
    pos2 = POS(begin=5, end=7, PosValue="VB")
    pos3 = POS(begin=8, end=9, PosValue="DT")
    pos4 = POS(begin=10, end=14, PosValue="NN")
    pos5 = POS(begin=14, end=15, PosValue=".")
    pos6 = POS(begin=16, end=17, PosValue="DT")
    pos7 = POS(begin=18, end=22, PosValue="JJ")
    pos8 = POS(begin=23, end=30, PosValue="NN")
    pos9 = POS(begin=31, end=32, PosValue=".")
    pos10 = POS(begin=33, end=37, PosValue="JJ")
    pos11 = POS(begin=38, end=39, PosValue=".")
    pos12 = POS(begin=40, end=44, PosValue="NN")
    pos13 = POS(begin=45, end=46, PosValue=".")
    cas.add_all([pos1, pos2, pos3, pos4, pos5, pos6, pos7, pos8, pos9, pos10, pos11, pos12, pos13])

    SE_EvpCefrAnnotator("en").process(cas)

    words = ["This", "is", "a", "test", "A", "minimal", "metaphor", "Fake", "Fake"]
    labels_cefr = [1, 1, 1, 1, 1, 5, 6, 5, 6]

    words_with_level = {word: level for word, level in zip(words, labels_cefr)}

    for feature in cas.select(T_FEATURE):
        if feature.get_covered_text() in words:
            assert feature.level == words_with_level[feature.get_covered_text()]
        else:
            print('Test failed :)')




    
