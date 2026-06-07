
import pytest
from py_lift.preprocessing import Spacy_Preprocessor
from py_lift.annotators.misc import SE_CoarsePosTagAnnotator
from py_lift.dkpro import T_POS

def test_coarse_postag_annotator():
    text = "Ich bin ein Beispiel und sehe gut aus."
    spacy = Spacy_Preprocessor(language='de')
    cas = spacy.run(text)
    fine_pos_tags = [pos.PosValue for pos in cas.select(T_POS)]
    assert fine_pos_tags == ['PPER', 'VAFIN', 'ART', 'NN', 'KON', 'VVFIN', 'ADJD', 'PTKVZ', '$.']                                
    
    SE_CoarsePosTagAnnotator("de", "de-stts-pos").process(cas)

    assert len(list(cas.select("de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS_NOUN"))) == 1
    assert len(list(cas.select("de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS_VERB"))) == 3
    assert len(list(cas.select("de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS_X"))) == 0
    assert len(list(cas.select(T_POS))) == 9