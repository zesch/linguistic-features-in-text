from __future__ import annotations

import logging
from typing import ClassVar, FrozenSet, Optional, Sequence

from cassis import Cas
from abc import ABC, abstractmethod
from py_lift.util import get_lift_typesystem
from py_lift.decorators import normalize_language

logger = logging.getLogger(__name__)

class UnsupportedLanguageError(ValueError):
    pass

class TypeSystemMismatchError(TypeError):
    pass

class SEL_BaseAnnotator(ABC):
    """Marker base class for all annotators that operate on the LIFT TypeSystem.

    Notes:
    - supported_languages: empty frozenset means 'no restriction'.
    - language is normalized (e.g., 'en_US' -> 'en-US').
    - The CAS MUST use the same TypeSystem instance as self.ts.
    """

    @property
    def ts(self):
        return get_lift_typesystem()

    supported_languages: ClassVar[FrozenSet[str]] = frozenset()
    requires_types: ClassVar[Sequence[str]] = ()

    def __init__(self, language: Optional[str], strict: bool = True):
        self.strict = strict

        # Language normalization and check
        self.language = normalize_language(language) if language else None
        if self.supported_languages and self.language:
            if self.language not in self.supported_languages:
                msg = (
                    f"{self.__class__.__name__}: language '{self.language}' is not supported. "
                    f"Supported: {sorted(self.supported_languages)}"
                )
                if self.strict:
                    raise UnsupportedLanguageError(msg)
                logger.warning(msg)

    def require_same_typesystem(self, cas: Cas) -> None:
        """Ensure the CAS uses the exact same TypeSystem instance as this annotator."""
        if cas.typesystem is not self.ts:
            msg = (
                f"{self.__class__.__name__}: CAS TypeSystem is not the LIFT TypeSystem "
                f"instance used by this annotator. "
                f"Create the CAS with Cas(typesystem=self.ts) or provide the same ts everywhere."
            )
            # Strictly enforce, because adding FS created from a different TS will fail in cassis.
            raise TypeSystemMismatchError(msg)

    def ensure_required_types(self, cas: Cas) -> None:
        missing = []
        for t in self.requires_types:
            try:
                self.get_type(t)
            except Exception:
                missing.append(t)
        if missing:
            msg = f"{self.__class__.__name__}: missing required types in LIFT TS: {missing}"
            if self.strict:
                raise TypeError(msg)
            logger.warning(msg)

    @staticmethod
    def get_cas_language(cas: Cas) -> Optional[str]:
        """Try to read document language from common metadata annotations."""
        for tname in (
            "de.tudarmstadt.ukp.dkpro.core.api.metadata.type.DocumentMetaData",
            "uima.tcas.DocumentAnnotation",
        ):
            try:
                for fs in cas.select(tname):
                    lang = getattr(fs, "language", None)
                    if lang:
                        return normalize_language(lang)
            except Exception:
                continue
        return None

    def validate_language_against_cas(self, cas: Cas) -> None:
        cas_lang = self.get_cas_language(cas)
        if self.language and cas_lang and self.language != cas_lang:
            msg = (
                f"{self.__class__.__name__}: language mismatch: annotator={self.language}, CAS={cas_lang}"
            )
            if self.strict:
                raise UnsupportedLanguageError(msg)
            logger.warning(msg)

    def get_type(self, typename: str):
        """Convenience accessor against the LIFT TS."""
        return self.ts.get_type(typename)

    def process(self, cas: Cas) -> bool:
            self.require_same_typesystem(cas)
            self.ensure_required_types(cas)
            self.validate_language_against_cas(cas)

            return self._process(cas)

    @abstractmethod
    def _process(self, cas: Cas) -> bool:
        """Annotate the CAS. Return True if something was added."""
        pass