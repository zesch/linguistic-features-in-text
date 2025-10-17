from cassis import Cas

from util import load_lift_typesystem, supported_languages
from dkpro import T_TOKEN, T_POS, T_STRUCTURE
from abc import ABC
from annotators.api import SEL_BaseAnnotator

class SEL_ListReader(ABC):
    """Abstract class for reading lists."""

    def __init__(self, filename):
        self.filename = filename

    def read_list(self) -> set[str]:
        """Reads lines from a txt file and returns as a list (stripped of whitespace)."""
        with open(self.filename, 'r', encoding='utf-8') as f:
            return {line.strip() for line in f if line.strip()}
        
@supported_languages('de', 'en')
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
        