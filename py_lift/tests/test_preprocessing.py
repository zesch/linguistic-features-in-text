
import pytest
from util import load_lift_typesystem
from cassis import Cas
from preprocessing import Spacy_Preprocessor
from dkpro import T_TOKEN, T_POS, T_DEP

def test_spacy_preprocessing():
    ts = load_lift_typesystem()
    cas = Cas(typesystem=ts)
    cas.sofa_string = "Demokratie ist eher abstrakt. Leben ist konkret."

    spacy = Spacy_Preprocessor(language='de')
    cas = spacy.run(cas.sofa_string)

    gold_tokens = ["Demokratie", "ist", "eher", "abstrakt", ".", "Leben", "ist", "konkret", "."]
    gold_lemmas = ["Demokratie", "sein", "eher", "abstrakt", ".", "Leben", "sein", "konkret", "."]
    gold_pos = ["NN", "VAFIN", "ADV", "ADJD", "$.", "NN", "VAFIN", "ADJD", "$."]
    
    assert all([a.get_covered_text() == b for a, b in zip(cas.select(T_TOKEN), gold_tokens)])
    assert all([a.get('PosValue') == b for a, b in zip(cas.select(T_POS), gold_pos)])

    # TODO really check all deps
    for dep in cas.select(T_DEP):
        print(dep)
        assert dep.get('Dependent') is not None
        assert dep.get('Governor') is not None
        assert dep.get('DependencyType') is not None