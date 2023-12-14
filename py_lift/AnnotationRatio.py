from cassis import *
import util


class AnnotationRatio:

    def __init__(self, path_a, path_b, ent_a, ent_b, cas):
        self.path_a = path_a
        self.path_b = path_b
        self.ent_a = ent_a
        self.ent_b = ent_b
        self.cas = cas
        self.result = -1



    def count(self, feat, typePath, cas, entity):
        size = 0
        for item in cas.select(typePath):
            if feat != 'none':
                if getattr(item, feat) == entity:
                    size += 1
            else:
                size += 1
        return size

    def extract(self):

        dividendPath, dividend = util.resolve_annotation(self.path_a)
        divisorPath, divisor = util.resolve_annotation(self.path_b)

        countDividend = self.count(dividend, dividendPath, self.cas, self.ent_a)
        countDivisor = self.count(divisor, divisorPath, self.cas, self.ent_b)

        self.result = countDividend / countDivisor
        return self.result


# def getAnnotationRatio(path_a, path_b, ent_a, ent_b, cas):
#
#     dividendPath, dividend = util.resolve_annotation(path_a)
#     divisorPath, divisor = util.resolve_annotation(path_b)
#
#     countDividend = count(dividend, dividendPath, cas, ent_a)
#     countDivisor = count(divisor, divisorPath, cas, ent_b)
#
#     finalRatio = countDividend / countDivisor
#     return finalRatio
#
#
# def count(feat, typePath, cas, entity):
#     size = 0
#     for item in cas.select(typePath):
#         if feat != 'none':
#             if getattr(item, feat) == entity:
#                 size += 1
#         else:
#             size += 1
#     return size
