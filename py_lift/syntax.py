from cassis import *
from udapi.core.node import Node
import pprint as pp
from udapi.core.document import Document
import re
from utils.conllu import cas_to_str
from collections import Counter
from typing import List, Dict, Union, Generator, Tuple
from dkpro import *
import statistics as stats
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
FINITE_VERBS_STTS_BROAD = ["VVFIN", "VVIMP", "VMFIN", "VAFIN", "VMIMP", "VAIMP"]
NONFINITE_VERBS_STTS_BROAD = [
	"VVPP",
	"VAPP",
	"VMPP",
	"VVINF",
	"VAINF",
	"VMINF",
	"VVIZU",
]
INFINITIVES_STTS = ["VVINF", "VAINF", "VMINF", "VVIZU"]  # maybe leave out VVIZU?
ALL_VERB_TAGS_STTS = FINITE_VERBS_STTS_BROAD + NONFINITE_VERBS_STTS_BROAD
FINITE_MOD_AUX_STTS = ["VMFIN", "VAFIN"]

TIGER_SUBJ_LABELS = ["SB", "EP"]  # the inclusion of expletives (EP) is sorta debatable
TIGER_LEX_NOUN_POS = ["NN", "NE"]

LEMMA_FEAT = "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Lemma"
POS_FEAT = "de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS"
DEP_FEAT = "de.tudarmstadt.ukp.dkpro.core.api.syntax.type.dependency.Dependency"
TOK_FEAT = "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token"
STRUCT_FEAT = "org.lift.type.Structure"

DEFAULT_FEATLIST = [
	LEMMA_FEAT,
	POS_FEAT,
	DEP_FEAT,
]

MAP_FEAT_TO_KEY_ATTRIB = {
	LEMMA_FEAT: "value",
	POS_FEAT: "PosValue",
	DEP_FEAT: "DependencyType",
}


class StuffRegistry:
	def __init__(self):
		self.dependency_length_distribution_per_rel_type = {}
		self.dependents_count_distribution_per_verb_type = {}

		self.max_dep_lengths =[] # list of int
		self.sent_lengths = []  # list of int
		self.tree_depths = []  # list of int
		self.finite_verb_counts = []  # list of int
		self.total_verb_counts = []  # list of int
		self.modal_verb_counts = []  # list of int
		self.position_of_subj_relative_to_vfin = (
			[]
		)  # list of int (where 1 signifies S after Vfin, and -1 the opposite order)
		self.subj_less_verbs = []  # list of int
		self.verbal_bracket_cands = []  # list of int
		self.lex_np_sizes = []  # list of int
		self.substituting_pronoun_counts = []  # list of int
		self.attributive_pronoun_counts = []  # list of int
		self.personal_pronoun_counts = []  # list of int
		self.adposition_counts = []  # list of int
		self.preposition_counts = []  # list of int
		self.postposition_counts = []  # list of int
		self.relative_pronoun_counts = []  # list of int
		self.conjunction_counts = []  # list of int
		self.subordinator_counts = []  # list of int
		self.coordination_is_between_verbs = []  # list of bool
		self.rels_of_conjunctions = Counter()  # counter for deprel-strings as keys


