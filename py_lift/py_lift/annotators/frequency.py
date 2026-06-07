from cassis import Cas
from py_lift.decorators import supported_languages, requires_types
from py_lift.util import load_lift_typesystem
from wordfreq import zipf_frequency
from py_lift.dkpro import T_TOKEN
from py_lift.annotators.api import SEL_BaseAnnotator


@supported_languages(
'ar',
'bn',
'bs',
'bg',
'ca',
'zh',
'hr',
'cs',
'da',
'nl',
'en',
'fi',
'fr',
'de',
'el',
'he',
'hi',
'hu',
'is',
'id',
'it',
'ja',
'ko',
'lv',
'lt',
'mk',
'ms',
'nb',
'fa',
'pl',
'pt',
'ro',
'ru',
'sk',
'sl',
'sr',
'es',
'sv',
'fi',
'ta',
'tr',
'uk',
'ur',
'vi')
@requires_types("org.lift.type.Frequency")
class SE_TokenZipfFrequency(SEL_BaseAnnotator):

    def __init__(self, language):
        super().__init__(language)

    def _process(self, cas: Cas) -> bool:
        
        F = self.get_type("org.lift.type.Frequency")

        for token in cas.select(T_TOKEN):
            # TODO removed for now. This is language dependent and token.pos might not be set - need to check
            # if token.pos.PosValue in ['PUNCT', 'SYM']:
            #     continue

            freq = zipf_frequency(token.get_covered_text(), self.language)
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