from cassis import Cas

from util import load_typesystem as lt
from spellchecker import SpellChecker



class FEL_AnnotationRatio:

    def __init__(self, type_dividend, type_divisor):
        self.ts = lt('data/TypeSystem.xml')
        self.dividend_type = type_dividend
        self.divisor_type = type_divisor

    def count(self, cas, type):
        size = 0
        for anno in cas.select(type):
            size += 1
        return size

    def extract(self, cas: Cas) -> bool:
        count_dividend = self.count(cas, self.dividend_type)
        count_divisor = self.count(cas, self.divisor_type)

        # TODO catch division by zero
        ratio = count_dividend / count_divisor

        name = self.dividend_type + '_PER_' + self.divisor_type

        # write feature value in CAS
        T_FEATURE = 'org.lift.type.FeatureAnnotationNumeric'

        F = self.ts.get_type(T_FEATURE)
        feature = F(name=name, value=ratio)
        cas.add(feature)

        return True

class FE_NounPhrasesPerSentence(FEL_AnnotationRatio):
    def __init__(self):
        super().__init__('de.tudarmstadt.ukp.dkpro.core.api.syntax.type.chunk.NC',
                         'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence')
        
class FE_TokensPerSentence(FEL_AnnotationRatio):
    def __init__(self):
        super().__init__('de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token',
                         'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence')




class SE_SpellErrorAnnotator:

    def __init__(self):
        self.ts = lt('data/TypeSystem.xml')
        self.spell = SpellChecker()
        T_ANNOTATION = 'de.tudarmstadt.ukp.dkpro.core.api.anomaly.type.SpellingAnomaly'
        S_SUGGESTION = 'de.tudarmstadt.ukp.dkpro.core.api.anomaly.type.SuggestedAction'
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

