
import pytest
from util import load_lift_typesystem
from cassis import Cas
from preprocessing import Spacy_Preprocessor
from dkpro import T_TOKEN, T_POS, T_DEP, T_SENT

def test_spacy_preprocessing():
    ts = load_lift_typesystem()
    text = "Demokratie ist eher abstrakt. Leben ist konkret."
    spacy = Spacy_Preprocessor(language='de')
    cas = spacy.run(text)

    gold_tokens = ["Demokratie", "ist", "eher", "abstrakt", ".", "Leben", "ist", "konkret", "."]
    gold_lemmas = ["Demokratie", "sein", "eher", "abstrakt", ".", "Leben", "sein", "konkret", "."]
    gold_pos = ["NN", "VAFIN", "ADV", "ADJD", "$.", "NN", "VAFIN", "ADJD", "$."]
    gold_sentences = [[28, 29], [47, 48]]
    gold_tok_index = [[0, 10], [11, 14], [15, 19], [20, 28], [28, 29], [30, 35], [36, 39], [40, 47], [47, 48]]
    gold_dep = [[gold_tokens[1], gold_tokens[0], 'nsubj', 'basic'],
                [gold_tokens[3], gold_tokens[2], 'cop', 'basic'],
                [gold_tokens[1], gold_tokens[3], 'advmod', 'basic'],
                [gold_tokens[1], gold_tokens[4], 'punct', 'basic'],
                [gold_tokens[6], gold_tokens[5], 'nsubj', 'basic'],
                [gold_tokens[6], gold_tokens[7], 'cop', 'basic'],
                [gold_tokens[6], gold_tokens[8], 'punct', 'basic']]
    
    assert all([a.get_covered_text() == b for a, b in zip(cas.select(T_TOKEN), gold_tokens)])
    assert all([a.get('PosValue') == b for a, b in zip(cas.select(T_POS), gold_pos)])

    found_sents = []
    for sent in cas.select(T_SENT):
        print([sent.begin, sent.end])
        found_sents.append([sent.begin, sent.end])
    for i in range(len(found_sents)):
        assert found_sents[i] == gold_sentences[i]



    # TODO really check all deps
    found_dep = []
    for dep in cas.select(T_DEP):
        print(dep)
        found_dep.append([cas.sofa_string[dep.Governor.begin: dep.Governor.end],
                                 cas.sofa_string[dep.Dependent.begin: dep.Dependent.end],
                                 #TODO spacy dependencytype mapping to dkpro dependencytype
                                 #dep.DependencyType,
                                 dep.flavor])
        #assert dep.get('Dependent') is not None
        #assert dep.get('Governor') is not None
    for i in range(len(found_dep)):
        assert found_dep[i] == [gold_dep[i][0], gold_dep[i][1], gold_dep[i][3]]
