from cassis import Cas
from util import load_lift_typesystem
from typing import Callable, Any, Optional
from abc import ABC, abstractmethod

class FEL_BaseExtractor(ABC):
    """Marker base class for all extractors."""
    
    @abstractmethod
    def extract(self, cas: Cas) -> bool:
        pass

class FEL_Abstractness_min_max_avg(FEL_BaseExtractor):
    def __init__(self):
        self.ts = load_lift_typesystem()
        self.type = 'org.lift.type.AbstractnessConcreteness'

    def count_and_collect(self, cas, type):
        size = 0
        vals = []
        # geht nicht rein
        print(type)
        for anno in cas.select(type):
            print('heloooooooo')
            size += 1
            vals.append(anno.value)

        return [size, vals]


    def extract(self, cas: Cas) -> bool:
        count = self.count_and_collect(cas, self.type)[0]
        print(count)
        vals = self.count_and_collect(cas, self.type)[1]
        print(vals)

        min_val = -1
        max_val = -1
        added_vals = 0

        for val in vals:
            added_vals += val

            if min_val == -1:
                min_val = val
            else:
                if val < min_val:
                    min_val = val

            if max_val == -1:
                max_val = val
            else:
                if val > max_val:
                    max_val = val

        avg = added_vals/count
        # write feature value in CAS
        T_FEATURE = 'org.lift.type.FeatureAnnotationNumeric'

        F = self.ts.get_type(T_FEATURE)
        feature = F(name='Abstractness_AVG', value=avg, begin=0, end=0)
        cas.add(feature)

        F = self.ts.get_type(T_FEATURE)
        feature = F(name='Abstractness_MIN', value=min_val, begin=0, end=0)
        cas.add(feature)

        F = self.ts.get_type(T_FEATURE)
        feature = F(name='Abstractness_MAX', value=max_val, begin=0, end=0)
        cas.add(feature)

        return True


class FEL_AnnotationCounter(FEL_BaseExtractor):
    def __init__(
            self, 
            type, 
            feature_path='', 
            allowed_feature_values = [], 
            unique=False, 
            custom_to_string: Optional[Callable[[Any], str]] = None
    ):
        self.ts = load_lift_typesystem()
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
        
    def count(self, cas, type):
        elements = {}
        for anno in cas.select(type):
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
        count = self.count(cas, self.type)
        
        name = self.type + '_COUNT'

        if self.unique:
            name = name + '_UNIQUE'

        if self.feature_path != '':
            name = name + '_' + self.feature_path + '_' + '_'.join(self.allowed_feature_values)

        # write feature value in CAS
        T_FEATURE = 'org.lift.type.FeatureAnnotationNumeric'

        F = self.ts.get_type(T_FEATURE)
        feature = F(name=name, value=count, begin=0, end=0)
        cas.add(feature)

        return True


class FEL_AnnotationRatio(FEL_BaseExtractor):

    def __init__(self, type_dividend, type_divisor):
        self.ts = load_lift_typesystem()
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

        # write feature value in CAS
        T_FEATURE = 'org.lift.type.FeatureAnnotationNumeric'

        F = self.ts.get_type(T_FEATURE)
        feature = F(name=name, value=ratio, begin=0, end=0)
        cas.add(feature)

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
class FE_Abstractness_Stats(FEL_Abstractness_min_max_avg):
    def __init__(self):
        super().__init__()

