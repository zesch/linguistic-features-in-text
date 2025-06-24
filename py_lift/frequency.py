from cassis import Cas
from util import load_lift_typesystem
from wordfreq import zipf_frequency
from dkpro import T_TOKEN

class SE_WordFrequency:

    def __init__(self, language):
        self.ts = load_lift_typesystem('data/TypeSystem.xml')
        self.language = language

    def process(self, cas: Cas) -> bool:
        for token in cas.select(T_TOKEN):
            freq= zipf_frequency(token.get_covered_text(), self.language)

            F = self.ts.get_type("org.lift.type.Frequency")
            feature = F(begin=token.begin, end=token.end, value=freq)
            cas.add(feature)

        return True