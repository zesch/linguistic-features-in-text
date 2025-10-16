from cassis import Cas

from util import load_lift_typesystem, read_tsv_to_dict, supported_languages
from spellchecker import SpellChecker
from cassis.typesystem import TYPE_NAME_FS_ARRAY
from dkpro import T_TOKEN, T_ANOMALY, T_SUGGESTION, T_LEMMA, T_POS
from abc import ABC, abstractmethod

# TODO switch to polars?
import pandas as pd

class SEL_BaseAnnotator(ABC):
    """Marker base class for all annotators."""
    
    @abstractmethod
    def process(self, cas: Cas) -> bool:
        pass

@supported_languages('en', 'es', 'fr', 'pt', 'de', 'it', 'ru', 'ar', 'eu', 'lv', 'nl')
class SE_SpellErrorAnnotator(SEL_BaseAnnotator):

    def __init__(self, language):
        self.language = language
        if self.language not in self.supported_languages:
            raise ValueError(
                f"{self.language} is not a supported language."
            )
        self.spell = SpellChecker(language=self.language, case_sensitive=True)
            
        self.ts = load_lift_typesystem()
        
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


@supported_languages('en')
class SE_EasyWordAnnotator(SEL_BaseAnnotator):

    def __init__(self, language):
        self.language = language
        if self.language not in self.supported_languages:
            raise ValueError(
                f"{self.language} is not a supported language."
            )
        from pathlib import Path

        file_path = Path(
            __file__).parent.parent / "shared_resources" / "resources" / "easy_words" / "en_BNC_easy_words.txt"

        with file_path.open("r", encoding="utf-8") as f:
            self.easy_words = [line.strip() for line in f]

        self.ts = load_lift_typesystem()
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

@supported_languages('de', 'en')
class SE_AbstractnessAnnotator(SEL_BaseAnnotator):

    def __init__(self, language):
        self.language = language
        if self.language not in self.supported_languages:
            raise ValueError(
                f"{self.language} is not a supported language."
            )
        from pathlib import Path

        # file_path = Path(
        #     __file__).parent.parent / "shared_resources" / "resources" / "abstractness" / self.language / "ratings_lrec16_koeper_ssiw.txt"

        # self.data_dict = read_tsv_to_dict(file_path, 'Word', 'AbstConc')

        from importlib.resources import files
        import lift_resources_lists
        
        # Access a specific file
        data_dir = files('lift_resources_lists').joinpath('abstractness').joinpath(self.language)
        model_path = data_dir / 'ratings_lrec16_koeper_ssiw.txt'
        print(model_path)

        self.data_dict = read_tsv_to_dict(model_path, 'Word', 'AbstConc')        

        self.ts = load_lift_typesystem()
        self.AC = self.ts.get_type("org.lift.type.AbstractnessConcreteness")

    def process(self, cas: Cas) -> bool:
        for lemma in cas.select(T_LEMMA):
            l_str = lemma.value
            if l_str in self.data_dict:
                anno = self.AC(begin=lemma.get('begin'), end=lemma.get('end'), value=self.data_dict[l_str])
                cas.add(anno)
        return True

@supported_languages('en')
class SE_EvpCefrAnnotator(SEL_BaseAnnotator):
    """ADD DOCUMENTATION."""

    def __init__(self, language):
        self.language = language
        if self.language not in self.supported_languages:
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

        self.evp_cefr_words = cefr_words
        self.ts = load_lift_typesystem()
        self.evp_cefr = self.ts.get_type("org.lift.type.EvpCefr")

    def process(self, cas: Cas) -> bool:
        for lemma in cas.select(T_LEMMA):
            t_str = lemma.value

            if t_str in self.evp_cefr_words.keys():
                if len(self.evp_cefr_words[t_str]) > 1:
                    word_dict = self.evp_cefr_words[t_str]

                    t_pos = cas.select_covered(type_=T_POS, covering_annotation=lemma)[0]
                    pos_value = t_pos.PosValue
                    our_pos_value = self.pos_tag_map[pos_value]

                    if our_pos_value in word_dict.keys():
                        cefr_word = self.evp_cefr(begin=lemma.begin, end=lemma.end, level=word_dict[our_pos_value], pos=our_pos_value)
                        cas.add(cefr_word)
                    else:
                        # Take pos with lowest level
                        cefr_word = self.evp_cefr(begin=lemma.begin, end=lemma.end, level=min(word_dict.values()), pos=min(word_dict, key=word_dict.get))
                        cas.add(cefr_word)
                else:
                    cefr_word = self.evp_cefr(begin=lemma.begin, end=lemma.end, level=list(self.evp_cefr_words[t_str].values())[0], pos=list(self.evp_cefr_words[t_str].keys())[0])
                    cas.add(cefr_word)

                print("Found evp cefr word: ", t_str)
            else:
                print("Found not so evp cefr word: ", t_str)

        return True