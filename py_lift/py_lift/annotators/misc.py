from cassis import Cas
from cassis.typesystem import TypeNotFoundError

from py_lift.decorators import supported_languages
from py_lift.util import load_lift_typesystem, read_tsv_to_dict
from spellchecker import SpellChecker
from cassis.typesystem import TYPE_NAME_FS_ARRAY
from py_lift.dkpro import T_TOKEN, T_ANOMALY, T_SUGGESTION, T_LEMMA, T_POS, T_RWSE, T_SENT
from py_lift.annotators.api import SEL_BaseAnnotator
from rwse_checker import rwse
from pathlib import Path
from typing import Union, List

import polars as pl

@supported_languages('en', 'es', 'fr', 'pt', 'de', 'it', 'ru', 'ar', 'eu', 'lv', 'nl')
class SE_SpellErrorAnnotator(SEL_BaseAnnotator):

    def __init__(self, language, ts=None):
        super().__init__(language, ts)
        self.spell = SpellChecker(language=self.language, case_sensitive=True)
                
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

@supported_languages('de', 'en')
class SE_AbstractnessAnnotator(SEL_BaseAnnotator):

    def __init__(self, language, ts=None):
        super().__init__(language, ts)

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
    """TODO ADD DOCUMENTATION."""

    def __init__(self, language, ts=None):
        super().__init__(language, ts)

        file_path = Path(
            __file__).parent.parent.parent.parent / "shared_resources" / "resources" / "evp" / "EVP.csv"

        df = pl.read_csv(file_path)
        df = df.unique(subset=['word', 'pos'])

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
        self.T_evp_cefr = self.ts.get_type("org.lift.type.EvpCefr")

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
                        cefr_word = self.T_evp_cefr(begin=lemma.begin, end=lemma.end, level=word_dict[our_pos_value], pos=our_pos_value)
                        cas.add(cefr_word)
                    else:
                        # Take pos with lowest level
                        cefr_word = self.T_evp_cefr(begin=lemma.begin, end=lemma.end, level=min(word_dict.values()), pos=min(word_dict, key=word_dict.get))
                        cas.add(cefr_word)
                else:
                    cefr_word = self.T_evp_cefr(begin=lemma.begin, end=lemma.end, level=list(self.evp_cefr_words[t_str].values())[0], pos=list(self.evp_cefr_words[t_str].keys())[0])
                    cas.add(cefr_word)

        return True
    
@supported_languages('de')
class SE_CoarsePosTagAnnotator(SEL_BaseAnnotator):
    """ Takes fine grained POS tags and maps them to coarse grained ones based on a mapping file.
    Add the coarse grained POS tag as new annotation type.
    Remove the old POS tag anotation.
    """

    def __init__(self, language, mapping: str, remove_old: bool = True, ts=None):
        super().__init__(language, ts)
        self.pmap = self.read_pos_mapping(mapping)
        self.remove_old = remove_old

    def read_pos_mapping(self, mapping) -> dict:
        pmap = {}
        filename = Path(__file__).parent.parent / "data" / "pos_maps" / f"{mapping}.map"
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    pmap[key.strip()] = value.strip()
        return pmap

    def process(self, cas: Cas) -> bool:

        for pos in cas.select(T_POS):
            fine_tag = pos.get('PosValue')

            # if fine_tag not in self.pos_mapping, default to '*'
            if fine_tag not in self.pmap:
                # TODO proper logging?
                print(f"Warning: fine grained POS tag '{fine_tag}' not found in mapping. Using '*' as coarse tag.")
                fine_tag = "*"

            coarse_tag = self.pmap.get(fine_tag)
            T = cas.typesystem.get_type(self.pmap['__META_TYPE_BASE__'] + coarse_tag)
            anno = T(begin=pos.begin, end=pos.end, PosValue=fine_tag)
            cas.add(anno)
            if self.remove_old:
                cas.remove(pos)

        return True

class SE_RWSE_Annotator(SEL_BaseAnnotator):
    """
        Checks all tokens in all sentences of the CAS object,
        suggests corrections using fill-mask if necessary,
        and adds RWSE annotations to the CAS.
    """
    
    def __init__(self, model_name, confusion_sets: Union[str, Path, List[List[str]]], magnitude: int = 10, case_sensitive=False, ts=None):
        super().__init__(ts)
        self.checker = rwse.RWSE_Checker(
            confusion_sets=confusion_sets, 
            model_name=model_name,
            case_sensitive=case_sensitive
        )
        self.magnitude = magnitude
    
    def process(self, cas: Cas) -> bool:
        RWSE = self.ts.get_type(T_RWSE)

        # Iterate over sentences
        for sentence in cas.select(T_SENT):
            tokens = list(cas.select_covered(T_TOKEN, sentence))
            for i, token in enumerate(tokens):
                token_str = token.get_covered_text()
                if (self.checker.in_confusion_sets(token_str)):
                    text_str = cas.sofa_string

                    begin = tokens[i].begin
                    end = tokens[i].end

                    prefix = text_str[:begin]
                    suffix = text_str[end:]

                    # Ensure proper spacing around mask token
                    masked_sentence = f"{prefix.rstrip()} {rwse.MASK} {suffix.lstrip()}"

                    corrected, certainty, _ = self.checker.correct(token_str, masked_sentence, self.magnitude)

                    # if correction suggested (case-insensitive comparison)
                    if token_str.lower() != corrected.lower():
                        # create new RWSE annotation
                        anno = RWSE(
                            begin=token.begin,
                            end=token.end,
                            suggestion=corrected,
                            certainty=certainty
                        )
                        cas.add(anno)

        return True