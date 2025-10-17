from cassis import Cas
from abc import ABC, abstractmethod

class SEL_BaseAnnotator(ABC):
    """Marker base class for all annotators."""
    
    @abstractmethod
    def process(self, cas: Cas) -> bool:
        pass