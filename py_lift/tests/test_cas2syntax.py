import pytest
import re
import ast
from util import load_typesystem
from cassis import load_cas_from_xmi
from syntax import FE_CasToTree  # FE_TokensPerSentence
import pyconll
import logging
import statistics as stats

logger = logging.getLogger(__name__)

T_FEATURE = "org.lift.type.FeatureAnnotationNumeric"

ts = load_typesystem("data/TypeSystem.xml")

casfile = "data/k002_s04_cas.xmi" # sample file from OSNA corpus
myview = "corr"  # learner layer
conllufile = "data/k002_s04_corr_offsets.conllu" # conllu file from OSNA corpus, with annotations in metadata fields of sentences

def test_syntax():    
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

            numfeats = cas.select(T_FEATURE)

        for numfeat in numfeats:
            stored_vals[numfeat.get("name")] = numfeat.get("value")

    # process the manual annos in the conllu file
    goldconllu = pyconll.load_from_file(conllufile)
    tree_depths = []
    v_counts = []
    s_lens = []
    v_fin_counts = []
    s_before_vfin = 0
    s_after_vfin = 0
    deps_left = []
    deps_right = []
    max_dep_lengths =[]
    for sent in goldconllu:
        s_lens.append(sent.__len__())
        annots_str_raw = sent.meta_value("gold")
        annots_str = re.sub("'", '"', annots_str_raw)
        annots = ast.literal_eval(annots_str)
        max_dep_lengths.append(annots["max_dep_len"])
        tree_depths.append(annots["tree_depth"])
        v_counts.append(annots["vtotal"])
        v_fin_counts.append(annots["vfin_ct"])
        s_before_vfin+= annots["s_before_vfin"][True]
        s_after_vfin+=annots["s_before_vfin"][False]
        deps_left.extend(annots["deps_left"])
        deps_right.extend(annots["deps_right"])



    print("Comparing value from cas (left) to value from conllu file (right)")
    assert stored_vals["Average_Tree_Depth"] == stats.mean(tree_depths)
    assert stored_vals["Average_Number_Of_Verbs"] == stats.mean(v_counts)
    assert stored_vals["Average_Number_Of_Finite_Verbs"] == stats.mean(v_fin_counts)
    assert stored_vals["Average_Sentence_Length"] == stats.mean(s_lens)
    assert stored_vals["Average_Maximal_Dependency_Length"] == stats.mean(max_dep_lengths)

    
    propinv = round( s_after_vfin / (s_before_vfin + s_after_vfin), 2)
    assert propinv == stored_vals["Proportion_of_Subj_Vfin_Inversions"]

    assert stored_vals["Average_Dependency_Length_Left"] == round(
         stats.mean(deps_left), 2
    )

    assert stored_vals["Average_Dependency_Length_Right"] == round(
        stats.mean(deps_right), 2
    )

    all_deps = deps_left + deps_right
    assert stored_vals["Average_Dependency_Length_All"] == round(
        stats.mean(all_deps), 2
    )