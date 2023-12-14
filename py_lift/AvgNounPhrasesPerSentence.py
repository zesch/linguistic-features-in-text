import AnnotationRatio
from cassis import *

class AvgNounPhrasesPerSentence:
    def __init__(self, cas):
        self.cas = cas
        self.result = -1

    def extract(self) -> float:
        path_a = 'de.tudarmstadt.ukp.dkpro.core.api.syntax.type.chunk.NC/none'
        path_b = 'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence/none'
        ent_a = 'none'
        ent_b = 'none'
        self.result = AnnotationRatio.AnnotationRatio(path_a, path_b, ent_a, ent_b, self.cas).extract()

        return self.result
