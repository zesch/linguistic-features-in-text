from cassis import Cas

from util import load_typesystem
from spellchecker import SpellChecker
from cassis.typesystem import TYPE_NAME_FS_ARRAY
from dkpro import T_TOKEN, T_ANOMALY, T_SUGGESTION

class SE_SpellErrorAnnotator():

    def __init__(self, language):
        self.language = language
        supported_langs = ['en', 'es', 'fr', 'pt', 'de', 'it', 'ru', 'ar', 'eu', 'lv', 'nl']
        if self.language not in supported_langs:
            raise ValueError(
                f"{self.language} is not a supported language."
            )
        self.spell = SpellChecker(language=self.language)
            
        self.ts = load_typesystem('data/TypeSystem.xml')
        
        self.A = self.ts.get_type(T_ANOMALY)
        self.S = self.ts.get_type(T_SUGGESTION)
        self.FSArray = self.ts.get_type(TYPE_NAME_FS_ARRAY)

    def process(self, cas: Cas) -> bool: 
        for token in cas.select(T_TOKEN):
            t_str = token.get_covered_text()
            if t_str in self.spell.unknown([t_str]):
                suggested_action = self.S(replacement=self.spell.correction(t_str), begin=token.begin, end=token.end)
                anomaly = self.A(begin=token.begin, end=token.end, suggestions=self.FSArray(elements=[suggested_action])) 
                cas.add(anomaly)

        return True