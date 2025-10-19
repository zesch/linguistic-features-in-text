import spacy
import unicodedata
from cassis import Cas
from dkpro import T_TOKEN, T_SENT, T_POS, T_DEP, T_LEMMA
from util import load_lift_typesystem

class Spacy_Preprocessor:
    # TODO really work with small models only?
    # TODO support more languages
    # TODO support custom models?
    def __init__(self, language: str):
        if language == "en":
            self.nlp = spacy.load("en_core_web_md")
        elif language == "de":
            self.nlp = spacy.load("de_core_news_lg")
        elif language == "fr":
            self.nlp = spacy.load("fr_core_news_lg")
        elif language == "tr":
            self.nlp = spacy.load("tr_core_news_md")
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
        L = self.ts.get_type(T_LEMMA)

        for sent in doc.sents:
            begin = doc[sent.start-1].idx
            end = begin + len(doc[sent.end-1].text)
            cas_sentence = S(begin=begin, end=end)
            self.cas.add(cas_sentence)

        token_annos = []
        for token in doc:
            # TODO need to map from spacy pos tags to dkpro 
            cas_pos = P(begin=token.idx, end=token.idx+len(token.text), PosValue=token.tag_)
            print(cas_pos)
            self.cas.add(cas_pos)
            
            cas_lemma = L(begin=token.idx, end=token.idx+len(token.text), value=token.lemma_)
            self.cas.add(cas_lemma)

            cas_token = T(
                begin=token.idx, 
                end=token.idx+len(token.text), 
                id=token.i,
                pos=cas_pos,
                lemma=cas_lemma
                )
            self.cas.add(cas_token)
            token_annos.append(cas_token)



    

        # need another loop to ensure that all tokens are already in the CAS
        for token in doc:
            if token.head == token:
                continue

            token_anno = token_annos[token.i]

            cas_dep = D(
                begin=token_anno.begin, 
                end=token_anno.end, 
                Governor=token_annos[token.head.i],
                Dependent=token_annos[token.i], 
                DependencyType=token.dep_,
                flavor='basic'
            )
            self.cas.add(cas_dep)

        return self.cas