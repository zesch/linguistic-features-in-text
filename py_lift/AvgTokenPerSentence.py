import AnnotationRatio
from cassis import *


def getAvgTokenPerSentence(cas):
    path_a = 'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token/none'
    path_b = 'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence/none'
    ent_a = 'none'
    ent_b = 'none'
    avgTokPerSen = AnnotationRatio.getAnnotationRatio(path_a, path_b, ent_a, ent_b, cas)

    return avgTokPerSen
