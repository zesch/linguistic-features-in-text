from cassis import Cas
from util import load_typesystem
from textstat import *

class FEL_AnnotationRatio:

    def __init__(self, type_dividend, type_divisor):
        self.ts = load_typesystem('data/TypeSystem.xml')
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
        feature = F(name=name, value=ratio)
        cas.add(feature)

        return True

class FEL_ReadabilityScore:
    def __init__(self, lang):
        self.ts = load_typesystem('data/TypeSystem.xml')
        self.lang = lang

    def extract(self, cas: Cas, view) -> bool:
        casView = cas.get_view(view)
        textstat.set_lang(self.lang)
        readability_score = textstat.flesch_reading_ease(casView.sofa_string)
        #print('FLESCH_KINCAID: ' + str(readability_score))
        name = 'Readability_Score_Flesch_Kincaid_Lang_' + self.lang

        # write feature value in CAS
        T_FEATURE = 'org.lift.type.FeatureAnnotationNumeric'

        F = self.ts.get_type(T_FEATURE)
        feature = F(name=name, value=readability_score)
        cas.add(feature)

        return True


class FE_NounPhrasesPerSentence(FEL_AnnotationRatio):
    def __init__(self):
        super().__init__('de.tudarmstadt.ukp.dkpro.core.api.syntax.type.chunk.NC',
                         'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence')
        
class FE_TokensPerSentence(FEL_AnnotationRatio):
    def __init__(self):
        super().__init__('de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token',
                         'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence')

class FE_FleschIndex(FEL_ReadabilityScore):
    def __init__(self):
        super().__init__('de')

