from cassis import Cas

from util import load_lift_typesystem
from spellchecker import SpellChecker
from cassis.typesystem import TYPE_NAME_FS_ARRAY
from dkpro import T_TOKEN, T_ANOMALY, T_SUGGESTION, T_LEMMA, T_POS

# TODO switch to polars?
import pandas as pd

class SE_SpellErrorAnnotator():

    def __init__(self, language):
        self.language = language
        supported_langs = ['en', 'es', 'fr', 'pt', 'de', 'it', 'ru', 'ar', 'eu', 'lv', 'nl']
        if self.language not in supported_langs:
            raise ValueError(
                f"{self.language} is not a supported language."
            )
        self.spell = SpellChecker(language=self.language)
            
        self.ts = load_lift_typesystem('data/TypeSystem.xml')
        
        self.A = self.ts.get_type(T_ANOMALY)
        self.S = self.ts.get_type(T_SUGGESTION)
        self.FSArray = self.ts.get_type(TYPE_NAME_FS_ARRAY)

    def process(self, cas: Cas) -> bool: 
        for token in cas.select(T_TOKEN):
            t_str = token.get_covered_text()
            if t_str in self.spell.unknown([t_str]):
                suggested_action = self.S(
                    replacement=self.spell.correction(t_str),
                    begin=token.get('begin'),
                    end=token.get('end')
                )
                cas.add(suggested_action)
                anomaly = self.A(
                    begin=token.get('begin'),
                    end=token.get('end'), 
                    suggestions=self.FSArray(elements=[suggested_action])
                ) 
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

        self.ts = load_lift_typesystem('data/TypeSystem.xml')
        self.EW = self.ts.get_type("org.lift.type.EasyWord")

    def process(self, cas: Cas) -> bool:
        for lemma in cas.select(T_LEMMA):
            t_str = lemma.value
            if t_str in self.easy_words:
                easy_word = self.EW(begin=lemma.get('begin'), end=lemma.get('end'))
                cas.add(easy_word)
                print("Found easy word: ", t_str)
            else:
                print("Found not so easy word: ", t_str)
        return True


class SE_CEFRAnnotator():
    """ADD DOCUMENTATION."""
    
    def __init__(self, language):
        self.language = language
        supported_langs = ['en']
        if self.language not in supported_langs:
            raise ValueError(
                f"{self.language} is not a supported language."
            )
        from pathlib import Path

        file_path = Path(
            __file__).parent.parent / "shared_resources" / "resources" / "evp" / "EVP.csv"

        df = pd.read_csv(file_path)
        df.columns = ['word', 'pos', 'level']
        df = df.drop_duplicates(subset=['word', 'pos'], keep='first')

        self.pos_tag_map = {

            'CC': 'none',
            'CD': 'none',
            'DT': 'determiner',
            'EX': 'adverb',
            'FW': 'none',
            'IN': 'preposition',
            'JJ': 'adjective',
            'JJR': 'adjective',
            'JJS': 'adjective',
            'LS': 'none',
            'MD': 'verb',
            'NN': 'noun',
            'NNS': 'noun',
            'NNP': 'noun',
            'NNPS': 'noun',
            'PDT': 'determiner',
            'POS': 'none',
            'PRP': 'pronoun',
            'PRP$': 'pronoun',
            'RB': 'adverb',
            'RBR': 'adverb',
            'RBS': 'adverb',
            'RP': 'none',
            'SYM': 'none',
            'TO': 'none',
            'UH': 'none',
            'VB': 'verb',
            'VBD': "verb", 
            "VBG": "verb", 
            "VBN": "verb", 
            "VBP":"verb", 
            "VBZ": "verb", 
            "WDT": "determiner", 
            "WP": "pronoun", 
            "WP$": "determiner", 
            "WRB": "adverb"
        }

        # TODO: Move pos info to keys of dictionary?
        #self.cefr_words = {(word, pos): level for word, pos, level in zip(df['word'], df['pos'], df['level'])}

        cefr_words = {}
        for word, pos, level in zip(df['word'], df['pos'], df['level']):

            word_dict = cefr_words.get(word, {})
            word_dict[pos] = level
            cefr_words[word] = word_dict

        self.cefr_words = cefr_words
        self.ts = load_lift_typesystem('data/TypeSystem.xml')
        self.cefr = self.ts.get_type("org.lift.type.CEFR")

    def process(self, cas: Cas) -> bool:
        for lemma in cas.select(T_LEMMA):
            l_str = lemma.value

            if l_str not in self.cefr_words.keys():
                continue

            if len(self.cefr_words[l_str]) > 1:

                word_dict = self.cefr_words[l_str]

                t_pos = cas.select_covered(T_POS, lemma)[0]
                pos_value = str(t_pos.get('PosValue'))
                our_pos_value = self.pos_tag_map[pos_value]

                if our_pos_value in word_dict.keys():
                    cefr_word = self.cefr(
                        begin=lemma.get('begin'), 
                        end=lemma.get('end'), 
                        level=word_dict[our_pos_value], 
                        pos=our_pos_value
                    )
                    cas.add(cefr_word)

                else:
                    # Take pos with lowest level
                    cefr_word = self.cefr(
                        begin=lemma.get('begin'), 
                        end=lemma.get('end'), 
                        level=min(word_dict.values()), 
                        pos=min(word_dict, key=word_dict.get)
                    )
                    cas.add(cefr_word)

            else:
                cefr_word = self.cefr(
                    begin=lemma.get('begin'), 
                    end=lemma.get('end'), 
                    level=list(self.cefr_words[l_str].values())[0],
                    pos=list(self.cefr_words[l_str].keys())[0]
                )
                cas.add(cefr_word)

        return True