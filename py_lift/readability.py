from cassis import Cas
from util import load_typesystem
from textstat import *

class FEL_ReadabilityScore:
    def __init__(self, language):
        self.ts = load_typesystem('data/TypeSystem.xml')
        self.language = language

    def extract(self, cas: Cas) -> bool:
        textstat.set_lang(self.language)
        readability_score = textstat.flesch_reading_ease(cas.sofa_string)

        name = 'Readability_Score_Flesch_Kincaid_Lang_' + self.language

        T_FEATURE = 'org.lift.type.FeatureAnnotationNumeric'

        F = self.ts.get_type(T_FEATURE)
        feature = F(name=name, value=readability_score)
        cas.add(feature)

        return True


class FE_FleschIndex(FEL_ReadabilityScore):
    def __init__(self):
        super().__init__('de')
