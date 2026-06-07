import cassis
from cassis import Cas
from py_lift.dkpro import T_FEATURE, T_TOKEN, T_LEMMA, T_POS

def construct_cas(ts, tokens, lemmas, pos_tags) -> Cas:
    text = ' '.join(tokens)

    cas = cassis.Cas(typesystem=ts)
    cas.sofa_string = text

    begin = 0
    for token, lemma, pos in zip(tokens, lemmas, pos_tags):
        end = begin + len(token)
        
        # Token annotation
        TokenType = ts.get_type(T_TOKEN)
        token_ann = TokenType(begin=begin, end=end)
        cas.add(token_ann)
        
        # Lemma annotation
        LemmaType = ts.get_type(T_LEMMA)
        lemma_ann = LemmaType(begin=begin, end=end)
        lemma_ann.value = lemma
        cas.add(lemma_ann)
        
        # POS annotation
        POSType = ts.get_type(T_POS)
        pos_ann = POSType(begin=begin, end=end)
        pos_ann.PosValue = pos
        cas.add(pos_ann)

        begin += len(token) + 1 

    return cas

def assert_annotations(expected, annotations, key_attr, value_attr):
    """
    Checks that for each expected (key, value) pair there is an annotation 
    where getattr(annotation, key_attr) == key and getattr(annotation, value_attr) == value.
    
    Args:
        expected: List of (key, value) pairs.
        annotations: Iterable of annotation objects.
        value_attr: Name of the attribute in annotation holding the feature value.
    """
    actual = {}
    for anno in annotations:
        key_or_method = getattr(anno, key_attr)
        key = key_or_method() if callable(key_or_method) else key_or_method

        value_or_method = getattr(anno, value_attr)
        value = value_or_method() if callable(value_or_method) else value_or_method

        actual[key] = value
    
    for key, value in expected:
        assert key in actual, f"Missing annotation for '{key}'"
        assert actual[key] == value, f"For '{key}', expected '{value}' but got '{actual[key]}'"