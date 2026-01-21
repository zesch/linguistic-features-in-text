from cassis import *
from cassis.typesystem import FeatureStructure
from udapi.core.node import Node
from udapi.core.document import Document
import re
from py_lift.utils.conllu import cas_to_str
from collections import Counter
from typing import List, Dict, Union, Generator, Tuple
from py_lift.dkpro import *

class TreeBuilder:

    def build_tree(self, cas: Cas, sent: FeatureStructure) -> Node:
        udapi_doc = Document()
        udapi_doc.from_conllu_string(cas_to_str(cas, sent))
        if len(udapi_doc.bundles) > 1:
            raise ValueError("Multiple bundles per sentence are not supported.")

        return udapi_doc.bundles[0].get_tree()

    def build_trees(self, cas: Cas) -> list[Node]:
        forest = []
        for sent in cas.select(T_SENT):
            forest.append(self.build_tree(cas, sent))
        return forest


    def _get_filtered_children(self, node, excluded_rels):
        return [
            tuple([child.form, child.deprel])
            for child in node.children
            if not child.deprel.lower() in excluded_rels
        ]

    def _get_max_subtree_depth(self, node: Node) -> int:
        """Determine depth of the subtree rooted at the given node.
        This is counted as the number of edges to traverse from `node` to the root node.
        """
        return max([child._get_attr("depth") for child in node.descendants])

    def _get_max_dep_length(self, node, excluded_rels=["root", "punct"]) -> int:
        """return the longest dependency length in the subtree rooted at the given node"""
        deplens = []
        for d in node.descendants:
            if d.deprel.lower() in excluded_rels:
                continue
            deplens.append(abs(d.ord - d.parent.ord))
        if len(deplens) > 0:
            return max(deplens)
        else:
            return 1
        # return max(max([ abs(d.ord - d.parent.ord) for d in node.descendants if d.deprel.lower() not in excluded_rels]),1)

    # def _get_dep_dist(self, node, excluded_rels=["root"]) -> Dict:
    #     """Update the document-level distribution of dependency lenghts per dependency type by processing the nodes in the tree.
    #     Dep length is the difference between the indices of the head and the dependent. Deps adjacent to their heads have a dep length of |1| , etc.
    #     The values can be pos and neg: they're positive if the dependent is to the right of the head, and negative if it's the other way around.
    #     We're not merging the two cases by using absolute values!
    #     """
    #     dep_dist = {}
    #     all_lens = {"l": [], "r": []}
    #     for d in node.descendants:
    #         rel = d.deprel
    #         if rel.lower() in excluded_rels:
    #             continue
    #         cix = d.ord
    #         pix = d.parent.ord
    #         diff = cix - pix
    #         if diff < 0:
    #             all_lens["l"].append(abs(diff))
    #         elif diff > 0:
    #             all_lens["r"].append(diff)
    #         else:
    #             continue
    #         if not rel in dep_dist:
    #             dep_dist[rel] = Counter()
    #             # dep_dist[rel][diff]=0
    #         dep_dist[rel][diff] += 1
    #     return (dep_dist, all_lens)

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

    # def _get_lex_np_sizes(
    #     self, tree: Node, lex_noun_pos_tags=TIGER_LEX_NOUN_POS
    # ) -> List[int]:
    #     """get the number of tokens that make up the lexical noun phrases in the sentence/tree"""
    #     size_list = []
    #     for d in tree.descendants:
    #         if d.xpos in lex_noun_pos_tags:
    #             n_size = 1 + len(d.descendants)
    #             size_list.append(n_size)
    #     return size_list

    def _check_position_of_subj_relative_to_vfin(
        self,
        node: Node,
        finiteverbtags,
        subjlabels,
    ) -> List[bool]:
        """
        For eachf finite verb in the sentence/tree determine the relative order of subject and finite verb.
        1 if subject follows verb; -1 if subject precedes verb; 0 if there is no subject for the finite verb in question.
        We return a list  because there can be multiple finite verbs in the sentence.

        Finiteness is being determined by fine-grained POS-Tag in a conllu tree

        The lists of pos tags for finite verbs and of subj relation labels may need to be adjusted per tagger/parser used.
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
        finitemodeauxtags,
        nonfinitetags,
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
        verbtags,
        conjtags,
        coordinator_rel="cd",
        conjunct_rel="cj",
    ) -> List[bool]:
        """
        Check whether conjunctions coordinate verbal elements.
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