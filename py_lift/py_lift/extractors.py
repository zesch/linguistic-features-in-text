from cassis import Cas
from py_lift.dkpro import T_FEATURE
from py_lift.util import load_lift_typesystem
from typing import Callable, Any, Optional
from abc import ABC, abstractmethod

class FEL_BaseExtractor(ABC):
    """Marker base class for all extractors."""
    
    def __init__(self):
        self.ts = load_lift_typesystem()
    
    @abstractmethod
    def extract(self, cas: Cas) -> bool:
        pass

# TODO rename type to annotation_type to avoid conflict with built-in type()
class FEL_AnnotationCounter(FEL_BaseExtractor):
    def __init__(
            self, 
            type: str, 
            feature_path='', 
            allowed_feature_values = [], 
            unique=False, 
            custom_to_string: Optional[Callable[[Any], str]] = None
    ):
        super().__init__()
        self.type = type
        self.unique = unique
        self.feature_path = feature_path
        self.allowed_feature_values = allowed_feature_values

        if custom_to_string is not None:
            self.to_string = custom_to_string
        else:
            self.to_string = lambda x: x.get_covered_text() if x is not None else ''

    def _get_feature_value(self, anno):
        feature = anno.get(self.feature_path)
        return feature if feature is not None else ''
        
    def count(self, cas):
        elements = {}
        for anno in cas.select(self.type):
            if self.feature_path != '':
                anno_value = self._get_feature_value(anno)

                if anno_value in self.allowed_feature_values:
                    str_repr = self.to_string(anno)
                    elements[str_repr] = elements.get(str_repr, 0) + 1
            else:    
                str_repr = anno.get_covered_text()
                elements[str_repr] = elements.get(str_repr, 0) + 1
        
        if self.unique:
            print(elements)
            return len(elements.keys())
        else: 
            return sum(elements.values())

    def extract(self, cas: Cas) -> bool:
        count = self.count(cas)
        
        name = self.type + '_COUNT'

        if self.unique:
            name = name + '_UNIQUE'

        if self.feature_path != '':
            name = name + '_' + self.feature_path + '_' + '_'.join(self.allowed_feature_values)

        F = self.ts.get_type(T_FEATURE)
        feature = F(name=name, value=count, begin=0, end=0)
        cas.add(feature)

        return True


class FEL_AnnotationRatio(FEL_BaseExtractor):

    def __init__(self, type_dividend, type_divisor):
        super().__init__()
        self.dividend_type = type_dividend
        self.divisor_type = type_divisor

    def count(self, cas, type):
        size = 0
        for anno in cas.select(type):
            size += 1
        return size

    def extract(self, cas: Cas) -> bool:
        count_dividend = self.count(cas, self.dividend_type)
        count_divisor = self.count(cas, self.divisor_type)

        # TODO catch division by zero
        ratio = count_dividend / count_divisor

        name = self.dividend_type + '_PER_' + self.divisor_type

        F = self.ts.get_type(T_FEATURE)
        feature = F(name=name, value=ratio, begin=0, end=0)
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
        super().__init__('NC',
                         'Sentence')
        
class FE_TokensPerSentence(FEL_AnnotationRatio):
    def __init__(self):
        super().__init__('Token',
                         'Sentence')

class FE_EasyWordRatio(FEL_AnnotationRatio):
    def __init__(self):
        super().__init__('EasyWord',
                         'Token')

class FE_AbstractnessStats(FEL_Min_Max_Mean):
    def __init__(self):
        super().__init__('org.lift.type.AbstractnessConcreteness', 'value')