from cassis import Cas

from util import load_typesystem as lt
from spellchecker import SpellChecker
from cassis.typesystem import TYPE_NAME_FS_ARRAY

T_TOKEN = 'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token'
T_ANOMALY = 'de.tudarmstadt.ukp.dkpro.core.api.anomaly.type.SpellingAnomaly'
T_SUGGESTION = 'de.tudarmstadt.ukp.dkpro.core.api.anomaly.type.SuggestedAction'

class SE_SpellErrorAnnotator:

    def __init__(self):
        self.ts = lt('data/TypeSystem.xml')
        self.spell = SpellChecker()
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