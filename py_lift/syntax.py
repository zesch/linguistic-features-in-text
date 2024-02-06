from cassis import *
from util import (
	load_typesystem,
)
from udapi.core.node import Node
import pprint as pp
from udapi.core.document import Document
import pandas as pd
import re
from collections import Counter
from typing import List, Dict, Union, Generator, Tuple

UD_SYNTAX_TEST_STRING = """# sent_id = 299,300
# text = Solltest Du dann auf einmal kalte Füße bekommen, dann gnade Dir Gott.
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


# TODO should be in resource file
FINITE_VERBS_STTS = ["VVFIN", "VMFIN", "VAFIN"]
FINITE_VERB_STTS_BROAD = ["VVFIN", "VVIMP", "VMFIN", "VAFIN", "VMIMP", "VAIMP"]
TIGER_SUBJ_LABELS = ["SB", "EP"]  # the inclusion of expletives (EP) is sorta debatable
TIGER_LEX_NOUN_POS = ["NN", "NE"]

class FE_CasToTree:
	def __init__(self, layer, ts):
		self.ts = ts
		self.layer = layer

		self.token_path = self.ts.get_type(
			"de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token"
		)
		self.lemma_path = self.ts.get_type(
			"de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Lemma"
		)
		self.pos_path = self.ts.get_type(
			"de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS"
		)
		self.sent_path = self.ts.get_type(
			"de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence"
		)
		self.morph_path = self.ts.get_type(
			"de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.morph.Morpheme"
		)
		self.deps_path = self.ts.get_type(
			"de.tudarmstadt.ukp.dkpro.core.api.syntax.type.dependency.Dependency"
		)

	def add_feat_to_cas(self, cas, name, featpath, value):
		F = self.ts.get_type(featpath)
		feature = F(name=name, value=value)
		cas.add(feature)

	def extract(self, cas):
		
		# TODO why "vu"?
		vu = cas.get_view(self.layer)


		deps_list = vu.select(self.deps_path)
		# TODO: get rid of the magic number below; only used for debugging
		MAXSENT = 2000
		sct = 0
		dep_matches = []
		dependency_length_distribution_per_rel_type = {}
		sent_lengths = []  # list of int
		tree_depths = []  # list of int
		finite_verb_counts = []  # list of int
		total_verb_counts = []  # list of int
		subj_before_vfin = []  # list of bool
		lex_np_sizes = []  # list of int

		for sent in vu.select(self.sent_path):
			sct += 1
			if sct > MAXSENT:
				break

			# NB: we need to filter out empty tokens that have no annotations
			unfiltered_token_list = vu.select_covered(self.token_path, sent)
			token_list = [
				x
				for x in unfiltered_token_list
				if not re.match("^\s*$", x.get_covered_text())
			]

			form_list = [x.get_covered_text for x in token_list]
			orig_id_list = [x.xmiID for x in token_list]
			id_list = list(range(1, len(token_list) + 1))

			id_map = dict(zip(orig_id_list, id_list))

			lemma_list = [
				x.get_covered_text for x in vu.select_covered(self.lemma_path, sent)
			]
			pos_list = [x.PosValue for x in vu.select_covered(self.pos_path, sent)]
			morph_list = [x.morphTag for x in vu.select_covered(self.morph_path, sent)]
			
			# TODO why like this?
			udpos_list = ["FM"] * len(token_list)

			rel_list = []
			head_list = []
			enhanced_deps_list = ["_"] * len(token_list)
			misc_list = ["_"] * len(token_list)

			for token in token_list:
				token_id = token.xmiID
				del dep_matches[:]
				for dep in deps_list:
					if (
						dep.Governor.xmiID not in id_map
						and dep.Dependent.xmiID not in id_map
					):
						pass
					else:
						if dep.Dependent.xmiID == token_id:
							dep_matches.append(dep)
							# root node (in Merlin) has its own id as head!
							if dep.Governor.xmiID == token_id:
								head_list.append(0)
								rel_list.append("root")
							else:
								head_list.append(id_map[dep.Governor.xmiID])
								rel_list.append(dep.DependencyType)
						else:
							pass
				if len(dep_matches) == 0:
					raise RuntimeError(
						"No dependency matches for token %s !\n" % token.get_covered_text
					)

			assert len(udpos_list) == len(token_list)
			assert len(head_list) == len(token_list)
			assert len(head_list) == len(rel_list)
			
			list_of_cols = [
				id_list,
				form_list,
				lemma_list,
				udpos_list,
				pos_list,
				morph_list,
				head_list,
				rel_list,
				enhanced_deps_list,
				misc_list,
			]
			colnames = [
				"id",
				"token",
				"lemma",
				"udpos",
				"pos",
				"morph",
				"head",
				"rel",
				"enhanced_deps",
				"misc",
			]
			df = pd.DataFrame(list_of_cols, colnames).T

			sent_id_line = "# sent_id = 1"
			s_text_line = "# text = " + re.sub("\n", " ", sent.get_covered_text())
			df_str = df.to_csv(index=False, header=False, sep="\t")
			conllu_string = sent_id_line + "\n" + s_text_line + "\n" + df_str
			conllu_string = re.sub("\n{2,}", "\n", conllu_string).strip()

			udapi_doc = Document()
			udapi_doc.from_conllu_string(conllu_string)

			# udapi_doc.from_conllu_string(TEST_STRING)
			for bundle in udapi_doc.bundles:
				tree = bundle.get_tree()
				print(tree.compute_text())
				# finite verbs are identifed by their xpos-tag; we're not looking at any info in the morphological feats
				finite_verb_counts.append(
					self.count_nodes_with_specified_values_for_feat(
						tree, "xpos", [".*FIN"]
					)
				)
				# all verbal forms have a pos-Tag beginning with "V"
				total_verb_counts.append(
					self.count_nodes_with_specified_values_for_feat(
						tree, "xpos", ["V.*"]
					)
				)
				subj_before_vfin.extend(self.check_s_before_vfin(tree))

				tree_depths.append(self.get_max_subtree_depth(tree))
				sent_lengths.append(len(tree.descendants))
				lex_np_sizes.extend(self.get_lex_np_sizes(tree))

				# Not used for now
				# print(list(self.get_triples(tree, feats=["xpos","deprel"])))

				dependency_length_distribution_per_rel_type = self.update_dep_dist(
					tree, dependency_length_distribution_per_rel_type
				)

		NUM_FEATURE = "org.lift.type.FeatureAnnotationNumeric"
		print(
			"Dependency length distribution per relation type\n"
			+ pp.pformat(dependency_length_distribution_per_rel_type)
		)
		(
			avg_left_dep_len,
			avg_right_dep_len,
			avg_all_dep_len,
		) = self.get_dependency_lengths_across_all_rels_in_doc(
			dependency_length_distribution_per_rel_type
		)

		print("average dependency length leftward %s" % avg_left_dep_len)
		self.add_feat_to_cas(
			cas, "Average_Dependeny_Length_Left", NUM_FEATURE, avg_left_dep_len
		)
		print("average dependency length rightward %s" % avg_right_dep_len)
		self.add_feat_to_cas(
			cas, "Average_Dependeny_Length_Right", NUM_FEATURE, avg_right_dep_len
		)
		print("average dependency length all %s" % avg_all_dep_len)
		self.add_feat_to_cas(
			cas, "Average_Dependeny_Length_All", NUM_FEATURE, avg_all_dep_len
		)

		print("sent lengths %s" % sent_lengths)
		avg_sent_len = round(float(sum(sent_lengths)) / len(sent_lengths), 2)
		self.add_feat_to_cas(
			cas, "Average_Sentence_Length", NUM_FEATURE, avg_sent_len
		)

		print("tree_depths %s" % tree_depths)
		avg_tree_depth = round(float(sum(tree_depths)) / len(tree_depths), 2)
		self.add_feat_to_cas(
			cas, "Average_Tree_Depth", NUM_FEATURE, avg_tree_depth
		)

		print("finite_verb_counts %s" % finite_verb_counts)
		try:
			avg_finite_verbs = round(
				float(sum(finite_verb_counts)) / len(finite_verb_counts), 2
			)
		except:
			avg_finite_verbs = 0
		self.add_feat_to_cas(
			cas, "Average_Number_Of_Finite_Verbs", NUM_FEATURE, avg_finite_verbs
		)

		print("total_verb_counts %s" % total_verb_counts)
		try:
			avg_verb_count = round(
				float(sum(total_verb_counts)) / len(total_verb_counts), 2
			)
		except:
			avg_verb_count = 0
		self.add_feat_to_cas(
			cas, "Average_Number_Of_Verbs", NUM_FEATURE, avg_verb_count
		)

		print("subj_before_vfin %s" % subj_before_vfin)
		invc = Counter(subj_before_vfin)
		try:
			share_of_s_vfin_inversions = invc[True] / invc[False]
		except:
			share_of_s_vfin_inversions = 0

		self.add_feat_to_cas(
			cas, "Proportion_of_Subj_Vfin_Inversions",
			NUM_FEATURE,
			share_of_s_vfin_inversions,
		)

		print("lex_np_sizes %s" % lex_np_sizes)
		try:
			avg_lex_np_size = round(float(sum(lex_np_sizes)) / len(lex_np_sizes), 2)
		except:
			avg_lex_np_size = 0
		self.add_feat_to_cas(
			cas, "Average_Size_Of_Lexical_NP", NUM_FEATURE, avg_lex_np_size
		)
		return True

	def get_average_from_counter(self, mycounter):
		""" get average value from counter """
		insts = 0
		totlen = 0
		for lng in mycounter:
			totlen += mycounter[lng] * lng
			insts += mycounter[lng]
		try:
			avg_dep_len = round(float(totlen / insts), 2)
		except:
			avg_dep_len = 0

		return avg_dep_len

	# def get_dependency_lengths_across_all_rels_in_doc(counts_per_rel):
	def get_dependency_lengths_across_all_rels_in_doc(
		self, counts_per_rel: Dict
	) -> Tuple:
		"""
		Merge the information from individual counters per relation type.
		Do this once for each dependency direction and then do this for absolute values.
		Returns three average dependency length values.
		"""
		leftward = Counter()
		rightward = Counter()
		for rel in counts_per_rel.keys():
			ctr = counts_per_rel[rel]
			for kee in ctr.keys():
				if kee < 0:
					leftward.update({abs(kee): ctr[kee]})
				else:
					rightward.update({kee: ctr[kee]})
		anydir = Counter()
		anydir.update(leftward)
		anydir.update(rightward)
		avg_all = self.get_average_from_counter(anydir)
		avg_left = self.get_average_from_counter(leftward)
		avg_right = self.get_average_from_counter(rightward)

		return (avg_left, avg_right, avg_all)


	def get_max_subtree_depth(self, node: Node) -> int:
		""" determine depth of the subtree rooted at the given node """
		return max([child._get_attr("depth") for child in node.descendants])

	def count_nodes_with_specified_values_for_feat(
		self, node, featname, wanted_values
	) -> int:
		"""count nodes with specified values for a given feature; values are regex"""
		return len(
			set(
				[
					child
					for child in node.descendants
					for wv in wanted_values
					if re.match(wv, child._get_attr(featname))
				]
			)
		)

	def update_dep_dist(self, node, dep_dist) -> Dict:
		"""Update the document-level distribution of dependency lenghts per dependency type by processing the nodes in the tree.
		Dep length is the difference between the indices of the head and the dependent. Deps adjacent to their heads have a dep length of |1| , etc.
		The values can be pos and neg: they're positive if the dependent is to the right of the head, and negative if it's the other way around.
		We're not merging the two cases by using absolute values!
		"""
		for d in node.descendants:
			rel = d.deprel
			cix = d.ord
			pix = d.parent.ord
			diff = cix - pix
			if not rel in dep_dist:
				dep_dist[rel] = Counter()
			dep_dist[rel][diff] += 1
		return dep_dist

	def get_triples(self, node: Node, feats=["form", "upos"]) -> Generator:
		"""Yields triples of the form: (head, dependency_rel, dep) where head and dep are tuples
		containing the attributes specified in the feats parameter.
		Default feats are "form" and "upos".
		"""
		head = tuple(node.get_attrs(feats, stringify=False))
		for i in node.children:
			dep = tuple(i.get_attrs(feats, stringify=False))
			yield (head, i.deprel, dep)
			yield from self.get_triples(i, feats=feats)

	def get_lex_np_sizes(
		self, tree: Node, lex_noun_pos_tags=TIGER_LEX_NOUN_POS
	) -> List[int]:
		"""get the number of tokens that make up the lexical noun phrases in the sentence/tree"""
		size_list = []
		for d in tree.descendants:
			if d.xpos in lex_noun_pos_tags:
				n_size = 1 + len(d.descendants)
				size_list.append(n_size)
		return size_list

	def check_s_before_vfin(
		self, node: Node, finiteverbtags=FINITE_VERBS_STTS, subjlabels=TIGER_SUBJ_LABELS
	) -> List[bool]:
		"""
		True or false depending on whether a subject precedes its finite verb .
		If a verb lacks a subject, it's disregarded.
		The lists of pos tags for finite verbs and of subj relation labels may need to be adjusted per tagger/parser used!
		"""
		s_inv_list = []
		for d in node.descendants:
			if d.xpos in finiteverbtags:
				print(d.form, d.upos, d.xpos)
				for kid in d.children:
					if kid.deprel in subjlabels:
						if kid.ord > d.ord:
							s_inv_list.append(True)
						else:
							s_inv_list.append(False)
		return s_inv_list
