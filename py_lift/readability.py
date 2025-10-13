from cassis import Cas
from util import load_lift_typesystem, supported_languages
from textstat import textstat
from extractors import FEL_BaseExtractor
from abc import abstractmethod

# TODO expose the remaining measures for english and spanish
class FEL_TextstatReadabilityScore(FEL_BaseExtractor):
    def __init__(self, language):
        self.ts = load_lift_typesystem()
        self.language = language

    @abstractmethod
    def score(self, text: str) -> float:
        pass

    @abstractmethod
    def name(self) -> str:
        pass

    def extract(self, cas: Cas) -> bool:
        textstat.set_lang(self.language)
        readability_score = self.score(cas.sofa_string)

        feature_name = self.name() + '_' + self.language

        T_FEATURE = 'org.lift.type.FeatureAnnotationNumeric'

        F = self.ts.get_type(T_FEATURE)
        feature = F(name=feature_name, value=readability_score, begin=0, end=0)
        cas.add(feature)

        return True

@supported_languages('en', 'de', 'es', 'fr', 'it', 'nl', 'ru')
class FE_TextstatFleschIndex(FEL_TextstatReadabilityScore):
    def __init__(self, language):
        if language not in self.supported_languages:
            raise ValueError(
                f"{self.language} is not a supported language."
            )
        super().__init__(language)

    def name(self):
        return 'Readability_Score_Flesch_Kincaid'
    
    def score(self, text: str) -> float:
        return textstat.flesch_reading_ease(text)

@supported_languages('en', 'pl')
class FE_TextstatGunningFog(FEL_TextstatReadabilityScore):
    def __init__(self, language):
        if language not in self.supported_languages:
            raise ValueError(
                f"{self.language} is not a supported language."
            )
        super().__init__(language)

    def name(self):
        return 'Readability_Score_Gunning_Fog'
    
    def score(self, text: str) -> float:
        return textstat.gunning_fog(text)