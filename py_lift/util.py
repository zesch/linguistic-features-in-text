import typing
import cassis
import pathlib
import polars as pl
from cassis import Cas
from dkpro import T_FEATURE

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
