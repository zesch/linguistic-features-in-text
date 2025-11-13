import pytest
import sys
import re
import json
import ast
from py_lift.util import load_lift_typesystem
from cassis import Cas, load_cas_from_xmi
from py_lift.syntax import FE_CasToTree  # FE_TokensPerSentence
import udapi
import pyconll
import os
import logging
import glob
import statistics as stats

logger = logging.getLogger(__name__)

T_TOKEN = "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token"
T_SENTENCE = "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence"
T_FEATURE = "org.lift.type.FeatureAnnotationNumeric"


ts = load_lift_typesystem()


# casfile = "data/k002_s04_cas.xmi_modded.xmi"
#casfile = "data/k002_s04_cas.xmi" # sample file from OSNA corpus
#myview = "corr"  # learner layer

#casfile = "/mnt/big/jkrcode/paula2cas/retagged/spacy/1091_0000274.xmi"#1091_0000266.xmi" #  sample file from MERLIN
#myview = "learner"
#conllufile = "data/k002_s04_corr_offsets.conllu" # conllu file from OSNA corpus, with annotations in metadata fields of sentences


def extract_feats_into_metadata(casfile,myview):
    if os.path.exists(casfile + "_modded_"+myview+".xmi"):
        print("target file exists, skipping! %s" %(casfile + "_modded_"+myview+".xmi"))
    # if the cas has the info stored already, we use that;   otherwise, we compute it
    stored_vals = {}
    with open(casfile, "rb") as f:
        cas = load_cas_from_xmi(f, typesystem=ts)
        numfeats = cas.select(T_FEATURE)


        if len(numfeats) > 0:
            sys.stderr.write("Found %d features\n" % (len(numfeats)))
            pass
        else:
            fe2cas = FE_CasToTree(myview, ts)
            fe2cas.extract(cas)

            fe2cas.annotate(cas)
            numfeats = cas.select(T_FEATURE)
            for numfeat in numfeats:
                stored_vals[numfeat.get("name")] = numfeat.get("value")

            cas.to_xmi(casfile + "_modded_"+myview+".xmi",pretty_print=True)
            print(stored_vals)

if __name__ == "__main__":
    indir = "/mnt/big/jkrcode/paula2cas/retagged/experiment"
    flist =  sorted([ x for x in  glob.glob(indir + "/*.xmi") if not "modded" in x])
    print(str(len(flist))+ " files to process")
    #sys.exit(-2)
    #MAXPROC=1
    #fct=0

    for file in flist:
        print("## PROCESSING %s" % (file))
        extract_feats_into_metadata(file,"learner")
        extract_feats_into_metadata(file,"TH1")

        #fct+=1
        #if fct>MAXPROC:
        #    break