from cassis import Cas

from util import load_typesystem
from spellchecker import SpellChecker
from cassis.typesystem import TYPE_NAME_FS_ARRAY
from dkpro import T_TOKEN, T_ANOMALY, T_SUGGESTION, T_LEMMA

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
                cas.add(suggested_action)
                anomaly = self.A(begin=token.begin, end=token.end, suggestions=self.FSArray(elements=[suggested_action])) 
                cas.add(anomaly)

        return True


class SE_EasyWordAnnotator():

    def __init__(self, language):
        self.language = language
        supported_langs = ['en']
        if self.language not in supported_langs:
            raise ValueError(
                f"{self.language} is not a supported language."
            )
        from pathlib import Path

        file_path = Path(
            __file__).parent.parent / "shared_resources" / "resources" / "easy_words" / "en_BNC_easy_words.txt"

        with file_path.open("r", encoding="utf-8") as f:
            self.easy_words = [line.strip() for line in f]


        self.ts = load_typesystem('data/TypeSystem.xml')
        self.easy = self.ts.get_type("org.lift.type.EasyWord")

    def process(self, cas: Cas) -> bool:
        for lemma in cas.select(T_LEMMA):
            t_str = lemma.value
            if t_str in self.easy_words:
                easy_word = self.easy(begin=lemma.begin, end=lemma.end)
                cas.add(easy_word)
                print("Found easy word: ", t_str)
            else:
                print("Found not so easy word: ", t_str)
        return True