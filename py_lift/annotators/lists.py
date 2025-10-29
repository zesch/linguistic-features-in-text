from cassis import Cas

from util import load_lift_typesystem, supported_languages
from dkpro import T_TOKEN, T_POS, T_STRUCTURE, T_LEMMA
from abc import ABC
from annotators.api import SEL_BaseAnnotator
from pathlib import Path
from typing import Union, Set

class SEL_ListReader(ABC):
    """Abstract class for reading lists."""

    def __init__(self, filename: Union[str, Path]):
        self.filename: Path = Path(filename)

    def read_list(self) -> Set[str]:
        """
        Reads lines from a txt file and returns as a set (stripped of whitespace).
        """
        with self.filename.open('r', encoding='utf-8') as f:
            return {line.strip() for line in f if line.strip()}
        
@supported_languages('de', 'en', 'sl')
class SE_FiniteVerbAnnotator(SEL_BaseAnnotator, SEL_ListReader):

    STRUCTURE_NAME = "FiniteVerb"

    def __init__(self, language):
        self.language = language
        filename = self._get_filename_for_language(language)
        SEL_ListReader.__init__(self, filename)
        self.S = load_lift_typesystem().get_type(T_STRUCTURE)

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
        self.language = language
        filename = Path(__file__).parent.parent.parent / "shared_resources" / "resources" / "easy_words" / "en_BNC_easy_words.txt"
        SEL_ListReader.__init__(self, filename)

        # TODO language check should be in base class to avoid code duplication
        if self.language not in self.supported_languages:
            raise ValueError(
                f"{self.language} is not a supported language."
            )

        self.EW = load_lift_typesystem().get_type("org.lift.type.EasyWord")

    def process(self, cas: Cas) -> bool:
        for lemma in cas.select(T_LEMMA):
            l_str = lemma.value
            if l_str in self.read_list():
                easy_word = self.EW(begin=lemma.get('begin'), end=lemma.get('end'))
                cas.add(easy_word)
                print("Found easy word: ", l_str)
            else:
                print("Found not so easy word: ", l_str)
        return True