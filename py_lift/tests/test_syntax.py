import pytest
import re
import ast
import sys
from dkpro import T_FEATURE
from util import load_lift_typesystem
from cassis import load_cas_from_xmi
from syntax import FE_CasToTree
from pyconll.load import load_from_file
import logging
import statistics as stats
from udapi.core.document import Document

logger = logging.getLogger(__name__)

ts = load_lift_typesystem()

casfile = "data/k002_s04_cas.xmi"  # sample file from OSNA corpus
myview = "corr"  # learner layer
conllufile = "data/k002_s04_corr_offsets.conllu"  # conllu file from OSNA corpus, with annotations in metadata fields of sentences


UD_SYNTAX_TEST_STRING = """# text = Solltest Du dann auf einmal kalte Füße bekommen, dann gnade Dir Gott.
1	Solltest	Solltest	AUX	VMFIN	Mood=Sub|Number=Sing|Person=2|Tense=Past|VerbForm=Fin	8	aux	_	Morph=2sit|NE=O|TopoField=LK
2	Du	du	PRON	PPER	Case=Nom|Number=Sing|PronType=Prs	8	nsubj	_	Morph=ns*2|NE=O|TopoField=MF
3	dann	dann	ADV	ADV	_	8	advmod	_	Morph=null|NE=O|TopoField=MF
4	auf	auf	ADP	APPR	Case=Acc	5	case	_	Morph=a|NE=O|TopoField=MF
5	einmal	einmal	ADV	ADV	_	8	obl	_	Morph=null|NE=O|TopoField=MF
6	kalte	kalt	ADJ	ADJA	Case=Acc|Gender=Masc|Number=Plur	7	amod	_	Morph=apm|NE=O|TopoField=MF
7	Füße	Fuß	NOUN	NN	Case=Acc|Gender=Masc|Number=Plur	8	obj	_	Morph=apm|NE=O|TopoField=MF
8	bekommen	bekommen	VERB	VVINF	_	11	advcl	_	Morph=null|NE=O|SpaceAfter=No|TopoField=VC
9	,	,	PUNCT	$,	_	8	punct	_	Morph=null|NE=O|TopoField=null
10	dann	dann	ADV	ADV	_	11	advmod	_	Morph=null|NE=O|TopoField=VF
11	gnade	gnaden	VERB	VVFIN	Mood=Sub|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	0	root	_	Morph=3sks|NE=O|TopoField=LK
12	Dir	du	PRON	PPER	Case=Dat|Number=Sing|PronType=Prs	11	obj	_	Morph=ds*2|NE=O|TopoField=MF
13	Gott	Gott	PROPN	NE	Case=Nom|Gender=Masc|Number=Sing	11	nsubj	_	Morph=nsm|NE=B-OTH|SpaceAfter=No|TopoField=MF
14	.	.	PUNCT	$.	_	11	punct	_	Morph=null|NE=O|SpaceAfter=No|TopoField=null

"""


udapi_doc = Document()
udapi_doc.from_conllu_string(UD_SYNTAX_TEST_STRING)
assert len(udapi_doc.bundles) == 1

tree = udapi_doc.bundles[0].get_tree()
fe2cas = FE_CasToTree(None, ts, "de", False)


def test_tree_depth():
    """In the test string , the maximum depth is 4. It applies to the nodes `auf` and `einmal`."""
    td = fe2cas._get_max_subtree_depth(tree)
    sys.stderr.write(f"{td}")
    assert td == 4


def test_count_nodes_with_specified_values_for_feat():
    """The sample tree has two (full) verbs, namely `bekommen` and `gnade`."""
    result = fe2cas._count_nodes_with_specified_values_for_feat(tree, "upos", ["VERB"])
    assert result == 2


def test_get_max_dep_length():
    """In the sample string, `Solltest` is separated from `bekommen` by 6 intervening tokens, so the distance between the two nodes is 7"""
    maxlen = fe2cas._get_max_dep_length(tree, excluded_rels=["root", "punct"])
    assert maxlen == 7


def test_get_filtered_children():
    """The verb `gnade` at the root of the sentence has 4 children with relations other than `punct`.
    (We identify the `root` as the one and only child of the virtual root node, i.e. `tree._children[0]`.)
    """
    children_of_sentence_root = fe2cas._get_filtered_children(
        tree._children[0], ["punct"]
    )
    assert len(children_of_sentence_root) == 4


def test_get_lex_np_sizes():
    """The noun phrase `Gott` (NE) has length 1, the noun phrase `kalte Füße` (NN) has length 2.
    The heads of NPs are defined  in terms of language specific POS-Tags (`xpos`).
    """
    sizes = sorted(fe2cas._get_lex_np_sizes(tree, lex_noun_pos_tags=["NN", "NE"]))
    assert sizes == [1, 2]


def test_multi_sentence_results():
    # if the cas has the info stored already, we use that;   otherwise, we compute it
    stored_vals = {}
    with open(casfile, "rb") as f:
        cas = load_cas_from_xmi(f, typesystem=ts)
        numfeats = cas.select(T_FEATURE)

        fe2cas = FE_CasToTree(myview, ts, "de", False)
        
        if len(numfeats) > 0:
            pass
        else:
            fe2cas.extract(cas)

            numfeats = cas.select(T_FEATURE)

        for numfeat in numfeats:
            stored_vals[numfeat.get("name")] = numfeat.get("value")

        fe2cas.annotate(cas, "de")
        cas.to_xmi("modified.xmi")

    # process the manual annos in the conllu file
    goldconllu = load_from_file(conllufile)
    tree_depths = []
    v_counts = []
    s_lens = []
    v_fin_counts = []
    s_before_vfin = 0
    s_after_vfin = 0
    deps_left = []
    deps_right = []
    max_dep_lengths = []
    for sent in goldconllu:
        s_lens.append(sent.__len__())
        annots_str_raw = str(sent.meta_value("gold"))
        annots_str = re.sub("'", '"', annots_str_raw)
        annots = ast.literal_eval(annots_str)
        max_dep_lengths.append(annots["max_dep_len"])
        tree_depths.append(annots["tree_depth"])
        v_counts.append(annots["vtotal"])
        v_fin_counts.append(annots["vfin_ct"])
        s_before_vfin += annots["s_before_vfin"][True]
        s_after_vfin += annots["s_before_vfin"][False]
        deps_left.extend(annots["deps_left"])
        deps_right.extend(annots["deps_right"])

    print("Comparing value from cas (left) to value from conllu file (right)")
    assert stored_vals["Average_Tree_Depth"] == stats.mean(tree_depths)
    assert stored_vals["Average_Number_Of_Verbs"] == stats.mean(v_counts)
    assert stored_vals["Average_Number_Of_Finite_Verbs"] == stats.mean(v_fin_counts)
    assert stored_vals["Average_Sentence_Length"] == stats.mean(s_lens)
    assert stored_vals["Average_Maximal_Dependency_Length"] == stats.mean(
        max_dep_lengths
    )

    propinv = round(s_after_vfin / (s_before_vfin + s_after_vfin), 2)
    assert (
        propinv == stored_vals["Proportion_of_Subj_Vfin_Inversions"]
    ), "Proportion_of_Subj_Vfin_Inversions does not match"

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
