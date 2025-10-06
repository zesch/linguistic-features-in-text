from cassis import Cas
from util import load_lift_typesystem
from wordfreq import zipf_frequency
from dkpro import T_TOKEN

class SE_WordFrequency:

    def __init__(self, language):
        self.ts = load_lift_typesystem('data/TypeSystem.xml')
        self.language = language

    def process(self, cas: Cas) -> bool:
        #         1  2  3  4  5  6  7 oov
        counts = [0, 0, 0, 0, 0, 0, 0, 0]

        for token in cas.select(T_TOKEN):
            freq= zipf_frequency(token.get_covered_text(), self.language)
            if 2 > freq > 0:
                fb = 'f1'
                counts[0] += 1
            elif 3 > freq >= 2:
                fb = 'f2'
                counts[1] += 1
            elif 4 > freq >= 3:
                fb = 'f3'
                counts[2] += 1
            elif 5 > freq >= 4:
                fb = 'f4'
                counts[3] += 1
            elif 6 > freq >= 5:
                fb = 'f5'
                counts[4] += 1
            elif 7 > freq >= 6:
                fb = 'f6'
                counts[5] += 1
            elif freq >= 7:
                fb = 'f7'
                counts[6] += 1
            elif freq == 0:
                fb = 'oov'
                counts[7] += 1

            F = self.ts.get_type("org.lift.type.Frequency")
            feature = F(begin=token.begin, end=token.end, value=freq, frequencyBand=fb)
            cas.add(feature)

            sum = 0
            for x in counts:
                sum += x

            bands_with_count = [['F1', counts[0]], ['F2', counts[1]], ['F3', counts[2]], ['F4', counts[3]],
                                ['F5', counts[4]], ['F6', counts[5]], ['F7', counts[6]], ['OOV', counts[7]]]

            for pair in bands_with_count:
                F = self.ts.get_type('org.lift.type.FeatureAnnotationNumeric')
                feature = F(name='org.lift.type.FrequencyBand_' + pair[0] + '_ratio', value=pair[1], begin=0, end=0)
                cas.add(feature)

        return True


