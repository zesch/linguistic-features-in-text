import spacy
import unicodedata
from cassis import Cas
from dkpro import T_TOKEN, T_SENT, T_POS, T_DEP
from util import load_lift_typesystem

class Spacy_Preprocessor:
    # TODO really work with small models only?
    # TODO support more languages
    # TODO support custom models?
    def __init__(self, language: str):
        if language == "en":
            self.nlp = spacy.load("en_core_web_md")
        elif language == "de":
            self.nlp = spacy.load("de_core_news_sm")
        else:
            raise ValueError(f"Language '{language}' not supported in Spacy_Preprocessor")
        
        self.ts = load_lift_typesystem()

    def _clean_string(self, text: str) -> str:
        ''' Remove control characters and extra whitespace '''
        cleaned = ''.join(ch for ch in text if unicodedata.category(ch)[0]!="C")
        unstretched = ' '.join(cleaned.split())
        return unstretched

    def run(self, text) -> Cas:
        self.cas = Cas(self.ts)

        # converting from spaCy to DKPro is challenging
        # we discard control characters and multiple whitespaces here to make handling offsets easier
        cleaned = self._clean_string(text)
        self.cas.sofa_string = cleaned
        doc = self.nlp(cleaned)

        T = self.ts.get_type(T_TOKEN)
        S = self.ts.get_type(T_SENT)
        P = self.ts.get_type(T_POS)
        D = self.ts.get_type(T_DEP)

        for sent in doc.sents:
            begin = doc[sent.start-1].idx
            end = begin + len(doc[sent.end-1].text)
            cas_sentence = S(begin=begin, end=end)
            self.cas.add(cas_sentence)

        token_with_annotations = []
        for token in doc:
            cas_token = T(begin=token.idx, end=token.idx+len(token.text), id=token.i)
            self.cas.add(cas_token)

            cas_pos = P(begin=token.idx, end=token.idx+len(token.text), PosValue=token.pos)
            self.cas.add(cas_pos)
            token_with_annotations.append(cas_pos)

        for tok in doc:
            if tok.head == tok:
                continue
            cas_dep = D(begin=tok.idx, end=tok.idx+len(tok.text), Governor=token_with_annotations[tok.head.i],
                        Dependent=token_with_annotations[tok.i], DependencyType=tok.dep_,flavor='basic')
            self.cas.add(cas_dep)

        return self.cas