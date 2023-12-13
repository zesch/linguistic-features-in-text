from cassis import *

def getAnnotationRatio(path_a, path_b, ent_a, ent_b, cas):
    split_a = path_a.split('/')
    type_a = split_a[0]
    feat_a = split_a[1]

    split_b = path_b.split('/')
    type_b = split_b[0]
    feat_b = split_b[1]

    divident = feat_a
    divisor = feat_b

    dividentPath = type_a
    divisorPath = type_b

    countDivident = count(divident, dividentPath, cas, ent_a)
    countDivisor = count(divisor, divisorPath, cas, ent_b)

    finalRatio = countDivident / countDivisor
    return finalRatio


def count(feat, typePath, cas, entity):
    size = 0
    for item in cas.select(typePath):
        if feat != 'none':
            if getattr(item, feat) == entity:
                size += 1
        else:
            size += 1
    return size
