import pytest
import sys
import re
import json
import ast
from util import load_typesystem
from cassis import Cas, load_cas_from_xmi
from syntax import FE_CasToTree  # FE_TokensPerSentence
import udapi
import pyconll
import logging
import statistics as stats

logger = logging.getLogger(__name__)

T_TOKEN = "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token"
T_SENTENCE = "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence"
T_FEATURE = "org.lift.type.FeatureAnnotationNumeric"


ts = load_typesystem("data/TypeSystem.xml")


# casfile = "data/k002_s04_cas.xmi_modded.xmi"
casfile = "data/k002_s04_cas.xmi" # sample file from OSNA corpus
myview = "corr"  # learner layer

#casfile = "data/1023_0001416.xmi" #  sample file from MERLIN
#myview = "_InitialView"
#conllufile = "data/k002_s04_corr_offsets.conllu" # conllu file from OSNA corpus, with annotations in metadata fields of sentences


def extract_feats_into_metadata():
    
    # if the cas has the info stored already, we use that;   otherwise, we compute it
    stored_vals = {}
    with open(casfile, "rb") as f:
        cas = load_cas_from_xmi(f, typesystem=ts)
        numfeats = cas.select(T_FEATURE)


        if len(numfeats) > 0:
            pass
        else:
            fe2cas = FE_CasToTree(myview, ts)
            fe2cas.extract(cas)
            print("and now annotate!")
            fe2cas.annotate(cas)

            numfeats = cas.select(T_FEATURE)
            for numfeat in numfeats:
                stored_vals[numfeat.get("name")] = numfeat.get("value")

        cas.to_xmi(casfile + "_modded.xmi",pretty_print=True)
        print(stored_vals)

if __name__ == "__main__":
    extract_feats_into_metadata()