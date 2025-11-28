from cassis import Cas
from py_lift.dkpro import T_FEATURE
from py_lift.util import load_lift_typesystem
from typing import Callable, Any, Optional, Union, List
from abc import ABC, abstractmethod


class FEL_BaseExtractor(ABC):
    """Marker base class for all extractors."""

    # whether to raise exceptions on errors (e.g., division by zero)
    # by default, errors are silently handled (e.g., ratio set to 0)
    # but strict mode can be useful for debugging
    strict: bool = False 

    def __init__(self):
        self.ts = load_lift_typesystem()

    @abstractmethod
    def extract(self, cas: Cas) -> bool:
        pass

class FEL_BaseCounter(ABC):
    """Marker base class for all counters."""
    
    @abstractmethod
    def count(self, cas: Cas) -> int:
        pass

    @abstractmethod
    def feature_name(self) -> str:
        pass

class FEL_AnnotationCounter(FEL_BaseExtractor, FEL_BaseCounter):
    """Counts annotations of a specific type.
    For unique counts, a custom function can be provided to convert
    an annotation to a string representation.
    By default, the covered text is used."""
    
    def __init__(
        self, 
        _type: str, 
        unique: bool = False, 
        custom_to_string: Optional[Callable[[Any], str]] = None
    ):
        super().__init__()
        self.type = _type
        self.unique = unique
        self.to_string = custom_to_string or (
            lambda x: x.get_covered_text() if x is not None else ''
        )
    
    def feature_name(self) -> str:
        name = f"{self.type}_COUNT"
        if self.unique:
            name += "_UNIQUE"
        return name
        
    def count(self, cas: Cas) -> int:
        if not self.unique:
            return sum(1 for _ in cas.select(self.type))
        
        # Count unique string representations
        unique_values = {self.to_string(anno) for anno in cas.select(self.type)}
        print(unique_values)

        return len(unique_values)
    
    def extract(self, cas: Cas) -> bool:
        count = self.count(cas)
        
        F = self.ts.get_type(T_FEATURE)
        feature = F(name=self.feature_name(), value=count, begin=0, end=0)
        cas.add(feature)

        return True

class FEL_FeatureValueCounter(FEL_BaseExtractor, FEL_BaseCounter):
    """Counts occurrences of specific feature values."""
    
    allowed_feature_values: List[str]

    def __init__(
        self, 
        _type: str, 
        feature_path: str, 
        feature_values: Optional[Union[str, List[str]]] = None
    ):
        super().__init__()
        self.type = _type
        self.feature_path = feature_path

        if feature_values is None:
            self.allowed_feature_values = []
        elif isinstance(feature_values, str):
            self.allowed_feature_values = [feature_values]
        else:
            # TODO TBD do we want shallow copy here?
            self.allowed_feature_values = list(feature_values)

    def feature_name(self) -> str:
        name = f"{self.type}"
        if self.allowed_feature_values:
            name += "_" + "_".join(self.allowed_feature_values)
        name += "_FEATURECOUNT"
        return name
    
    def _get_feature_value(self, anno):
        """Get feature value from annotation."""
        feature = anno.get(self.feature_path)
        return feature if feature is not None else ''
    
    def count(self, cas) -> int:
        """Count annotations with specific feature values."""
        count = 0
        for anno in cas.select(self.type):
            feature_value = self._get_feature_value(anno)
            
            if not self.allowed_feature_values:
                count += 1
            elif feature_value in self.allowed_feature_values:
                count += 1
        
        return count
    
    def extract(self, cas: Cas) -> bool:
        count = self.count(cas)
        
        F = self.ts.get_type(T_FEATURE)
        feature = F(name=self.feature_name(), value=count, begin=0, end=0)
        cas.add(feature)
        
        return True

