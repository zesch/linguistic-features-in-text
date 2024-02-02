from cassis import Cas
from util import load_typesystem
from textstat import *

class FEL_ReadabilityScore:
    def __init__(self, lang):
        self.ts = load_typesystem('data/TypeSystem.xml')
        self.lang = lang

    def extract(self, cas: Cas) -> bool:
        textstat.set_lang(self.lang)
        readability_score = textstat.flesch_reading_ease(cas.sofa_string)
        #print('FLESCH_KINCAID: ' + str(readability_score))
        name = 'Readability_Score_Flesch_Kincaid_Lang_' + self.lang

        # write feature value in CAS
        T_FEATURE = 'org.lift.type.FeatureAnnotationNumeric'

        F = self.ts.get_type(T_FEATURE)
        feature = F(name=name, value=readability_score)
        cas.add(feature)

        return True


class FE_FleschIndex(FEL_ReadabilityScore):
    def __init__(self):
        super().__init__('de')
