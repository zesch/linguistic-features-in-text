from cassis import Cas

class FEL_AnnotationRatio:

    def __init__(self, type_dividend, type_divisor):
        self.dividend_type = type_dividend
        self.divisor_type = type_divisor

    def count(self, cas, type):
        size = 0
        for anno in cas.select(type):
            size += 1
        return size

    def extract(self, cas: Cas):

        count_dividend = self.count(cas, self.dividend_type)
        count_divisor = self.count(cas, self.divisor_type)

        # TODO catch division by zero
        ratio = count_dividend / count_divisor

        return ratio

class FE_NounPhrasesPerSentence(FEL_AnnotationRatio):

    def extract(cas: Cas) -> float:
        return super.extract('de.tudarmstadt.ukp.dkpro.core.api.syntax.type.chunk.NC',
                             'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence')
        
class FE_TokensPerSentence(FEL_AnnotationRatio):

    def extract(cas: Cas) -> float:
        return super.extract('de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token',
                             'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence')
