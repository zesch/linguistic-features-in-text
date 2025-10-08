from cassis import Cas
from util import load_lift_typesystem
from textstat import textstat

class FEL_ReadabilityScore:
    def __init__(self, language):
        self.ts = load_lift_typesystem()
        self.language = language

    def extract(self, cas: Cas) -> bool:
        textstat.set_lang(self.language)
        readability_score = textstat.flesch_reading_ease(cas.sofa_string)

        name = 'Readability_Score_Flesch_Kincaid_Lang_' + self.language

        T_FEATURE = 'org.lift.type.FeatureAnnotationNumeric'

        F = self.ts.get_type(T_FEATURE)
        feature = F(name=name, value=readability_score, begin=0, end=0)
        cas.add(feature)

        return True


class FE_FleschIndex(FEL_ReadabilityScore):
    def __init__(self):
        super().__init__('de')
