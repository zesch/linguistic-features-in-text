import typing
import cassis
import pathlib
import csv
import polars as pl
from cassis import Cas
from dkpro import T_FEATURE, T_TOKEN, T_LEMMA, T_POS

def load_lift_typesystem(typesystem: typing.Union[cassis.TypeSystem, str]) -> cassis.TypeSystem:
    def load_typesystem_from_file(path):
        with open(path, 'rb') as f:
            return cassis.load_typesystem(f)

    ts_typemap = {
        pathlib.Path: load_typesystem_from_file,
        str: load_typesystem_from_file,
        cassis.TypeSystem: identity
    }

    return map_from_type(typesystem, ts_typemap)

def map_from_type(x, type_to_mapper: dict):
    T = type(x)
    mapping_fn = type_to_mapper.get(T)

    if mapping_fn is None:
        raise ValueError

    return mapping_fn(x)

def identity(x):
    return x

def resolve_annotation(annotation_path: str, feature_seperator='/') -> typing.Tuple[str, str]:
    if feature_seperator == '.':
        raise ValueError('Feature separator must not be "."')

    split = annotation_path.split(feature_seperator)

    if len(split) > 2:
        raise ValueError(f'Annotation Path is ill defined, as it contains multiple features, seperated by {feature_seperator}')

    # no feature in annotation path
    if len(split) == 1:
        return split[0], ''

    type_path, feature_path = split

    return type_path, feature_path

def df_features(cas: Cas) -> pl.DataFrame:
    features = []

    for anno in cas.select(T_FEATURE):
        features.append({
            'name': anno.get('name'),
            'value': anno.get('value')
        })

    return pl.DataFrame(features)


def read_list(file_path: pathlib.Path) -> typing.List[str]:
    with file_path.open("r", encoding="utf-8") as f:
        readlist = [line.strip() for line in f]
    return readlist

def read_tsv_to_dict(filename, key_column, value_column):
    result = {}
    with open(filename, encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            key = row[key_column]
            value = row[value_column]
            result[key] = value
    return result

def construct_cas(ts, tokens, lemmas, pos_tags):
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

def get_all_subclasses(mymodule, MyBase):
    return [
        obj for name, obj in vars(mymodule).items()
        if isinstance(obj, type) and issubclass(obj, MyBase) and obj is not MyBase
    ]