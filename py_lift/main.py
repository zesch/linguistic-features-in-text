from cassis import *
import AnnotationRatio
import AvgTokenPerSentence
import AvgNounPhrasesPerSentence


file = 'data/1023_0001416.xmi'
pathFeature = "de.tudarmstadt.ukp.dkpro.core.api.metadata.type.MetaDataStringField"

with open('data/TypeSystem.xml', 'rb') as f:
    typesys = load_typesystem(f)

with open(file, 'rb') as f:
    cas = load_cas_from_xmi(f, typesystem=typesys)

path1 = 'de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS/PosValue'
ent1 = 'NN'
path2 = 'de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS/PosValue'
ent2 = 'ADV'
entity = 'PosValue'

print(AnnotationRatio.AnnotationRatio(path1, path2, ent1, ent2, cas).extract())
print(AvgTokenPerSentence.AvgTokenPerSentence(cas).extract())
print(AvgNounPhrasesPerSentence.AvgNounPhrasesPerSentence(cas).extract())
#print(AvgTokenPerSentence.Test(2,5).multi())

