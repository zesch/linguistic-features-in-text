from typing import FrozenSet, Optional, Callable, Tuple, TypeVar, cast

def normalize_language(lang: Optional[str]) -> Optional[str]:
    if not lang:
        return None
    lang = lang.replace('_', '-')          # en_US -> en-US
    parts = lang.split('-')
    parts[0] = parts[0].lower()             # primary subtag lowercase
    if len(parts) > 1 and len(parts[1]) == 2:
        parts[1] = parts[1].upper()         # region uppercase
    return '-'.join(parts)

def supported_languages(*langs: str, normalize_codes: bool = True):
    """Class decorator to declare supported languages.
    Empty set means: no restriction.
    """
    if normalize_codes:
        normalized: FrozenSet[str] = frozenset(
            filter(None, (normalize_language(l) for l in langs))
        )
    else:
        normalized = frozenset(langs)

    def decorator(cls):
        # Assign an immutable set to avoid accidental mutation
        cls.supported_languages = normalized
        return cls
    return decorator


C = TypeVar("C", bound=type)

def requires_types(*typenames: str, extend: bool = False) -> Callable[[C], C]:
    """
    Class decorator to declare required type names.

    - If extend=False (default), it overrides any existing declaration.
    - If extend=True, it merges with any existing requires_types found on the class.
    """
    def decorator(cls: C) -> C:
        prev = tuple(getattr(cls, "requires_types", ()))
        if extend and prev:
            # stable order + dedup
            merged = tuple(dict.fromkeys([*prev, *typenames]))
            cls.requires_types = merged  # type: ignore[attr-defined]
        else:
            cls.requires_types = tuple(typenames)  # type: ignore[attr-defined]
        return cls
    return decorator