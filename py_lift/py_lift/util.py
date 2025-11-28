import typing
import cassis
import pathlib
import csv
import polars as pl
import inspect
import re
import string
from cassis import Cas
from py_lift.dkpro import T_FEATURE, T_TOKEN, T_LEMMA, T_POS
from types import ModuleType
from typing import Type, List
from lingua import LanguageDetectorBuilder
from importlib.resources import files

def detect_language(text: str) -> str:
    detector = LanguageDetectorBuilder.from_all_spoken_languages().build()
    return str(detector.detect_language_of(text).iso_code_639_1.name).lower()

# def load_lift_typesystem() -> cassis.TypeSystem:
#     return load_typesystem('py_lift/data/TypeSystem.xml')

def load_lift_typesystem() -> cassis.TypeSystem:
    with (files("py_lift.data") / "TypeSystem.xml").open("rb") as f:
        return cassis.load_typesystem(f)

def load_typesystem(typesystem: typing.Union[cassis.TypeSystem, str]) -> cassis.TypeSystem:
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

def get_all_subclasses(mymodule: ModuleType, MyBase: Type) -> List[Type]:
    return [
        obj for name, obj in vars(mymodule).items()
        if isinstance(obj, type) and issubclass(obj, MyBase) and obj is not MyBase
    ]

def get_constructor_params(cls):
    sig = inspect.signature(cls.__init__)
    params = [
        param for name, param in sig.parameters.items()
        if name != 'self'
    ]
    return params

def df_features(cas: Cas) -> pl.DataFrame:
    features = []

    for anno in cas.select(T_FEATURE):
        features.append({
            'name': anno.get('name'),
            'value': anno.get('value')
        })

    return pl.DataFrame(features)

def print_features(cas, sort_by='name', abbreviate=True, float_decimals=4):
    """
    Print all features from CAS in a readable format.
    
    Args:
        cas: The CAS object
        sort_by: 'name' or 'value' for sorting
        abbreviate: Whether to abbreviate long package-style names
        float_decimals: Number of decimal places to show for float values
    """
    F = load_lift_typesystem().get_type(T_FEATURE)
    features = list(cas.select(F))
    
    if not features:
        print("No features found.")
        return
    
    # Sort features
    if sort_by == 'value':
        features.sort(key=lambda f: f.value, reverse=True)
    else:
        features.sort(key=lambda f: f.name)
    
    # Calculate max name length for proper alignment
    max_name_len = max(len(abbreviate_package_name(f.name) if abbreviate else f.name) 
                       for f in features)
    name_width = max(max_name_len, 30)  # At least 30 chars
    total_width = name_width + 20
    
    # Print header
    print("\n" + "=" * total_width)
    print(f"Features (sorted by {sort_by})")
    print("=" * total_width)
    print(f"{'Name':<{name_width}} {'Value':>15}")
    print("-" * total_width)
    
    # Print features
    for feature in features:
        display_name = abbreviate_package_name(feature.name) if abbreviate else feature.name
        
        # Format value based on type
        if isinstance(feature.value, float):
            print(f"{display_name:<{name_width}} {feature.value:>15.{float_decimals}f}")
        elif isinstance(feature.value, int):
            print(f"{display_name:<{name_width}} {feature.value:>15d}")
        else:
            print(f"{display_name:<{name_width}} {str(feature.value):>15}")
    
    print("-" * total_width)
    print(f"Total: {len(features)} features\n")

def abbreviate_package_name(name: str) -> str:
    """
    Abbreviate Java-style package names while keeping important parts readable.
    Always keeps the last part full, and keeps parts that look like class names.
    
    Example:
        de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS_ADJ_PER_de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token
        -> d.t.u.d.c.a.l.t.p.POS_ADJ_PER_d.t.u.d.c.a.s.t.Token
    """
    parts = name.split('.')
    
    if len(parts) <= 2:
        return name  # Already short enough
    
    abbreviated = []
    for i, part in enumerate(parts):
        # Always keep the last part full
        if i == len(parts) - 1:
            abbreviated.append(part)
        # Keep the part full if it:
        # - Contains uppercase letters (but not just first letter)
        # - Contains underscores
        # - Contains digits
        # - Is very short (already abbreviated)
        elif (len(part) <= 1 or 
              '_' in part or 
              any(c.isupper() for c in part[1:]) or
              any(c.isdigit() for c in part)):
            abbreviated.append(part)
        else:
            abbreviated.append(part[0])
    
    return '.'.join(abbreviated)

def format_value(value, decimals=4):
    """Format a value, showing fewer decimals for floats."""
    if isinstance(value, float):
        return f"{value:.{decimals}f}"
    return str(value)


# Match only digits and common punctuation
_PATTERN_DIGITS_AND_PUNCT = re.compile(r'^[\d!-/:-@\[-`{-~]+$')

def is_digits_or_punct(s: str) -> bool:
    """Check if string contains only digits and punctuation."""
    return bool(_PATTERN_DIGITS_AND_PUNCT.match(s))

punct = string.punctuation.replace("'", "")
# Escape all special characters for use in a regex character class
escaped_punct = re.escape(punct)
_PATTERN_PUNCT_NO_APOSTROPHE = re.compile(f"[{escaped_punct}]")

def contains_punct_except_apostrophe(s: str) -> bool:
    """Check if string contains at least one punctuation character except apostrophe."""
    return bool(_PATTERN_PUNCT_NO_APOSTROPHE.search(s))
