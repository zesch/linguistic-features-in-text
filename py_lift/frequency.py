from cassis import Cas
from util import load_lift_typesystem
from wordfreq import zipf_frequency
from dkpro import T_TOKEN

class SE_TokenZipfFrequency:

    def __init__(self, language):
        self.ts = load_lift_typesystem()
        self.language = language

    def process(self, cas: Cas) -> bool:
        F = self.ts.get_type("org.lift.type.Frequency")

        for token in cas.select(T_TOKEN):
            freq= zipf_frequency(token.get_covered_text(), self.language)
            if 2 > freq > 0:
                fb = 'f1'
            elif 3 > freq >= 2:
                fb = 'f2'
            elif 4 > freq >= 3:
                fb = 'f3'
            elif 5 > freq >= 4:
                fb = 'f4'
            elif 6 > freq >= 5:
                fb = 'f5'
            elif 7 > freq >= 6:
                fb = 'f6'
            elif freq >= 7:
                fb = 'f7'
            elif freq == 0:
                fb = 'oov'

            feature = F(begin=token.begin, end=token.end, value=freq, frequencyBand=fb)
            cas.add(feature)

        return True