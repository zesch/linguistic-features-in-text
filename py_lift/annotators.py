from cassis import Cas

from util import load_typesystem as lt
from spellchecker import SpellChecker

T_ANNOTATION = 'de.tudarmstadt.ukp.dkpro.core.api.anomaly.type.SpellingAnomaly'
S_SUGGESTION = 'de.tudarmstadt.ukp.dkpro.core.api.anomaly.type.SuggestedAction'

class SE_SpellErrorAnnotator:

    def __init__(self):
        self.ts = lt('data/TypeSystem.xml')
        self.spell = SpellChecker()
        self.A = self.ts.get_type(T_ANNOTATION)
        self.S = self.ts.get_type(S_SUGGESTION)

    def process(self, cas: Cas) -> bool: 
        #for sentence in cas.select('de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence'):
        for token in cas.select('de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token'):
            if token.get_covered_text() in self.spell.unknown([token.get_covered_text()]):
                annotation = self.A(begin=token.begin, end=token.end) 
                suggested_action = self.S(replacement=self.spell.correction(token.get_covered_text()), begin=token.begin, end=token.end)
                cas.add(annotation)
                cas.add(suggested_action)

        return True
