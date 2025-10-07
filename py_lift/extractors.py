from cassis import Cas
from util import load_lift_typesystem
from typing import Callable, Any, Optional

class FEL_AnnotationCounter:
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


class FEL_AnnotationRatio:

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


