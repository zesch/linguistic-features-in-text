import pytest
from py_lift.dkpro import T_TOKEN, T_SENT, T_POS, T_DEP
from py_lift.preprocessing import *

def test_spacy_prepro_to_cas():
    text = 'This is a test. A small one.'
    ts = load_lift_typesystem()
    spacy = Spacy_Preprocessor(language='en')
    cas = spacy.run(text)

    expected_token = [[0,4], [5,7], [8,9], [10,14], [14,15], [16,17], [18,23], [24,27], [27,28]]
    expected_sentences = [[0,15], [16,27]]
    expected_pos = [
        ['PRON', 0, 4],
        ['AUX', 5, 7],
        ['DET', 8, 9],
        ['NOUN', 10, 14],
        ['PUNCT', 14, 15],
        ['DET', 16, 17],
        ['ADJ', 18, 23],
        ['PRON', 24, 27],
        ['PUNCT', 27, 28]]
    expected_dependencies = [
        ['is', 'This', 'nsubj', 'basic'],
        ['is', 'test','attr','basic'],
        ['test', 'a', 'det', 'basic'],
        ['is', '.', 'punct', 'basic'],
        ['.', 'one', 'nsubj', 'basic'],
        ['one', 'A', 'det', 'basic'],
        ['one', 'small', 'amod', 'basic']]
    actual_token = []
    actual_sentences = []
    actual_pos = []
    actual_dependencies = []

    for token in cas.select(T_TOKEN):
        actual_token.append([token.begin, token.end])
    for sent in cas.select(T_SENT):
        actual_sentences.append([sent.begin, sent.end])
    for pos in cas.select(T_POS):
        actual_pos.append([pos.PosValue, pos.begin, pos.end])
    for dep in cas.select(T_DEP):
        actual_dependencies.append([dep.Governor, dep.Dependent, dep.DependencyType, dep.flavor])

    assert len(expected_token) == len(actual_token)
    assert len(expected_sentences) == len(actual_sentences)
    assert len(expected_pos) == len(actual_pos)
    assert len(expected_dependencies) == len(actual_dependencies)

    for i in range(len(actual_token)):
        assert expected_token[i] == actual_token[i]
    for i in range(len(actual_sentences)):
        assert expected_sentences[i] == actual_sentences[i]
    for i in range(len(actual_pos)):
        assert expected_pos[i] == actual_pos[i]
    for i in range(len(actual_dependencies)):
        assert expected_dependencies[i] == actual_dependencies[i]

