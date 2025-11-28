from cassis import Cas
from py_lift.decorators import supported_languages
from py_lift.dkpro import T_TOKEN, T_POS, T_STRUCTURE, T_LEMMA, T_SENT
from py_lift.annotators.api import SEL_BaseAnnotator
from pathlib import Path
from typing import Union, Set
import gzip
import zipfile
from py_lift.util import is_digits_or_punct, contains_punct_except_apostrophe

class SEL_ListReader:
    """Reader for text lists from plain text, gzip, or zip files."""
    
    def __init__(self, filename: Union[str, Path]):
        self.filename = Path(filename)
        if not self.filename.exists():
            raise FileNotFoundError(f"File not found: {self.filename}")
    
    def read_list(self) -> Set[str]:
        """
        Reads lines from a text file and returns as a set (stripped of whitespace).
        Supports .txt, .gz, and .zip files.
        """
        suffix = self.filename.suffix.lower()
        
        if suffix == '.gz':
            return self._read_gzip()
        elif suffix == '.zip':
            return self._read_zip()
        else:
            return self._read_plain()
    
    def _read_plain(self) -> Set[str]:
        with self.filename.open('r', encoding='utf-8') as f:
            return {line.strip() for line in f if line.strip()}
    
    def _read_gzip(self) -> Set[str]:
        with gzip.open(self.filename, 'rt', encoding='utf-8') as f:
            return {line.strip() for line in f if line.strip()}
    
    def _read_zip(self) -> Set[str]:
        with zipfile.ZipFile(self.filename) as zf:
            namelist = zf.namelist()
            if not namelist:
                raise ValueError(f"Zip file is empty: {self.filename}")
            
            # Read first text-like file
            name = namelist[0]
            with zf.open(name) as f:
                lines = (line.decode('utf-8').strip() for line in f)
                return {line for line in lines if line}
        
@supported_languages('de', 'en', 'sl')
class SE_FiniteVerbAnnotator(SEL_BaseAnnotator, SEL_ListReader):

    STRUCTURE_NAME = "FiniteVerb"

    def __init__(self, language):
        filename = self._get_filename_for_language(language)
        SEL_ListReader.__init__(self, filename)
        SEL_BaseAnnotator.__init__(self, language)
        self.S = self.ts.get_type(T_STRUCTURE)

    def _get_filename_for_language(self, language):
        lang_to_file = {
            'en': '../shared_resources/resources/finite_verb_postags/finite_verb_postags_en_ptb.txt',
            'de': '../shared_resources/resources/finite_verb_postags/finite_verb_postags_de_stts.txt',
            'sl': '../shared_resources/resources/finite_verb_postags/sl_MULText-East_finite_verb_postags.txt',
        }
        try:
            return lang_to_file[language]
        except KeyError:
            raise ValueError(f"No list file defined for language '{language}'.")

    def process(self, cas: Cas) -> bool:
        finite_verb_postags = self.read_list()
        for token in cas.select(T_TOKEN):
            t_pos = cas.select_covered(type_=T_POS, covering_annotation=token)[0]
            if t_pos.PosValue in finite_verb_postags:
                structure = self.S(
                    begin=token.get('begin'),
                    end=token.get('end'),
                    name=self.STRUCTURE_NAME
                )
                cas.add(structure)

        return True

@supported_languages('en')
class SE_EasyWordAnnotator(SEL_BaseAnnotator, SEL_ListReader):

    def __init__(self, language):
        filename = Path(__file__).parent.parent.parent.parent / "shared_resources" / "resources" / "easy_words" / "en_BNC_easy_words.txt"
        SEL_ListReader.__init__(self, filename)
        SEL_BaseAnnotator.__init__(self, language)

        self.EW = self.ts.get_type("org.lift.type.EasyWord")

    def process(self, cas: Cas) -> bool:
        for lemma in cas.select(T_LEMMA):
            l_str = lemma.value
            # TODO punctuation currently counted as not easy word
            if l_str in self.read_list():
                easy_word = self.EW(begin=lemma.get('begin'), end=lemma.get('end'))
                cas.add(easy_word)
                print("Found easy word: ", l_str)
            else:
                print("Found not so easy word: ", l_str)
        return True


@supported_languages('de')
class SE_OOV_Annotator(SEL_BaseAnnotator, SEL_ListReader):

    STRUCTURE_NAME = "OOV_Token"

    def __init__(self, language):
        SEL_ListReader.__init__(self, self._get_path_for_language(language))
        SEL_BaseAnnotator.__init__(self, language)
        self.S = self.ts.get_type(T_STRUCTURE)

    def _get_path_for_language(self, language) -> Path:
        lang_to_path = {
            'de': Path(__file__).parent.parent.parent.parent / "shared_resources" / "resources" / "lift_resources_lists" / "lift_resources_lists" / "full_form" / "hunspell_dict_de.txt.zip"
        }
        try:
            return lang_to_path[language]
        except KeyError:
            raise ValueError(f"No list file defined for language '{language}'.")

    def _uppercase_at_sentence_start(self, token, cas):
        """Check if token is at the beginning of a sentence and starts with uppercase."""
        for sentence in cas.select(T_SENT):
            if token.begin == sentence.begin:
                return token.get_covered_text().isupper()
        return False

    def process(self, cas: Cas) -> bool:

        # store all sentence start offsets to speed up checks
        sentence_starts = {sentence.begin for sentence in cas.select(T_SENT)}

        known_tokens = self.read_list()
        for token in cas.select(T_TOKEN):
            token_text = token.get_covered_text()
            
            # single letter tokens are not considered OOV
            if len(token_text) < 2:
                continue

            # tokens only containing digits or punctuation are not considered OOV
            if is_digits_or_punct(token_text):
                continue

            # tokens containing punctuation (except apostrophes) are not considered OOV
            if contains_punct_except_apostrophe(token_text):
                continue

            # lowercase token if it is at the beginning of a sentence
            if token.begin in sentence_starts and token_text[:1].isupper():
                if token_text in known_tokens:
                    continue # do not lower case known tokens
                token_text = token_text.lower()                

            if token_text not in known_tokens:
                print(token.get_covered_text())
                feature = self.S(name=self.STRUCTURE_NAME, begin=token.begin, end=token.end)
                cas.add(feature)

        return True