class FE_CasToTree:
	def __init__(self, layer, ts):
		self.ts = ts
		self.layer = layer
		self.offset2label_map = {}

	def annotate(self, cas):
		view = cas.get_view(self.layer)

		self._fill_offset_map(view)

		# DEFAULT_JUNCTOR = "und"
		# junctor_list = [DEFAULT_JUNCTOR]

		myconstraints = {DEP_FEAT: ["ju"], LEMMA_FEAT: ["und"]}
		self._annotate_custom_struct(view, "JUNKTOR", myconstraints)

		myconstraints = {POS_FEAT: ["PPER","PRF","PIS","PPOS","PDS","PRELS","PWS"]}
		self._annotate_custom_struct(view, "PRON_SUBST", myconstraints)
	
		myconstraints = {POS_FEAT:["PPOSAT|PIAT|PDAT|PIDAT|PRELAT|PWAT"]}
		self._annotate_custom_struct(view, "PRON_ATTRIB", myconstraints)

		myconstraints = {DEP_FEAT:["ep","ph"], LEMMA_FEAT:["es"]}
		self._annotate_custom_struct(view, "EXPLETIVE", myconstraints)



	def _fill_offset_map(self, view):
		for FEAT in DEFAULT_FEATLIST:
			self.offset2label_map[FEAT] = {}
			items = view.select(FEAT)
			if FEAT != DEP_FEAT:
				for item in items:
					self.offset2label_map[FEAT][(item.begin, item.end)] = item.get(
						MAP_FEAT_TO_KEY_ATTRIB[FEAT]
					)
			else:
				# <dependency:Dependency xmi:id="519" Governor="12" Dependent="11" DependencyType="nk" flavor="basic" sofa="2"/>
				for deprel in items:
					rellabel = deprel.get(MAP_FEAT_TO_KEY_ATTRIB[FEAT])
					governed = deprel.get("Dependent")
					g_start = governed.begin
					g_end = governed.end
					self.offset2label_map[FEAT][(g_start, g_end)] = rellabel

	def _annotate_custom_struct(self, view: Cas, struct_name: str, constraints: Dict):
		"""annotate structures defined in terms of pos, dep and lemma"""
		matches = {}
		for CURR_FEAT in constraints:
			matches[CURR_FEAT] = set()
			ok_values = [item.lower() for item in constraints[CURR_FEAT]]

			cands = view.select(CURR_FEAT)
			if CURR_FEAT != DEP_FEAT:
				for cand in cands:
					if cand.get(MAP_FEAT_TO_KEY_ATTRIB[CURR_FEAT]).lower() in ok_values:
						matches[CURR_FEAT].add((cand.begin, cand.end))

			else:
				for cand in cands:
					if cand.get(MAP_FEAT_TO_KEY_ATTRIB[CURR_FEAT]).lower() in  ok_values:
						matches[CURR_FEAT].add(
							(cand.Dependent.begin, cand.Dependent.end)
						)

		sublists = [matches[kee] for kee in matches.keys()]
		final_matches = set.intersection(*sublists)
		for fm in final_matches:
			F = self.ts.get_type(STRUCT_FEAT)
			feature = F(name=struct_name, begin=fm[0], end=fm[1])
			view.add(feature)


	def _annotate_distant_verbal_brackets(
		self,
		node: Node,
		cas: Cas,
		finitemodeauxtags=FINITE_MOD_AUX_STTS,
		nonfinitetags=NONFINITE_VERBS_STTS_BROAD,

	):
		"""
		The code assumes that we're iterating sentences 
		in the udapi mode unlike the other annotation methods
		which just are based on selecting items from the cas.
		Therefore, for we currently simply call this from within extract.

		Maybe it would be cleaner to write code that 
		a) finds potential LSKs based on cas,
		b)  retrieves the sentences based on the coordinates of the token 
		c) and then processes the sentence in udapi node form

		"""
		bracket_candidates = []
		for d in node.descendants:
			if d.xpos in finitemodeauxtags:
				infdep = None
				for kid in d.children:
					if kid.xpos in nonfinitetags:
						infdep = kid
				if infdep is None:
					pass
					# bracket_candidates.append(999)
				else:
					if infdep.ord - d.ord > 1:
						name = "LSK"
						F = self.ts.get_type(STRUCT_FEAT)
						feature = F(name=name, begin=int(d.misc["t_start"]), end=int(d.misc["t_end"]))
						cas.add(feature)
						name = "RSK"
						F = self.ts.get_type(STRUCT_FEAT)
						feature = F(name=name, begin=int(infdep.misc["t_start"]), end=int(infdep.misc["t_end"]))
						cas.add(feature)

					else:
						pass
		return bracket_candidates


	def _annotate_junctors(self, view, junctor_list):


		deprels = view.select(DEP_FEAT)

		junctor_coords = []
		for deprel in deprels:
			if deprel.DependencyType.upper() == "JU":
				dependent = deprel.Dependent
				ds = dependent.get("begin")
				de = dependent.get("end")
				junctor_coords.append((ds, de))

		tox_for_view = view.select(TOK_FEAT)

		for cand in junctor_coords:

			for tok in tox_for_view:
				if (
					tok.get_covered_text().lower() in junctor_list
					and tok.begin == cand[0]
					and tok.end == cand[1]
				):
					name = "JUNCTOR"
					F = self.ts.get_type(STRUCT_FEAT)
					feature = F(name=name, begin=cand[0], end=cand[1])

					view.add(feature)
				else:
					pass

	def extract(self, cas):
		# TODO find out author id ~ file name from  metadatastringfield  within cas

		META_FEAT = (
			"de.tudarmstadt.ukp.dkpro.core.api.metadata.type.MetaDataStringField"
		)
		meta_feats = cas.select(META_FEAT)
		outfile = "undefined.xmi"
		for meta_feat in meta_feats:
			if meta_feat.get("key") == "_author_id":
				outfile = meta_feat.get("value") + "_modded.xmi"
		view = cas.get_view(self.layer)
		registry = StuffRegistry()

		# TODO: get rid of the magic number below; only used for debugging
		MAXSENT = 2000
		sct = 0
		for sent in view.select(T_SENT):
			self._register_stuff(view, registry, sent)

			sct += 1
			if sct > MAXSENT:
				break

		NUM_FEATURE = "org.lift.type.FeatureAnnotationNumeric"
		REF_TEXT_SIZE = 1000

		# register rels of `und`` without a preceding left clause
		# in STTS these uses have the rel `ju`
		JUNCTOR_REL = "ju"
		try:
			share_of_conj_uses_without_left_clause = round(
				float(
					registry.rels_of_conjunctions[JUNCTOR_REL]
					/ sum(registry.rels_of_conjunctions.values())
				),
				2,
			)
		except:
			share_of_conj_uses_without_left_clause = 0.0

		print(
			"Share_of_conj_uses_without_left_clause %s"
			% share_of_conj_uses_without_left_clause
		)
		self._add_feat_to_cas(
			cas,
			"Share_of_conj_uses_without_left_clause",
			NUM_FEATURE,
			share_of_conj_uses_without_left_clause,
		)

		###

		doc_length = sum(registry.sent_lengths)

		normalized_conjunction_proportion = round(
			(REF_TEXT_SIZE * float(sum(registry.conjunction_counts) / doc_length)), 2
		)
		print("CONJUNCTIONS_PER_1000 %s" % normalized_conjunction_proportion)
		self._add_feat_to_cas(
			cas,
			"Conjunctions_per_1k_tokens",
			NUM_FEATURE,
			normalized_conjunction_proportion,
		)


		for pos_class in registry.dependents_count_distribution_per_verb_type:
			self._add_feat_to_cas(
				cas,
				"Average_number_of_dependents_for_"+pos_class,
				NUM_FEATURE,
				stats.mean(registry.dependents_count_distribution_per_verb_type[pos_class]),
			)
    	
	

		normalized_subordinator_proportion = round(
			(REF_TEXT_SIZE * float(sum(registry.subordinator_counts) / doc_length)), 2
		)
		print("SUBORDINATORS_PER_1000 %s" % normalized_subordinator_proportion)
		self._add_feat_to_cas(
			cas,
			"Subordinators_per_1k_tokens",
			NUM_FEATURE,
			normalized_subordinator_proportion,
		)

		###

		normalized_adposition_proportion = round(
			(REF_TEXT_SIZE * float(sum(registry.adposition_counts) / doc_length)), 2
		)
		print("ADPOSITIONS_PER_1000 %s" % normalized_adposition_proportion)
		self._add_feat_to_cas(
			cas,
			"Adpositions_per_1k_tokens",
			NUM_FEATURE,
			normalized_adposition_proportion,
		)

		###

		normalized_preposition_proportion = round(
			(REF_TEXT_SIZE * float(sum(registry.preposition_counts) / doc_length)), 2
		)
		print("PREPOSITIONS_PER_1000 %s" % normalized_preposition_proportion)
		self._add_feat_to_cas(
			cas,
			"Prepositions_per_1k_tokens",
			NUM_FEATURE,
			normalized_preposition_proportion,
		)

		###

		normalized_postposition_proportion = round(
			(REF_TEXT_SIZE * float(sum(registry.postposition_counts) / doc_length)), 2
		)
		print("POSTPOSITIONS_PER_1000 %s" % normalized_postposition_proportion)
		self._add_feat_to_cas(
			cas,
			"Postpositions_per_1k_tokens",
			NUM_FEATURE,
			normalized_postposition_proportion,
		)

		###

		normalized_relative_pronoun_proportion = round(
			(REF_TEXT_SIZE * float(sum(registry.relative_pronoun_counts) / doc_length)),
			2,
		)
		print("RELATIVE_PRONOUNS_PER_1000 %s" % normalized_relative_pronoun_proportion)
		self._add_feat_to_cas(
			cas,
			"Relative_pronouns_per_1k_tokens",
			NUM_FEATURE,
			normalized_relative_pronoun_proportion,
		)

		###

		# normalized_attributive_pronoun_proportion = round(
		# 	(
		# 		REF_TEXT_SIZE
		# 		* float(sum(registry.attributive_pronoun_counts) / doc_length)
		# 	),
		# 	2,
		# )
		# print(
		# 	"ATTRIBUTIVE_PRONOUNS_PER_1000 %s"
		# 	% normalized_attributive_pronoun_proportion
		# )
		# self._add_feat_to_cas(
		# 	cas,
		# 	"Attributive_pronouns_per_1k_tokens",
		# 	NUM_FEATURE,
		# 	normalized_attributive_pronoun_proportion,
		# )

		###

		# normalized_substituting_pronoun_proportion = round(
		# 	(
		# 		REF_TEXT_SIZE
		# 		* float(sum(registry.substituting_pronoun_counts) / doc_length)
		# 	),
		# 	2,
		# )

		# print(
		# 	"SUBSTITUTING_PRONOUNS_PER_1000 %s"
		# 	% normalized_substituting_pronoun_proportion
		# )
		# self._add_feat_to_cas(
		# 	cas,
		# 	"Substituting_pronouns_per_1k_tokens",
		# 	NUM_FEATURE,
		# 	normalized_substituting_pronoun_proportion,
		# )

		###

		# normalized_pronoun_proportion = round(
		# 	(
		# 		REF_TEXT_SIZE
		# 		* float(
		# 			sum(
		# 				registry.substituting_pronoun_counts
		# 				+ registry.attributive_pronoun_counts
		# 			)
		# 			/ doc_length
		# 		)
		# 	),
		# 	2,
		# )
		# print("PRONOUNS_PER_1000 %s" % normalized_pronoun_proportion)
		# self._add_feat_to_cas(
		# 	cas, "Pronouns_per_1k_tokens", NUM_FEATURE, normalized_pronoun_proportion
		# )

		normalized_personal_pronoun_proportion = round(
			(REF_TEXT_SIZE * float(sum(registry.personal_pronoun_counts) / doc_length)),
			2,
		)
		print("PERSONAL_PRONOUNS_PER_1000 %s" % normalized_personal_pronoun_proportion)
		self._add_feat_to_cas(
			cas,
			"Personal_pronouns_per_1k_tokens",
			NUM_FEATURE,
			normalized_personal_pronoun_proportion,
		)

		print(
			"Dependency length distribution per relation type\n"
			+ pp.pformat(registry.dependency_length_distribution_per_rel_type)
		)
		(
			avg_left_dep_len,
			avg_right_dep_len,
			avg_all_dep_len,
		) = self._get_dependency_lengths_across_all_rels_in_doc(
			registry.dependency_length_distribution_per_rel_type
		)

		print("average dependency length leftward %s" % avg_left_dep_len)
		self._add_feat_to_cas(
			cas, "Average_Dependency_Length_Left", NUM_FEATURE, avg_left_dep_len
		)

		print("average dependency length rightward %s" % avg_right_dep_len)
		self._add_feat_to_cas(
			cas, "Average_Dependency_Length_Right", NUM_FEATURE, avg_right_dep_len
		)

		print("average dependency length all %s" % avg_all_dep_len)
		self._add_feat_to_cas(
			cas, "Average_Dependency_Length_All", NUM_FEATURE, avg_all_dep_len
		)

		avg_max_dep_len = round(float(sum(registry.max_dep_lengths)/len(registry.max_dep_lengths)),2)

		print("average max dependency length all %s based on %s" %(str(avg_max_dep_len),str(registry.max_dep_lengths)))
		self._add_feat_to_cas(
			cas, "Average_Maximal_Dependency_Length", NUM_FEATURE, avg_max_dep_len
		)


		print("sent lengths %s" % registry.sent_lengths)
		avg_sent_len = round(
			float(sum(registry.sent_lengths)) / len(registry.sent_lengths), 2
		)
		self._add_feat_to_cas(cas, "Average_Sentence_Length", NUM_FEATURE, avg_sent_len)

		print("tree_depths %s" % registry.tree_depths)
		avg_tree_depth = round(
			float(sum(registry.tree_depths)) / len(registry.tree_depths), 2
		)
		self._add_feat_to_cas(cas, "Average_Tree_Depth", NUM_FEATURE, avg_tree_depth)

		###

		assert len(registry.sent_lengths) == len(registry.finite_verb_counts)
		no_fin_verb_count = registry.finite_verb_counts.count(0)
		proportion_s_without_fin_verb = round(
			float(no_fin_verb_count) / len(registry.sent_lengths), 2
		)
		print("Proportion_S_without_finite_verb %s" % proportion_s_without_fin_verb)
		self._add_feat_to_cas(
			cas,
			"Proportion_S_without_finite_verb",
			NUM_FEATURE,
			proportion_s_without_fin_verb,
		)
		

		###

		print("finite_verb_counts %s" % registry.finite_verb_counts)
		try:
			avg_finite_verbs = round(
				float(sum(registry.finite_verb_counts))
				/ len(registry.finite_verb_counts),
				2,
			)
		except:
			avg_finite_verbs = 0
		self._add_feat_to_cas(
			cas, "Average_Number_Of_Finite_Verbs", NUM_FEATURE, avg_finite_verbs
		)

		###

		print("total_verb_counts %s" % registry.total_verb_counts)
		try:
			avg_verb_count = round(
				float(sum(registry.total_verb_counts))
				/ len(registry.total_verb_counts),
				2,
			)
		except:
			avg_verb_count = 0
		self._add_feat_to_cas(
			cas, "Average_Number_Of_Verbs", NUM_FEATURE, avg_verb_count
		)

		###

		try:
			proportion_modal_verbs_out_of_all_verbs = round(
				float(
					sum(registry.modal_verb_counts) / sum(registry.total_verb_counts)
				),
				2,
			)
		except:
			proportion_modal_verbs_out_of_all_verbs = 0.0

		print(
			"share of modal verbs %s" % (str(proportion_modal_verbs_out_of_all_verbs))
		)
		self._add_feat_to_cas(
			cas,
			"Proportion_of_modal_verbs_out_of_all_verbs",
			NUM_FEATURE,
			proportion_modal_verbs_out_of_all_verbs,
		)

		###

		no_verb_count = registry.total_verb_counts.count(0)
		proportion_s_without_verb = round(
			float(no_verb_count) / len(registry.sent_lengths), 2
		)
		print("Proportion_S_without_verb %s" % proportion_s_without_verb)
		self._add_feat_to_cas(
			cas, "Proportion_S_without_verb", NUM_FEATURE, proportion_s_without_verb
		)

		###

		bracket_ctr = Counter(registry.verbal_bracket_cands)
		totcands = sum(bracket_ctr.values())
		proportion_of_missing_brackets = round(float(bracket_ctr[999] / totcands), 2)
		proportion_of_switched_brackets = round(float(bracket_ctr[-1] / totcands), 2)
		proportion_of_standard_sequenced_brackets = round(
			float((bracket_ctr[0] + bracket_ctr[1]) / totcands), 2
		)
		proportion_of_brackets_with_emtpy_midfields = round(
			float(bracket_ctr[0] / (bracket_ctr[0] + bracket_ctr[1])), 2
		)

		print("Proportion_of_missing_brackets %s" % proportion_of_missing_brackets)
		self._add_feat_to_cas(
			cas,
			"Proportion_of_missing_verbal_brackets",
			NUM_FEATURE,
			proportion_of_missing_brackets,
		)

		print("Proportion_of_switched_brackets %s" % proportion_of_switched_brackets)
		self._add_feat_to_cas(
			cas,
			"Proportion_of_switched_brackets",
			NUM_FEATURE,
			proportion_of_switched_brackets,
		)

		print(
			"Proportion_of_canonical_brackets %s"
			% proportion_of_standard_sequenced_brackets
		)
		self._add_feat_to_cas(
			cas,
			"Proportion_of_canonical_brackets",
			NUM_FEATURE,
			proportion_of_standard_sequenced_brackets,
		)

		print(
			"Proportion_of_brackets_with_empty_midfields %s"
			% proportion_of_brackets_with_emtpy_midfields
		)
		self._add_feat_to_cas(
			cas,
			"Proportion_of_brackets_with_empty_midfields",
			NUM_FEATURE,
			proportion_of_brackets_with_emtpy_midfields,
		)

		###

		sb4v_ctr = Counter(registry.position_of_subj_relative_to_vfin)

		try:
			share_of_s_vfin_inversions = round(
				float(sb4v_ctr[1] / (sb4v_ctr[1] + sb4v_ctr[-1])), 2
			)
		except:
			share_of_s_vfin_inversions = 0.0

		self._add_feat_to_cas(
			cas,
			"Proportion_of_Subj_Vfin_Inversions",
			NUM_FEATURE,
			share_of_s_vfin_inversions,
		)

		###

		try:
			share_of_subjectless_finite_verbs = round(
				float(registry.subj_less_verbs / (sb4v_ctr[1] + sb4v_ctr[-1])), 2
			)
		except:
			share_of_subjectless_finite_verbs = 0.0

		self._add_feat_to_cas(
			cas,
			"Proportion_of_subjectless_finite_verbs",
			NUM_FEATURE,
			share_of_subjectless_finite_verbs,
		)

		###

		coord_between_V_ctr = Counter(registry.coordination_is_between_verbs)
		print("coordination_is_between_verbs %s" % coord_between_V_ctr)
		try:
			share_of_verbal_coordinations = round(
				float(
					coord_between_V_ctr[True]
					/ (coord_between_V_ctr[False] + coord_between_V_ctr[True])
				),
				2,
			)
		except:
			share_of_verbal_coordinations = 0.0

		self._add_feat_to_cas(
			cas,
			"Proportion_of_coordination_between_verbs",
			NUM_FEATURE,
			share_of_verbal_coordinations,
		)

		###

		print("lex_np_sizes %s" % registry.lex_np_sizes)
		try:
			avg_lex_np_size = round(
				float(sum(registry.lex_np_sizes)) / len(registry.lex_np_sizes), 2
			)
		except:
			avg_lex_np_size = 0
		self._add_feat_to_cas(
			cas, "Average_Size_Of_Lexical_NP", NUM_FEATURE, avg_lex_np_size
		)

		###

		return True

	def _add_feat_to_cas(self, cas, name, featpath, value):
		F = self.ts.get_type(featpath)
		feature = F(name=name, value=value)
		cas.add(feature)

	def _register_stuff(self, cas, registry: StuffRegistry, sent):
		udapi_doc = Document()
		cas_in_str_form = cas_to_str(cas, sent)
		udapi_doc.from_conllu_string(cas_in_str_form)
		sct = 1
		# udapi_doc.from_conllu_string(TEST_STRING)
		for bundle in udapi_doc.bundles:
			tree = bundle.get_tree()


			self._annotate_distant_verbal_brackets(tree,cas)

			# finite verbs are identifed by their xpos-tag; we're not looking at any info in the morphological feats
			registry.finite_verb_counts.append(
				self._count_nodes_with_specified_values_for_feat(
					tree, "xpos", [".*FIN"]
				)
			)

			DEFAULT_CONJ = "und"
			registry.rels_of_conjunctions += self._get_uses_of_conjunctions(
				DEFAULT_CONJ, tree
			)

			# all verbal forms have a pos-Tag beginning with "V"
			registry.total_verb_counts.append(
				self._count_nodes_with_specified_values_for_feat(tree, "xpos", ["V.*"])
			)

			registry.modal_verb_counts.append(
				self._count_nodes_with_specified_values_for_feat(tree, "xpos", ["VM.*"])
			)

			relative_position_of_subj_and_verb = (
				self._check_position_of_subj_relative_to_vfin(tree)
			)
			registry.position_of_subj_relative_to_vfin.extend(
				[x for x in relative_position_of_subj_and_verb if not x == 0]
			)

			registry.subj_less_verbs.append(relative_position_of_subj_and_verb.count(0))

			registry.coordination_is_between_verbs.extend(
				self._check_verbal_coordination(tree)
			)

			registry.verbal_bracket_cands.extend(
				self._check_verbal_bracket_configurations(tree)
			)

			# registry.attributive_pronoun_counts.append(
			# 	self._count_nodes_with_specified_values_for_feat(
			# 		tree, "xpos", ["PPOSAT|PIAT|PDAT|PIDAT|PRELAT|PWAT"]
			# 	)
			# )
			# registry.substituting_pronoun_counts.append(
			# 	self._count_nodes_with_specified_values_for_feat(
			# 		tree,
			# 		"xpos",
			# 		["PPER|PRF|PIS|PPOS|PDS|PRELS|PWS"],  # leaving out PWAV!
			# 	)
			# )

			registry.personal_pronoun_counts.append(
				self._count_nodes_with_specified_values_for_feat(
					tree, "xpos", ["PPER|PRF"]
				)
			)

			registry.adposition_counts.append(
				self._count_nodes_with_specified_values_for_feat(
					tree, "xpos", ["APPR|APPRART|APPO|APZR"]
				)
			)
			registry.postposition_counts.append(
				self._count_nodes_with_specified_values_for_feat(tree, "xpos", ["APPO"])
			)

			registry.preposition_counts.append(
				self._count_nodes_with_specified_values_for_feat(
					tree, "xpos", ["APPR|APPRART"]
				)
			)

			registry.relative_pronoun_counts.append(
				self._count_nodes_with_specified_values_for_feat(
					tree, "xpos", ["PRELAT|PRELS"]
				)
			)

			registry.subordinator_counts.append(
				self._count_nodes_with_specified_values_for_feat(
					tree, "xpos", ["KOUI|KOUS"]
				)
			)

			registry.conjunction_counts.append(
				self._count_nodes_with_specified_values_for_feat(tree, "xpos", ["KON"])
			)

			registry.tree_depths.append(self._get_max_subtree_depth(tree))
			registry.sent_lengths.append(len(tree.descendants))
			registry.lex_np_sizes.extend(self._get_lex_np_sizes(tree))


			
			dep_counts_for_posclasses = self._get_dep_counts_for_specified_classes_of_stts_tags(tree, 
			{"FINITE_VERBS_STTS_BROAD":FINITE_VERBS_STTS_BROAD, 'NONFINITE_VERBS_STTS_BROAD':NONFINITE_VERBS_STTS_BROAD,
			'LEXICAL_NOUNS_STTS':TIGER_LEX_NOUN_POS})
			
			registry.dependents_count_distribution_per_verb_type = (
                self._merge_sentwise_counts_into_global_counts(
                    dep_counts_for_posclasses,
                    registry.dependents_count_distribution_per_verb_type,
                )
			)

			(sent_wise_dep_len_dist, dir_lens) = self._get_dep_dist(tree)
			print(
				"directed lengths for sentence %s: %s, %s left and %s right "
				% (sct, dir_lens, len(dir_lens["l"]), len(dir_lens["r"]))
			)

			# TODO _get_max_dep_length
			registry.max_dep_lengths.append(self._get_max_dep_length(tree))

			registry.dependency_length_distribution_per_rel_type = (
				self._merge_sentwise_counts_into_global_counts(
					sent_wise_dep_len_dist,
					registry.dependency_length_distribution_per_rel_type,
				)
			)

	def _merge_sentwise_counts_into_global_counts(self, sentwise_dist, global_dist):
		for rel in sentwise_dist.keys():
			if rel not in global_dist:
				global_dist[rel] = Counter()
			global_dist[rel].update(sentwise_dist[rel])
		return global_dist

	def _get_average_from_counter(self, mycounter):
		"""get average value from counter"""
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


	def _get_filtered_children(self,node,excluded_rels):
		return [tuple([child.form,child.deprel]) for child in node.children if not child.deprel.lower() in excluded_rels]


	def _get_dep_counts_for_specified_classes_of_stts_tags(self,node, dict_of_postypelists,excluded_rels=["punct", "--"]):
		#print("On s %s " %node.print_subtree())
		list_of_postypelists = list(dict_of_postypelists.values())
		child_counts_per_type={}
		for d in node.descendants:
			for kee in dict_of_postypelists:
				if d.xpos in dict_of_postypelists[kee]:
					if kee not in child_counts_per_type:
						child_counts_per_type[kee]=[]
					acceptable_child_count = self._get_filtered_children(d,excluded_rels)
					child_counts_per_type[kee].append(len(acceptable_child_count))
		#print("child counts per type %s" %(str(child_counts_per_type)))
		return child_counts_per_type
	# def get_dependency_lengths_across_all_rels_in_doc(counts_per_rel):
	def _get_dependency_lengths_across_all_rels_in_doc(
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
					if not abs(kee) in leftward:
						leftward[abs(kee)] = 0
					leftward[abs(kee)] += ctr[kee]
				elif kee > 0:
					# rightward.update({kee: ctr[kee]})
					if not kee in rightward:
						rightward[kee] = 0
					rightward[kee] += ctr[kee]
				else:
					continue

		anydir = leftward + rightward

		avg_left = self._get_average_from_counter(leftward)
		avg_right = self._get_average_from_counter(rightward)
		avg_all = self._get_average_from_counter(anydir)
		return (avg_left, avg_right, avg_all)

	def _get_max_subtree_depth(self, node: Node) -> int:
		"""determine depth of the subtree rooted at the given node"""
		return max([child._get_attr("depth") for child in node.descendants])

	def _count_nodes_with_specified_values_for_feat(
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


	def _get_max_dep_length(self,node, excluded_rels=["root","punct"]) -> int:
		""" return the longest dependency length in the subtree rooted at the given node"""
		deplens = []
		for d in node.descendants:
			if d.deprel.lower() in excluded_rels:
				continue
			deplens.append(abs(d.ord - d.parent.ord))
		if len(deplens)>0:
			return max(deplens)
		else:
			return 1
		#return max(max([ abs(d.ord - d.parent.ord) for d in node.descendants if d.deprel.lower() not in excluded_rels]),1)


	def _get_dep_dist(self, node, excluded_rels=["root"]) -> Dict:
		"""Update the document-level distribution of dependency lenghts per dependency type by processing the nodes in the tree.
		Dep length is the difference between the indices of the head and the dependent. Deps adjacent to their heads have a dep length of |1| , etc.
		The values can be pos and neg: they're positive if the dependent is to the right of the head, and negative if it's the other way around.
		We're not merging the two cases by using absolute values!
		"""
		dep_dist = {}
		all_lens = {"l": [], "r": []}
		for d in node.descendants:
			rel = d.deprel
			if rel.lower() in excluded_rels:
				continue
			cix = d.ord
			pix = d.parent.ord
			diff = cix - pix
			if diff < 0:
				all_lens["l"].append(abs(diff))
			elif diff > 0:
				all_lens["r"].append(diff)
			else:
				continue
			if not rel in dep_dist:
				dep_dist[rel] = Counter()
				# dep_dist[rel][diff]=0
			dep_dist[rel][diff] += 1
		return (dep_dist, all_lens)

	def _get_triples(self, node: Node, feats=["form", "upos"]) -> Generator:
		"""Yields triples of the form: (head, dependency_rel, dep) where head and dep are tuples
		containing the attributes specified in the feats parameter.
		Default feats are "form" and "upos".
		"""
		head = tuple(node.get_attrs(feats, stringify=False))
		for i in node.children:
			dep = tuple(i.get_attrs(feats, stringify=False))
			yield (head, i.deprel, dep)
			yield from self._get_triples(i, feats=feats)

	def _get_lex_np_sizes(
		self, tree: Node, lex_noun_pos_tags=TIGER_LEX_NOUN_POS
	) -> List[int]:
		"""get the number of tokens that make up the lexical noun phrases in the sentence/tree"""
		size_list = []
		for d in tree.descendants:
			if d.xpos in lex_noun_pos_tags:
				n_size = 1 + len(d.descendants)
				size_list.append(n_size)
		return size_list

	def _check_position_of_subj_relative_to_vfin(
		self,
		node: Node,
		finiteverbtags=FINITE_VERBS_STTS_BROAD,
		subjlabels=TIGER_SUBJ_LABELS,
	) -> List[bool]:
		"""
		1 if subject follows verb; -1 if subject precedes verb; 0 if there is no subject for the finite verb in question.
		The lists of pos tags for finite verbs and of subj relation labels may need to be adjusted per tagger/parser used!
		"""
		position_of_s_relative_to_vfin = []
		for d in node.descendants:
			if d.xpos in finiteverbtags:
				for kid in d.children:
					rel_pos = 0
					if kid.deprel.upper() in subjlabels:
						if kid.ord > d.ord:
							rel_pos = 1
						else:
							rel_pos = -1
					position_of_s_relative_to_vfin.append(rel_pos)
		return position_of_s_relative_to_vfin

	def _get_uses_of_conjunctions(self, curr_lemma: str, node: Node) -> Counter:
		"""retrieve the rels of a particular conjunction"""
		conjrelctr = Counter()
		for d in node.descendants:
			print("d.lemma %s curr_lemma %s" % (d.lemma, curr_lemma))
			if re.match(re.escape(d.lemma), curr_lemma):
				conjrelctr[d.deprel] += 1

		return conjrelctr

	def _check_verbal_bracket_configurations(
		self,
		node: Node,
		finitemodeauxtags=FINITE_MOD_AUX_STTS,
		nonfinitetags=NONFINITE_VERBS_STTS_BROAD,
	):
		"""
		Check if modals and auxiliaries are part of verbal brackets with infinitives in RSK or not.
		We return
		999 if there is no bracket
		0 if there is a bracket and the midfield is empty (e.g. er hat gesagt, ...)
		1 if there is a bracket and the midfield is  not empty (e.g. er hat das gesagt)
		-1 if the non-finite verb is to the left of the finite form (e.g. Wollen kann man vieles.)
		Method assumes STTS POS tags.
		"""
		bracket_candidates = []
		for d in node.descendants:
			if d.xpos in finitemodeauxtags:
				infdep = None
				for kid in d.children:
					if kid.xpos in nonfinitetags:
						infdep = kid
				if infdep is None:
					pass
					# bracket_candidates.append(999)
				else:
					if infdep.ord > d.ord:
						if infdep.ord - d.ord == 1:
							bracket_candidates.append(0)
						else:
							bracket_candidates.append(1)
					else:

						bracket_candidates.append(-1)
		return bracket_candidates

	def _check_verbal_coordination(
		self,
		node: Node,
		verbtags=ALL_VERB_TAGS_STTS,
		conjtags=["KON"],
		coordinator_rel="cd",
		conjunct_rel="cj",
	) -> List[bool]:
		"""
		Check whether conjunctions coordinate verbal elements .
		Method assumes Tiger syntax.
		"""
		coordination_is_between_verbs = []
		for concand in node.descendants:
			if concand.xpos in conjtags and concand.deprel == coordinator_rel:
				parent = concand.parent
				if not parent.xpos in verbtags:
					coordination_is_between_verbs.append(False)
				else:
					found_match = False
					for child in concand.children:

						if child.xpos in verbtags and child.deprel == conjunct_rel:
							found_match = True
					if found_match == True:
						coordination_is_between_verbs.append(True)
					else:
						coordination_is_between_verbs.append(False)
		return coordination_is_between_verbs
