import typing
import cassis
import pathlib
import csv
import polars as pl
import inspect
import re
import string
import os
import pathlib
from functools import lru_cache
from cassis import Cas
from py_lift.dkpro import T_FEATURE, T_TOKEN, T_LEMMA, T_POS
from types import ModuleType
from typing import Type, List, Union, Optional
from lingua import LanguageDetectorBuilder
from importlib.resources import files


# --- Singleton LIFT TypeSystem ------------------------------------------------

@lru_cache(maxsize=1)
def get_lift_typesystem() -> cassis.TypeSystem:
    """Return the singleton LIFT TypeSystem instance.
    This guarantees identity equality across the process.
    """
    with (files("py_lift.data") / "TypeSystem.xml").open("rb") as f:
        ts = cassis.load_typesystem(f)
    return ts


# Backward-compatible alias (semantic: returns the cached singleton).
def load_lift_typesystem() -> cassis.TypeSystem:
    return get_lift_typesystem()

def reset_lift_typesystem_cache() -> None:
    """For tests: clear the singleton cache so the next call rebuilds the TS."""
    get_lift_typesystem.cache_clear()


# --- CAS helpers --------------------------------------------------------------

def new_lift_cas() -> cassis.Cas:
    """Create a new CAS that uses the singleton LIFT TypeSystem."""
    return cassis.Cas(typesystem=get_lift_typesystem())


def load_cas_from_xmi_with_lift_ts(source: Union[str, os.PathLike, bytes, bytearray]) -> cassis.Cas:
    """Load a CAS from XMI, enforcing the singleton LIFT TypeSystem identity."""
    ts = get_lift_typesystem()
    # cassis.load_cas_from_xmi supports path-like or bytes and accepts typesystem=
    if isinstance(source, (bytes, bytearray)):
        return cassis.load_cas_from_xmi(source, typesystem=ts)
    else:
        with open(source, "rb") as fh:
            return cassis.load_cas_from_xmi(fh, typesystem=ts)


# --- Generic TypeSystem resolver (robust isinstance mapping) ------------------

def load_typesystem(ts_or_path: Union[cassis.TypeSystem, str, os.PathLike]) -> cassis.TypeSystem:
    """Return a TypeSystem from a path or pass-through an existing one.
    Note: This loads a NEW TypeSystem when given a path; it is not the singleton.
    Use get_lift_typesystem() for the LIFT TS shared across annotators.
    """
    if isinstance(ts_or_path, cassis.TypeSystem):
        return ts_or_path
    if isinstance(ts_or_path, (str, os.PathLike)):
        with open(ts_or_path, "rb") as f:
            return cassis.load_typesystem(f)
    raise TypeError(
        f"Unsupported typesystem argument of type {type(ts_or_path)!r}; "
        f"expected cassis.TypeSystem, str, or os.PathLike."
    )


# --- Guards / diagnostics -----------------------------------------------------

class TypeSystemMismatchError(TypeError):
    pass


def require_same_typesystem(cas: cassis.Cas, ts: Optional[cassis.TypeSystem] = None) -> None:
    """Ensure CAS uses the exact same TypeSystem instance (identity) as the given or LIFT TS."""
    expected = ts if ts is not None else get_lift_typesystem()
    ts_cas = getattr(cas, "typesystem", None) or getattr(cas, "type_system", None)
    if ts_cas is not expected:
        raise TypeSystemMismatchError(
            "CAS TypeSystem is not the LIFT TypeSystem instance. "
            "Create the CAS with Cas(typesystem=get_lift_typesystem()) or pass "
            "typesystem=get_lift_typesystem() when loading XMI."
        )

def detect_language(text: str) -> str:
    detector = LanguageDetectorBuilder.from_all_spoken_languages().build()
    return str(detector.detect_language_of(text).iso_code_639_1.name).lower()

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