class FEL_AnnotationRatio(FEL_BaseExtractor):
    """Computes ratio between two annotation counts."""
    
    def __init__(self, counter_dividend: FEL_BaseCounter, counter_divisor: FEL_BaseCounter):
        super().__init__()
        self.counter_dividend = counter_dividend
        self.counter_divisor = counter_divisor

    def feature_name(self) -> str:
        name = f"{self.counter_dividend.feature_name()}_PER_{self.counter_divisor.feature_name()}"
        return name        
    
    def extract(self, cas: Cas) -> bool:
        count_dividend = self.counter_dividend.count(cas)
        count_divisor = self.counter_divisor.count(cas)
        
        if count_divisor == 0:
            if self.strict:
                raise ZeroDivisionError(f"Division by zero when calculating ratio {self.feature_name()}.")
            ratio = 0.0
        else:
            ratio = count_dividend / count_divisor
        
        F = self.ts.get_type(T_FEATURE)
        feature = F(name=self.feature_name(), value=ratio, begin=0, end=0)
        cas.add(feature)

        return True

class FEL_Length(FEL_BaseExtractor):
    def __init__(self, annotation_type: str):
        super().__init__()
        self.annotation_type = annotation_type

    def extract(self, cas: Cas) -> bool:
        lengths = [anno.end - anno.begin for anno in cas.select(self.annotation_type)]

        if not lengths:
            min_val = max_val = mean = None 
            print("No values found for annotation: " + self.annotation_type)
            if (self.strict):
                raise ValueError(f"No annotations found for type {self.annotation_type} when calculating lengths.")
        else:
            min_val = min(lengths)
            max_val = max(lengths)
            mean = sum(lengths) / len(lengths)

        F = self.ts.get_type(T_FEATURE)
        f_mean = F(name=self.annotation_type + '_length_mean', value=mean, begin=0, end=0)
        cas.add(f_mean)

        f_min = F(name=self.annotation_type + '_length_min', value=min_val, begin=0, end=0)
        cas.add(f_min)

        f_max = F(name=self.annotation_type + '_length_max', value=max_val, begin=0, end=0)
        cas.add(f_max)

        return True

class FEL_Min_Max_Mean(FEL_BaseExtractor):
    """Calculates min, max, and mean of numeric feature values of the given annotation type.
    An example would be abstractness scores for each token. 
    """
    
    def __init__(self, annotation_type: str, feature_path: str):
        super().__init__()
        self.annotation_type = annotation_type
        self.feature_path = feature_path 

    def _get_feature_value(self, anno):
        feature = anno.get(self.feature_path)
        return feature if feature is not None else ''

    def collect_values(self, cas):
        """Collects all values at the feature path of the given annotation as floats from the CAS."""
        return [float(self._get_feature_value(anno)) for anno in cas.select(self.annotation_type)]

    def extract(self, cas):
        vals = self.collect_values(cas)

        if not vals:
            min_val = max_val = mean = None 
            print("No values found for annotation: " + self.annotation_type)
            if (self.strict):
                raise ValueError(f"No annotations found for type {self.annotation_type} when calculating min/max/mean.")    
        else:
            min_val = min(vals)
            max_val = max(vals)
            mean = sum(vals) / len(vals)

        F = self.ts.get_type(T_FEATURE)
        f_mean = F(name=self.annotation_type + '_mean', value=mean, begin=0, end=0)
        cas.add(f_mean)

        f_min = F(name=self.annotation_type + '_min', value=min_val, begin=0, end=0)
        cas.add(f_min)

        f_max = F(name=self.annotation_type + '_max', value=max_val, begin=0, end=0)
        cas.add(f_max)

        return True
    
class FE_NumberOfSpellingAnomalies(FEL_AnnotationCounter):
    def __init__(self):
        super().__init__('SpellingAnomaly')

class FE_NounPhrasesPerSentence(FEL_AnnotationRatio):
    def __init__(self):
        super().__init__(
            FEL_AnnotationCounter('NC'),
            FEL_AnnotationCounter('Sentence')
        )
        
class FE_TokensPerSentence(FEL_AnnotationRatio):
    def __init__(self):
        super().__init__(
            FEL_AnnotationCounter('Token'),
            FEL_AnnotationCounter('Sentence')
        )

class FE_EasyWordRatio(FEL_AnnotationRatio):
    def __init__(self):
        super().__init__(
            FEL_AnnotationCounter('EasyWord'),
            FEL_AnnotationCounter('Token')
        )

class FE_AbstractnessStats(FEL_Min_Max_Mean):
    def __init__(self):
        super().__init__('org.lift.type.AbstractnessConcreteness', 'value')