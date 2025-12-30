from cassis import Cas
from py_lift.decorators import supported_languages
from py_lift.dkpro import T_FEATURE
from textstat import textstat
from py_lift.extractors import FEL_BaseExtractor
from abc import abstractmethod
from typing import Callable

class FEL_ReadabilityScore(FEL_BaseExtractor):
    supported_languages: set[str] = set()
    
    def __init__(self, language):
        self.language: str = language
        if hasattr(self, 'supported_languages'):
            if self.language not in self.supported_languages:
                raise ValueError(
                    f"{self.language} is not a supported language."
                )

    @abstractmethod
    def score(self, text: str) -> float:
        pass

    @abstractmethod
    def name(self) -> str:
        pass

    def extract(self, cas: Cas) -> bool:
        readability_score = self.score(cas.sofa_string)

        feature_name = self.name() + '_' + self.language

        F = cas.typesystem.get_type(T_FEATURE)
        feature = F(name=feature_name, value=readability_score, begin=0, end=0)
        cas.add(feature)

        return True 

class FEL_TextstatReadabilityScore(FEL_ReadabilityScore):
    def __init__(self, language, score_func, name, **kwargs):
        super().__init__(language, **kwargs)
        self._score_func: Callable[..., float] = score_func
        self._name: str = name

    def name(self):
        return self._name

    def score(self, text: str) -> float:
        return self._score_func(text)

@supported_languages('en', 'de', 'es', 'fr', 'it', 'nl', 'ru')
class FE_TextstatFleschIndex(FEL_TextstatReadabilityScore):
    def __init__(self, language):
        super().__init__(
            language,
            textstat.flesch_reading_ease,
            'Readability_Score_FleschKincaid',
        )

@supported_languages('en', 'pl')
class FE_TextstatGunningFog(FEL_TextstatReadabilityScore):
    def __init__(self, language, **kwargs):
        super().__init__(
            language,
            textstat.gunning_fog,
            'Readability_Score_GunningFog',
            **kwargs
        )

@supported_languages('en')
class FE_TextstatFleschKincaidGrade(FEL_TextstatReadabilityScore):
    def __init__(self, language, **kwargs):
        super().__init__(
            language,
            textstat.flesch_kincaid_grade,
            'Readability_Score_FleschKincaidGrade',
            **kwargs
        )
@supported_languages('en')
class FE_TextstatSmogIndex(FEL_TextstatReadabilityScore):
    def __init__(self, language, **kwargs):
        super().__init__(
            language,
            textstat.smog_index,
            'Readability_Score_SmogIndex',
            **kwargs
        )  
@supported_languages('en')
class FE_TextstatAutomatedReadabilityIndex(FEL_TextstatReadabilityScore):
    def __init__(self, language, **kwargs):
        super().__init__(
            language,
            textstat.automated_readability_index,
            'Readability_Score_AutomatedReadabilityIndex',
            **kwargs
        )

@supported_languages('en')
class FE_TextstatColemanLiauIndex(FEL_TextstatReadabilityScore):
    def __init__(self, language, **kwargs):
        super().__init__(
            language,
            textstat.coleman_liau_index,
            'Readability_Score_ColemanLiauIndex',
            **kwargs
        )
@supported_languages('en')
class FE_TextstatLinsearWriteFormula(FEL_TextstatReadabilityScore):
    def __init__(self, language, **kwargs):
        super().__init__(
            language,
            textstat.linsear_write_formula,
            'Readability_Score_LinsearWriteFormula',
            **kwargs
        )

@supported_languages('en')
class FE_TextstatDaleChallReadabilityScore(FEL_TextstatReadabilityScore):
    def __init__(self, language, **kwargs):
        super().__init__(
            language,
            textstat.dale_chall_readability_score,
            'Readability_Score_DaleChallReadabilityScore',
            **kwargs
        )

@supported_languages('en')
class FE_TextstatSpacheReadability(FEL_TextstatReadabilityScore):
    def __init__(self, language, **kwargs):
        super().__init__(
            language,
            textstat.spache_readability,
            'Readability_Score_SpacheReadability',
            **kwargs
        )

@supported_languages('en')
class FE_TextstatMcAlpineEFLAW(FEL_TextstatReadabilityScore):
    def __init__(self, language, **kwargs):
        super().__init__(
            language,
            textstat.mcalpine_eflaw,
            'Readability_Score_McAlpineEFLAW',
            **kwargs
        )
@supported_languages('es')
class FE_TextstatFernandezHuerta(FEL_TextstatReadabilityScore):
    def __init__(self, language, **kwargs):
        super().__init__(
            language,
            textstat.fernandez_huerta,
            'Readability_Score_FernandezHuerta',
            **kwargs
        )

@supported_languages('es')
class FE_TextstatSzigrisztPazos(FEL_TextstatReadabilityScore):
    def __init__(self, language, **kwargs):
        super().__init__(
            language,
            textstat.szigriszt_pazos,
            'Readability_Score_SzigrisztPazos',
            **kwargs
        )
    
@supported_languages('es')
class FE_TextstatGutierrezPolini(FEL_TextstatReadabilityScore):
    def __init__(self, language, **kwargs):
        super().__init__(
            language,
            textstat.gutierrez_polini,
            'Readability_Score_GutierrezPolini',
            **kwargs
        )

@supported_languages('es')
class FE_TextstatCrawford(FEL_TextstatReadabilityScore):
    def __init__(self, language, **kwargs):
        super().__init__(
            language,
            textstat.crawford,
            'Readability_Score_Crawford',
            **kwargs
        )

@supported_languages('ar')
class FE_TextstatOsman(FEL_TextstatReadabilityScore):
    def __init__(self, language, **kwargs):
        super().__init__(
            language,
            textstat.osman,
            'Readability_Score_Osman',
            **kwargs
        )
 
@supported_languages('it')
class FE_TextstatGulpeaseIndex(FEL_TextstatReadabilityScore):
    def __init__(self, language, **kwargs):
        super().__init__(
            language,
            textstat.gulpease_index,
            'Readability_Score_GulpeaseIndex',
            **kwargs
        )

@supported_languages('de')
class FE_TextstatWienerSachtextformel_1(FEL_TextstatReadabilityScore):
    def __init__(self, **kwargs):
        super().__init__(
            'de',
            textstat.wiener_sachtextformel,
            'Readability_Score_WienerSachtextformel-1',
            **kwargs
        )

    # override to pass variant parameter
    def score(self, text: str) -> float:
        return self._score_func(text, 1)