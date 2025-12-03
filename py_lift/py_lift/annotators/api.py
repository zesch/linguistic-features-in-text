from cassis import Cas
from abc import ABC, abstractmethod
from py_lift.util import load_lift_typesystem

class SEL_BaseAnnotator(ABC):
    """Marker base class for all annotators."""
    
    supported_languages = set()  # to be defined in subclasses
    
    def __init__(self, language, ts=None):
        self.language = language
        if (ts is not None):
            self.ts = ts
        else:
            self.ts = load_lift_typesystem()
        if hasattr(self, 'supported_languages'):
            if self.language not in self.supported_languages:
                raise ValueError(
                    f"{self.language} is not a supported language."
                )

    @abstractmethod
    def process(self, cas: Cas) -> bool:
        pass