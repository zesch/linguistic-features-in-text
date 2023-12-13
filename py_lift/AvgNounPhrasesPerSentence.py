import AnnotationRatio
from cassis import *


def getAvgNounPhrasesPerSentence(cas):
    path_a = 'de.tudarmstadt.ukp.dkpro.core.api.syntax.type.chunk.NC/none'
    path_b = 'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence/none'
    ent_a = 'none'
    ent_b = 'none'
    avgTokPerSen = AnnotationRatio.getAnnotationRatio(path_a, path_b, ent_a, ent_b, cas)

    return avgTokPerSen
