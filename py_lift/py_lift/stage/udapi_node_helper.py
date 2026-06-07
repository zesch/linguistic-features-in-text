import copy
import logging
import operator as op
import os

import pprint as pp
import re
import sys
from typing import Dict, List, Tuple, Union

from udapi.core.document import Document
from udapi.core.node import Node

from py_lift.stage.constants import get_logger

logger = get_logger(__name__)

# since not all wh-words are potentially embedded in larger phrases
# we have a small list as well
POT_EMBEDDED_WH_WORDS = [
    "wer",
    "wann",
    "wen",  # in case of weird lemmatization
    "wem",  #  in case of weird lemmatization
    "was",
    "wessen",
    "welcher",
    "wie",
    "welcherlei",
    "welcherart",
]

POT_QUESTION_EMBEDDING_PREDS = [
    "fragen",
    "wissen",
    "sagen",
    "vorhersagen",
    "voraussagen",
    "bestimmen",
    "Frage",
    "Vermutung",
    "Verdacht",
    "erinnern",
    "vergessen",
    "herausfinden",
    "rausfinden",
    "raten",
    "mitteilen",
]


TUEBA_2_SIMPLE_TOPO = {
    "C": "LSK",
    "FKONJ": "X_rels",
    "FKOORD": "X_rels",
    "KOORD": "X_rels",
    "LV": "X_rels",
    "LK": "LSK",
    "MF": "MF_rels",
    "NF": "NF_rels",
    "null": "null",
    "PARORD": "X_rels",
    "VC": "RSK",
    "VCE": "RSK",
    "VF": "VF_rels",
}

AUX_LEMMAS = ["sein", "haben"]

MODAL_LEMMAS = [
    "müssen",
    "muss",  # for mis-lemmatizations
    "können",
    "sollen",
    "werden",
    "dürfen",
    "mögen",
    "wollen",
]


PRONOMINAL_ADVERBS = ["daran", "darauf", "daraus", "darüber", "davon", "darum", "davor"]

SIMPLEWH = [
    "wer",
    "wann",
    "wem",
    "wen",
    "warum",
    "was",
    "wo",
    "wofür",
    "wohin",
    "woher",
    "wozu",
    "womit",
    "wobei",
    "wie",
    "worauf",
    "woran",
    "worunter",
    "worüber",
    "wonach",
    "wodurch",
    "wogegen",
    "weswegen",
    "weshalb",
    "welcher",
    "welcherlei",
    "welcherart",
    "inwiefern",
]

FINITE_VERB_POS = ["VVFIN", "VVIMP", "VMFIN", "VAFIN", "VMIMP", "VAIMP"]
LEXFINITE_VERB_POS = ["VVFIN", "VVIMP"]

COP_LEMMAS = ["werden", "sein"]

MATRIX_DEPTH = 1

FINAL_PUNCT = [".", "!", "?"]


def has_that_complementizer(node):
    for kid in node.children:
        if kid.form.lower() in ["dass", "daß"] and kid.deprel == "mark":
            return True
    return False


def has_non_that_subordinator(node):
    for kid in node.children:
        if kid.deprel == "mark" and kid.form.lower() not in ["dass", "daß"]:
            return True
    return False


def clause_gov_has_pronominal_adverb_as_child(child_node):
    node = child_node.parent
    for kid in node.children:
        if (
            kid.form.lower() in PRONOMINAL_ADVERBS
            and kid.upos == "ADV"
            and kid.deprel == "advmod"
        ):
            return True
    return False


def read_conllu_doc_to_udapi_doc(infile):
    """read a single conllu file into a udapi document"""

    basename = os.path.basename(infile)
    document = Document(filename=infile)
    docid = re.sub(r"\.conllu", "", basename)

    return (document, docid)


def read_udapi_doc_from_conllu_string(cstring):
    udapi_doc = Document()
    udapi_doc.from_conllu_string(cstring)
    logger.debug("read conllu into udapi")
    return udapi_doc


def return_conllu_string_from_file(conllufile):
    docid = re.split("_", os.path.basename(conllufile))[0]
    with open(conllufile, "r") as f:
        input = f.readlines()
    return ("".join(input), docid)


def reduce_field_contents_to_tops(field_2_node_map):
    for field in field_2_node_map:
        fillers = field_2_node_map[field]
        field_2_node_map[field] = eliminate_non_tops(fillers)
    return field_2_node_map


def map_all_children_to_fields(semroot, field_2_node_map, logger):
    for child in semroot.children:
        logger.debug("honey_chile " + child.form)

        # childrel= child.deprel
        fieldval = TUEBA_2_SIMPLE_TOPO[child.misc["TopoField"]]
        field_2_node_map[fieldval].add(child)
    return field_2_node_map


def get_depth_of_node(node: Node) -> int:
    return node._get_attr("depth")


def get_nodes_per_field(node, semroot, logger):
    """create a map from field labels to sets of top nodes in the field"""
    field_2_node_map = {}
    node_depth = get_depth_of_node(node)
    sr_depth = get_depth_of_node(semroot)
    sr_field = semroot.misc["TopoField"]
    node_field = node.misc["TopoField"]
    logger.info(
        "map fields to nodes, centered on node %s/%s/%s and semroot %s/%s/%s",
        node.form,
        node_field,
        node_depth,
        semroot.form,
        sr_field,
        sr_depth,
    )

    # set a key for each field
    for fld in set(TUEBA_2_SIMPLE_TOPO.values()):
        field_2_node_map[fld] = set()

    # NB: simple tense , matrix copular clause, non-verbal pred before copula
    if (
        node != semroot
        and node.xpos.endswith("FIN")
        and node.lemma in COP_LEMMAS
        and node.deprel == "cop"
        and (not semroot.xpos.startswith("V"))
        and sr_depth == MATRIX_DEPTH
    ):
        logger.info("non-verbal pred and copula in clause")
        if node.ord > semroot.ord:
            field_2_node_map["MF_rels"].add(semroot)
        elif semroot.ord < node.ord:
            field_2_node_map["VF_rels"].add(semroot)
        field_2_node_map = map_all_children_to_fields(semroot, field_2_node_map, logger)

    # text = Petra ist Krankenschwester gewesen .
    # 1 Petra   Petra   PROPN   NE  Case=Nom|Gender=Fem|Number=Sing 3   NSUBJ   _   TopoField=VF
    # 2 ist sein    AUX VAFIN   Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin   3   AUX _   TopoField=LK
    # 3 Krankenschwester    Krankenschwester    NOUN    NN  Case=Nom|Gender=Fem|Number=Sing 0   ROOT    _   TopoField=MF
    # 4 gewesen sein    AUX VAPP    _   3   COP _   TopoField=VC
    # 5 .   .   PUNCT   $.  _   3   PUNCT   _   TopoField=null

    # NB: complex tense , matrix copular clause, relative order of semroot and finite verb unspecified
    elif (
        node != semroot
        and node.xpos.endswith("FIN")
        and node.lemma in COP_LEMMAS
        and node.deprel == "aux"
        and (not semroot.xpos.startswith("V"))
        and sr_depth == MATRIX_DEPTH
        and has_child_with_given_rel(semroot, "cop")
    ):
        logger.info("COMPLEX TENSE COPULAR CLAUSE")
        if semroot.ord > node.ord:
            field_2_node_map["MF_rels"].add(semroot)
        elif semroot.ord < node.ord:
            field_2_node_map["VF_rels"].add(semroot)
        else:
            pass
        field_2_node_map = map_all_children_to_fields(semroot, field_2_node_map, logger)

    # NB: modal + copula + non-verbal pred in embedded clause
    elif (
        node != semroot
        and node.xpos.endswith("FIN")
        and node.lemma in MODAL_LEMMAS
        and node.deprel == "aux"
        and (not semroot.xpos.startswith("V"))
        and has_child_with_given_rel(semroot, "cop")
        and sr_depth > MATRIX_DEPTH
    ):
        logger.info("modal + copula + non-verbal pred in non-matrix clause")
        fieldval = TUEBA_2_SIMPLE_TOPO[semroot.misc["TopoField"]]
        field_2_node_map[fieldval].add(semroot)

        field_2_node_map = map_all_children_to_fields(semroot, field_2_node_map, logger)

    # NB: simple-tense, unmarked finite matrix clause with lexical verb
    if (
        node == semroot
        and (
            node.xpos in LEXFINITE_VERB_POS
            or node.lemma not in AUX_LEMMAS + MODAL_LEMMAS
        )
        and sr_depth == MATRIX_DEPTH
        and not has_child_with_given_rel(semroot, "mark")
    ):
        logger.info("simple-tense, finite matrix clause with lexical verb")
        for child in semroot.children:
            logger.debug("honey_chile " + child.form)

            childrel = child.deprel
            fieldval = TUEBA_2_SIMPLE_TOPO[child.misc["TopoField"]]

            if childrel == "ccomp" and fieldval == "RSK" and child.ord > semroot.ord:
                field_2_node_map["NF_rels"].add(child)
            elif childrel == "ccomp" and fieldval == "RSK" and child.ord < semroot.ord:
                field_2_node_map["VF_rels"].add(child)

            elif (
                childrel == "compound:prt"
                and fieldval == "RSK"
                and child.ord > semroot.ord
            ):
                field_2_node_map["NF_rels"].add(child)
            elif childrel == "compound:prt" and child.ord < node.ord:
                field_2_node_map["VF_rels"].add(child)

            elif (
                childrel == "xcomp"
                and child.xpos.startswith("V")
                and child.ord < node.ord
            ):
                field_2_node_map["VF_rels"].add(child)

            # Q:  put advcl in X_rels?
            elif childrel == "advcl" and child.ord < node.ord:
                field_2_node_map["VF_rels"].add(child)
            elif childrel == "advcl" and child.ord > node.ord:
                field_2_node_map["NF_rels"].add(child)

            elif childrel == "conj" and fieldval in ["LSK", "RSK"]:
                pass

            else:
                field_2_node_map[fieldval].add(child)

        field_2_node_map = reduce_field_contents_to_tops(field_2_node_map)
        field_2_node_map[TUEBA_2_SIMPLE_TOPO[semroot.misc["TopoField"]]].add(semroot)

    # NB: V-initial subordinate clause with lexical verb
    elif (
        node == semroot
        and (
            node.xpos in LEXFINITE_VERB_POS
            or node.lemma not in AUX_LEMMAS + MODAL_LEMMAS
        )
        and sr_depth > MATRIX_DEPTH
        and node.deprel == "advcl"
        and not has_child_with_given_rel(semroot, "mark")
    ):
        logger.info(
            "finite subordinate clause with lexical verb; special v1-adverbial clauses"
        )
        field_2_node_map[TUEBA_2_SIMPLE_TOPO[semroot.misc["TopoField"]]].add(semroot)

        for child in semroot.children:
            logger.debug("honey_chile " + child.form)

            childrel = child.deprel
            fieldval = TUEBA_2_SIMPLE_TOPO[child.misc["TopoField"]]

            if childrel == "ccomp" and fieldval == "RSK" and child.ord > semroot.ord:
                field_2_node_map["NF_rels"].add(child)

            elif (
                childrel == "compound:prt"
                and fieldval == "RSK"
                and child.ord > semroot.ord
            ):
                field_2_node_map["NF_rels"].add(child)

            elif childrel == "conj" and fieldval == "LSK":
                pass

            elif (
                childrel == "advcl"
                and child.xpos.endswith("FIN")
                and child.ord < node.ord
            ):
                field_2_node_map["VF_rels"].add(child)
                # TODO or put advcl in X_rels?
            else:
                field_2_node_map[fieldval].add(child)

        field_2_node_map = reduce_field_contents_to_tops(field_2_node_map)

    # NB: V-initial subordinate clause with aux or modal verb
    elif (
        node != semroot
        and (
            node.xpos not in LEXFINITE_VERB_POS
            or node.lemma in AUX_LEMMAS + MODAL_LEMMAS
        )
        and sr_depth > MATRIX_DEPTH
        and semroot.deprel == "advcl"
        and not has_child_with_given_rel(semroot, "mark")
    ):
        logger.info(
            "finite subordinate clause with lexical verb; special v1-adverbial clauses"
        )
        field_2_node_map[TUEBA_2_SIMPLE_TOPO[semroot.misc["TopoField"]]].add(semroot)

        for child in semroot.children:
            logger.debug("honey_chile " + child.form)

            childrel = child.deprel
            fieldval = TUEBA_2_SIMPLE_TOPO[child.misc["TopoField"]]

            if childrel == "ccomp" and fieldval == "RSK" and child.ord > semroot.ord:
                field_2_node_map["NF_rels"].add(child)

            elif (
                childrel == "compound:prt"
                and fieldval == "RSK"
                and child.ord > semroot.ord
            ):
                field_2_node_map["NF_rels"].add(child)

            elif childrel == "conj" and fieldval == "LSK":
                pass

            elif (
                childrel == "advcl"
                and child.xpos.endswith("FIN")
                and child.ord < node.ord
            ):
                field_2_node_map["VF_rels"].add(child)
                # TODO or put advcl in X_rels?
            else:
                field_2_node_map[fieldval].add(child)

        field_2_node_map = reduce_field_contents_to_tops(field_2_node_map)

    # NB: finite clause with lexical verb in simple tense as parataxis to root clause/unit
    elif (
        node == semroot
        and node.xpos in LEXFINITE_VERB_POS
        and node.deprel in ["parataxis"]
        and sr_depth == MATRIX_DEPTH + 1
    ):
        logger.info("finite clause as parataxis to root clause/unit")
        for child in semroot.children:
            logger.debug("honey_chile " + child.form)
            childrel = child.deprel
            fieldval = TUEBA_2_SIMPLE_TOPO[child.misc["TopoField"]]

            if childrel == "ccomp" and fieldval == "RSK" and child.ord > semroot.ord:
                field_2_node_map["NF_rels"].add(child)

            elif (
                childrel == "compound:prt"
                and fieldval == "RSK"
                and child.ord > semroot.ord
            ):
                field_2_node_map["NF_rels"].add(child)

            elif childrel == "conj" and fieldval == "LSK":
                pass

            else:
                field_2_node_map[fieldval].add(child)

        logger.info("parent %s", node.parent)
        parentfield = TUEBA_2_SIMPLE_TOPO[node.parent.misc["TopoField"]]
        if parentfield == "null" and node.parent.ord < node.ord:
            field_2_node_map["X_rels"].add(node.parent)

        field_2_node_map = reduce_field_contents_to_tops(field_2_node_map)
        field_2_node_map[TUEBA_2_SIMPLE_TOPO[semroot.misc["TopoField"]]].add(semroot)

    # NB: finite clause with lexical verb, coordinated to root clause
    elif (
        node == semroot
        and node.xpos in LEXFINITE_VERB_POS
        and node.deprel in ["conj"]
        and sr_depth == MATRIX_DEPTH + 1
    ):
        logger.info("finite clause coordinated to root clause")
        for child in semroot.children:
            logger.debug("honey_chile " + child.form)
            # field_2_node_map[fieldval].append(w)
            childrel = child.deprel
            fieldval = TUEBA_2_SIMPLE_TOPO[child.misc["TopoField"]]

            if childrel == "ccomp" and fieldval == "RSK" and child.ord > semroot.ord:
                field_2_node_map["NF_rels"].add(child)

            elif childrel == "ccomp" and fieldval == "LSK" and child.ord > semroot.ord:
                field_2_node_map["NF_rels"].add(child)

            elif (
                childrel == "compound:prt"
                and fieldval == "RSK"
                and child.ord > semroot.ord
            ):
                field_2_node_map["NF_rels"].add(child)

            elif childrel == "conj" and fieldval == "LSK":
                pass

            else:
                field_2_node_map[fieldval].add(child)

        field_2_node_map = reduce_field_contents_to_tops(field_2_node_map)
        field_2_node_map[TUEBA_2_SIMPLE_TOPO[semroot.misc["TopoField"]]].add(semroot)

    # NB: subordinate or conjoined simple-tense, matrix clause with lexical verb
    elif (
        node == semroot
        and (
            node.xpos in LEXFINITE_VERB_POS
            or node.lemma not in AUX_LEMMAS + MODAL_LEMMAS
        )
        and sr_depth > MATRIX_DEPTH
    ):
        logger.info(
            "subordinate or conjoined simple-tense, matrix clause with lexical verb"
        )
        for child in semroot.children:
            logger.debug("honey_chile " + child.form)

            childrel = child.deprel
            fieldval = TUEBA_2_SIMPLE_TOPO[child.misc["TopoField"]]

            if childrel == "ccomp" and fieldval == "RSK" and child.ord > semroot.ord:
                field_2_node_map["NF_rels"].add(child)

            elif (
                childrel == "ccomp" and child.ord < semroot.ord
            ):  # and fieldval == "RSK"
                field_2_node_map["VF_rels"].add(child)

            elif childrel == "ccomp" and fieldval == "LSK" and child.ord > semroot.ord:
                field_2_node_map["NF_rels"].add(child)

            elif (
                childrel == "compound:prt"
                and fieldval == "RSK"
                and child.ord > semroot.ord
            ):
                field_2_node_map["NF_rels"].add(child)

            elif childrel == "compound:prt" and child.ord < node.ord:
                field_2_node_map["VF_rels"].add(child)

            elif childrel == "conj" and fieldval in ["LSK", "RSK"]:
                pass

            # Q:  put advcl in X_rels?
            elif childrel == "advcl" and child.ord < node.ord:
                field_2_node_map["VF_rels"].add(child)

            elif childrel == "advcl" and child.ord > node.ord:
                field_2_node_map["NF_rels"].add(child)

            elif (
                childrel == "xcomp"
                and child.xpos.startswith("V")
                and child.ord < node.ord
            ):
                field_2_node_map["VF_rels"].add(child)

            else:
                field_2_node_map[fieldval].add(child)

        field_2_node_map = reduce_field_contents_to_tops(field_2_node_map)
        field_2_node_map[TUEBA_2_SIMPLE_TOPO[semroot.misc["TopoField"]]].add(semroot)

    # NB: modals such as haben or wollen used as full verbs, tho tagged as aux/mod
    elif (
        node == semroot
        and node.lemma == "haben"
        and node.xpos == "VAFIN"
        and sr_depth >= MATRIX_DEPTH
    ) or (
        node == semroot
        and node.lemma in ["können", "wollen"]
        and node.xpos == "VMFIN"
        and sr_depth >= MATRIX_DEPTH
    ):
        logger.info(
            "modals such as haben or wollen used as full verbs, tho tagged as aux/mod"
        )

        for child in semroot.children:
            logger.debug("honey_chile " + child.form)
            # field_2_node_map[fieldval].append(w)
            childrel = child.deprel
            fieldval = TUEBA_2_SIMPLE_TOPO[child.misc["TopoField"]]

            if childrel == "ccomp" and fieldval == "RSK" and child.ord > semroot.ord:
                field_2_node_map["NF_rels"].add(child)

            elif (
                childrel == "compound:prt"
                and fieldval == "RSK"
                and child.ord > semroot.ord
            ):
                field_2_node_map["NF_rels"].add(child)

            elif childrel == "conj" and fieldval == "LSK":
                pass

            elif childrel == "xcomp" and fieldval == "RSK" and child.ord > semroot.ord:
                field_2_node_map["MF_rels"].add(child)

            else:
                field_2_node_map[fieldval].add(child)

        field_2_node_map = reduce_field_contents_to_tops(field_2_node_map)
        # for field in field_2_node_map:
        #   fillers = field_2_node_map[field]
        #   field_2_node_map[field] = eliminate_non_tops(fillers)
        field_2_node_map[TUEBA_2_SIMPLE_TOPO[semroot.misc["TopoField"]]].add(semroot)

    # NB: simple finite lexical verb in RSK within marked clause => VEND
    if (
        node == semroot
        and node.xpos.endswith("FIN")
        and TUEBA_2_SIMPLE_TOPO[node.misc["TopoField"]] == "RSK"
        and has_child_with_given_rel(semroot, "mark")
    ):
        logger.info("simple finite lexical verb in RSK => VEND")
        field_2_node_map[TUEBA_2_SIMPLE_TOPO[semroot.misc["TopoField"]]].add(semroot)
        for child in semroot.children:
            childrel = child.deprel
            fieldval = TUEBA_2_SIMPLE_TOPO[child.misc["TopoField"]]
            logger.info("child_node %s in field %s ", child.form, fieldval)
            if childrel == "ccomp" and fieldval == "RSK" and child.ord > semroot.ord:
                field_2_node_map["NF_rels"].add(child)
            elif childrel == "xcomp" and fieldval == "RSK" and child.ord < semroot.ord:
                field_2_node_map["RSK"].add(child)
            elif childrel == "xcomp" and fieldval == "RSK" and child.ord > semroot.ord:
                field_2_node_map["NF_rels"].add(child)

            else:
                field_2_node_map[fieldval].add(child)
        field_2_node_map = reduce_field_contents_to_tops(field_2_node_map)

    # NB: complex tense of lexical verb, with aux in RSK of marked clause => VEND
    elif (
        node != semroot
        and node.xpos.endswith("FIN")
        and semroot.xpos not in LEXFINITE_VERB_POS
        and semroot.ord < node.ord
        and TUEBA_2_SIMPLE_TOPO[node.misc["TopoField"]] == "RSK"
        and has_child_with_given_rel(semroot, "mark")
    ):
        logger.info("complex tense of lexical verb, with aux in RSK of marked clause")
        field_2_node_map[TUEBA_2_SIMPLE_TOPO[semroot.misc["TopoField"]]].add(semroot)
        field_2_node_map[TUEBA_2_SIMPLE_TOPO[node.misc["TopoField"]]].add(node)

        for child in semroot.children:
            childrel = child.deprel
            fieldval = TUEBA_2_SIMPLE_TOPO[child.misc["TopoField"]]
            logger.info("child_node %s in field %s ", child.form, fieldval)
            if childrel == "ccomp" and fieldval == "RSK" and child.ord > semroot.ord:
                field_2_node_map["NF_rels"].add(child)
            elif childrel == "xcomp" and fieldval == "RSK" and child.ord < semroot.ord:
                field_2_node_map["RSK"].add(child)
            elif childrel == "xcomp" and fieldval == "RSK" and child.ord > semroot.ord:
                field_2_node_map["NF_rels"].add(child)

            else:
                field_2_node_map[fieldval].add(child)
        field_2_node_map = reduce_field_contents_to_tops(field_2_node_map)

    # NB: pseudo-subbordinated SEP with finite order
    if (
        node != semroot
        and semroot.xpos.startswith("V")
        and not node.xpos.startswith("VV")
        and sr_depth > MATRIX_DEPTH
        and semroot.ord > node.ord
        and semroot.deprel in ["conj"]
    ):
        logger.info("pseudo subbordinated SEP")
        field_2_node_map[TUEBA_2_SIMPLE_TOPO[semroot.misc["TopoField"]]].add(semroot)
        field_2_node_map[TUEBA_2_SIMPLE_TOPO[node.misc["TopoField"]]].add(node)

        for child in semroot.children:
            childrel = child.deprel
            fieldval = TUEBA_2_SIMPLE_TOPO[child.misc["TopoField"]]
            if childrel == "ccomp" and fieldval == "RSK" and child.ord > semroot.ord:
                field_2_node_map["NF_rels"].add(child)
            elif childrel == "xcomp" and fieldval == "RSK" and child.ord < semroot.ord:
                field_2_node_map["RSK"].add(child)

            elif childrel in ["csubj", "csubj:pass"] and child.ord < node.ord:
                field_2_node_map["VF_rels"].add(child)

            elif childrel in ["parataxis"]:
                if child.ord < node.ord:
                    field_2_node_map["VF_rels"].add(child)

            elif childrel == "cc" and child.upos == "CCONJ" and child.ord < node.ord:
                field_2_node_map["X_rels"].add(child)
            else:
                field_2_node_map[fieldval].add(child)
        field_2_node_map = reduce_field_contents_to_tops(field_2_node_map)

    # NB: embedded SEP as a complement clause, including marking
    elif (
        node != semroot
        and semroot.xpos.startswith("V")
        and not node.xpos.startswith("VV")
        and sr_depth > MATRIX_DEPTH
        and semroot.ord > node.ord
        and semroot.deprel in ["ccomp"]
        and has_child_with_given_rel(semroot, "mark")
    ):
        logger.info("embedded SEP as a complement clause, including marking")
        field_2_node_map[TUEBA_2_SIMPLE_TOPO[semroot.misc["TopoField"]]].add(semroot)
        field_2_node_map[TUEBA_2_SIMPLE_TOPO[node.misc["TopoField"]]].add(node)
        for child in semroot.children:
            childrel = child.deprel
            fieldval = TUEBA_2_SIMPLE_TOPO[child.misc["TopoField"]]
            logger.info("child_node %s in field %s ", child.form, fieldval)
            if childrel == "ccomp" and fieldval == "RSK" and child.ord > semroot.ord:
                field_2_node_map["NF_rels"].add(child)
            elif childrel == "xcomp" and fieldval == "RSK" and child.ord < semroot.ord:
                field_2_node_map["RSK"].add(child)

            elif childrel in ["csubj", "csubj:pass"] and child.ord < node.ord:
                field_2_node_map["VF_rels"].add(child)

            elif childrel in ["parataxis"]:
                if child.ord < node.ord:
                    field_2_node_map["VF_rels"].add(child)
            else:
                field_2_node_map[fieldval].add(child)

        field_2_node_map = reduce_field_contents_to_tops(field_2_node_map)

    # NB: SEP at matrix clause level
    elif (
        node != semroot
        and semroot.xpos.startswith("V")
        and not node.xpos.startswith("VV")
        and sr_depth == MATRIX_DEPTH
        and semroot.ord > node.ord
    ):
        logger.info("SEP in matrix clause")
        field_2_node_map[TUEBA_2_SIMPLE_TOPO[semroot.misc["TopoField"]]].add(semroot)
        field_2_node_map[TUEBA_2_SIMPLE_TOPO[node.misc["TopoField"]]].add(node)

        for child in semroot.children:
            childrel = child.deprel
            fieldval = TUEBA_2_SIMPLE_TOPO[child.misc["TopoField"]]
            logger.info("child_node %s in field %s ", child.form, fieldval)
            if childrel == "ccomp" and fieldval == "RSK" and child.ord > semroot.ord:
                field_2_node_map["NF_rels"].add(child)
            elif (
                childrel == "xcomp"
                and fieldval == "RSK"
                and child.ord < semroot.ord
                and child.ord > node.ord
            ):
                field_2_node_map["RSK"].add(child)
            elif childrel == "xcomp" and fieldval == "RSK" and child.ord < node.ord:
                field_2_node_map["VF_rels"].add(child)

            elif childrel in ["csubj", "csubj:pass"] and child.ord < node.ord:
                field_2_node_map["VF_rels"].add(child)

            elif childrel in ["parataxis"]:
                if child.ord < node.ord:
                    field_2_node_map["VF_rels"].add(child)
            else:
                field_2_node_map[fieldval].add(child)

        field_2_node_map = reduce_field_contents_to_tops(field_2_node_map)

    # NB: SEP in paratactic main clause
    # Du Schussel, jetzt HAST du die Milch überkochen lassen.
    elif (
        node != semroot
        and semroot.xpos.startswith("V")
        and not node.xpos.startswith("VV")
        and sr_depth > MATRIX_DEPTH
        and node.ord < semroot.ord
        and semroot.deprel in ["parataxis"]
    ):
        logger.info("SEP in paratactic main clause")
        field_2_node_map[TUEBA_2_SIMPLE_TOPO[node.misc["TopoField"]]].add(node)
        field_2_node_map[TUEBA_2_SIMPLE_TOPO[semroot.misc["TopoField"]]].add(semroot)
        for child in semroot.children:
            childrel = child.deprel
            fieldval = TUEBA_2_SIMPLE_TOPO[child.misc["TopoField"]]
            logger.info("child_node %s in field %s ", child.form, fieldval)

            if childrel == "ccomp" and fieldval == "RSK" and child.ord > semroot.ord:
                field_2_node_map["NF_rels"].add(child)
            elif (
                childrel == "xcomp"
                and fieldval == "RSK"
                and child.ord < semroot.ord
                and child.ord > node.ord
            ):
                field_2_node_map["RSK"].add(child)
            elif childrel == "xcomp" and fieldval == "RSK" and child.ord < node.ord:
                field_2_node_map["VF_rels"].add(child)

            elif childrel in ["csubj", "csubj:pass"] and child.ord < node.ord:
                field_2_node_map["VF_rels"].add(child)

            elif childrel in ["parataxis"]:
                if child.ord < node.ord:
                    field_2_node_map["VF_rels"].add(child)
            else:
                field_2_node_map[fieldval].add(child)
        if semroot.parent.ord < node.ord and semroot.parent.misc["TopoField"] == "null":
            field_2_node_map["X_rels"].add(semroot.parent)

        field_2_node_map = reduce_field_contents_to_tops(field_2_node_map)

    # NB: fronted non-finite VC
    # Feiern KANN man den Tag mit dem Verzehr von Pfannkuchen
    elif (
        node != semroot
        and semroot.xpos.startswith("V")
        and not node.xpos.startswith("VV")
        and sr_depth == MATRIX_DEPTH
        and semroot.ord < node.ord
    ):
        logger.info("fronted non-finite VC")
        field_2_node_map["VF_rels"].add(semroot)
        field_2_node_map[TUEBA_2_SIMPLE_TOPO[node.misc["TopoField"]]].add(node)
        for child in semroot.children:
            childrel = child.deprel
            fieldval = TUEBA_2_SIMPLE_TOPO[child.misc["TopoField"]]
            logger.debug("child_node %s in field %s ", child.form, fieldval)
            if childrel == "ccomp" and fieldval == "RSK" and child.ord > semroot.ord:
                field_2_node_map["NF_rels"].add(child)
            elif childrel == "xcomp" and fieldval == "RSK" and child.ord < semroot.ord:
                field_2_node_map["RSK"].add(child)
            elif childrel == "conj":
                pass
            elif child.ord < node.ord:
                pass

            else:
                field_2_node_map[fieldval].add(child)

        field_2_node_map = reduce_field_contents_to_tops(field_2_node_map)

    #   ┢─╼ gehen gehen VERB VVFIN aux Morph=1pis|NE=O|TopoField=LK
    #   ╰─┾ wandern wandern VERB VVINF root Morph=null|NE=O|SpaceAfter=No|TopoField=VC
    if (
        node != semroot
        and node.lemma in ["gehen", "bleiben"]
        and semroot.xpos.endswith("INF")
        and node.ord < semroot.ord
    ):
        logger.info(
            "gehen als 'light verb' in Kombinationen wie einkaufen gehen, wandern gehen; gehen in einfacher Zeitform vor Verb 2 "
        )
        field_2_node_map[TUEBA_2_SIMPLE_TOPO[semroot.misc["TopoField"]]].add(semroot)
        for kiddo in semroot.children:
            childrel = kiddo.deprel
            fieldval = TUEBA_2_SIMPLE_TOPO[kiddo.misc["TopoField"]]
            if childrel == "advcl" and kiddo.ord > semroot.ord:
                field_2_node_map["NF_rels"].add(kiddo)
            elif childrel == "advcl" and kiddo.ord < semroot.ord:
                field_2_node_map["VF_rels"].add(kiddo)
            # elif kiddo.ord < node.ord:
            #   pass
            else:
                field_2_node_map[fieldval].add(kiddo)

        field_2_node_map = reduce_field_contents_to_tops(field_2_node_map)

    logger.info("FIELD_2_NODE_map\n\n" + pp.pformat(field_2_node_map) + "\n")
    return field_2_node_map


def get_fin_verb_count(node: Node) -> int:
    return len([child for child in node.descendants if child.xpos in FINITE_VERB_POS])


def get_max_subtree_depth(node: Node) -> int:
    return max([child._get_attr("depth") for child in node.descendants])


def find_attached_final_punctuation(node: Node) -> Union[None, Node]:
    # we look at
    for kid in node.children[-1:]:
        if kid.deprel in ["punct"] and kid.form in ["?", "!", ".", ";", ":", ","]:
            return kid
    return None


def get_verb_count(node: Node) -> int:
    vlsit = [child for child in node.descendants if child.xpos.startswith("V")]
    if node.xpos.startswith("V"):
        vlsit.append(node)
    vtext = [v.form for v in vlsit]
    msg = f"The subtree rooted in {node.form} has these verbs: {vtext} "
    return (msg, vlsit)


# https://dkpro.github.io/dkpro-core/releases/1.8.0/docs/tagset-reference.html#tagset-de-tiger-dependency


def is_left_most_dep_wh_element(
    node: Node, logger: logging.Logger
) -> Union[None, Node]:
    """
    check if the left most node is a wh-element
    if not , return None
    """
    val = None

    if len(node.children) > 0:
        # get leftmost child
        leftmost = node.children[0]
        if leftmost.deprel in ["punct", "cc"]:
            # we can't switch to a non-punct child if there isn't one
            if len(node.children) > 1:
                leftmost = node.children[1]
            elif len(node.children) == 1:
                leftmode = node
            else:
                leftmost = node.children[2]

        logger.info(f"found leftmost {leftmost}")
        # that child is a wh-word
        if leftmost.lemma in SIMPLEWH and (
            leftmost.xpos.startswith("PW") or leftmost.lemma in ["wie", "inwiefern"]
        ):
            return leftmost
        else:
            logger.debug(" check if this is a phrase with an embedded wh-word")
            # not descending into clauses
            if len(leftmost.descendants) > 0 and leftmost.deprel not in [
                "ccomp",
                "csubj",
                "csubj:pass",
                "advcl",
            ]:
                for descendant in leftmost.descendants:
                    if (
                        descendant.xpos in ["PWS", "PWAT", "PWAV"]
                        and descendant.lemma in POT_EMBEDDED_WH_WORDS
                    ):
                        return leftmost

    return val


def is_node_correlative(node: Node, logger) -> Union[None, Node]:
    """check if node heads the je-part/clause of a German correlative construction (je-desto)"""
    logger.debug("Node having form: %s and lemma: >%s<", node.form, node.lemma)
    val = None
    if len(node.descendants) > 0:
        for ldm in node.descendants:
            if ldm.lemma == "je" and ldm.upos == "ADV":
                return node
    return val


def has_marker_for_embedded_yn_question(knode: Node) -> Union[None, Node]:
    val = None
    if len(knode.children) > 0:
        for ldm in knode.children:
            if ldm.lemma == "ob":
                return ldm

    return val


def wh_of_free_choice_cxn(knode: Node) -> Union[None, Node]:
    """check if the specified node is an adj-headed phrase with a sort of concessive/free choice semantics"""
    val = None
    if len(knode.children) > 0:
        if knode.children[0].lemma in ["egal", "gleich"]:
            for ldm in knode.children:
                if ldm.lemma in SIMPLEWH or ldm.lemma == "ob":
                    return ldm

    return val


def is_node_a_wh_element(lm: Node) -> Union[None, Node]:
    """check if node is a wh-element or contains one"""
    val = None
    # that child is a wh-word
    if lm.lemma in SIMPLEWH and lm.xpos.startswith("PW"):
        return lm
    else:
        # if it's not and if it has descendants,
        # look if this is a phrase with an embedded wh-word
        if len(lm.descendants) > 0:
            for ldm in lm.descendants:
                if ldm.lemma in POT_EMBEDDED_WH_WORDS:
                    return lm
        return val


def is_node_a_relativizer(
    current_node: Node, logger: logging.Logger
) -> Union[None, Node]:
    """check if the specified node is a relativizer or a phrase that contains one"""
    logger.debug(
        "Node with form: %s and lemma >%s<", current_node.form, current_node.lemma
    )
    val = None
    # check if  child itself is a wh-word
    if current_node.xpos in ["PRELS", "PRELAT"]:
        return current_node
    # if not, look if the node heads phrase that contains a wh-element
    if len(current_node.descendants) > 0:
        for kdesc in current_node.descendants:
            if kdesc.xpos in ["PRELS", "PRELAT"]:
                return current_node
    return val


def is_left_most_dep_relativizer(node):
    """check if left most dependent is a relativizer"""
    val = None
    if len(node.children) > 0:
        first_child = node.children[0]
        # look at the head/node itself
        if first_child.xpos.startswith("PRELS"):
            return first_child
        # alternatively, see if the node heads a phrase containing a relativizer
        if len(first_child.descendants) > 0:
            for kdesc in first_child.descendants:
                if kdesc.xpos.startswith("PRELS"):
                    return first_child
    return val


def get_tokens_formatted_for_presentation(root, node):
    tokens_formatted_for_presentation = []
    for knoten in root.descendants:
        tokens_formatted_for_presentation.append(knoten.form)
    tokens_formatted_for_presentation[(node.ord - 1)] = node.form.upper()
    return tokens_formatted_for_presentation


CORE_NOM_ARGS = ["nsubj", "obj", "iobj", "nsubj:pass"]
CORE_CLAUSAL_ARGS = ["csubj", "ccomp", "xcomp", "csubj:pass"]
CORE_RELS = CORE_NOM_ARGS + CORE_CLAUSAL_ARGS
NONCORENOMDEPS = ["obl", "vocative", "expl", "dislocated"]
NONCORECLDEPS = ["advcl"]
NOMDEPS = ["nmod", "appos", "nummod"]

NOMCLDEPS = ["acl"]
MODWORDS = ["advmod", "discourse"]
NOMFUNC = ["det", "case"]
MARKER = ["mark"]
NONLEXV = ["aux", "cop"]


def get_core_args_and_rest_UD_syntax(node):
    """return various lists holding e.g. a node's core args etc"""
    lov = []
    rov = []
    corenomargs = [x for x in node.children if x.deprel in CORE_NOM_ARGS]
    coreclausalargs = [x for x in node.children if x.deprel in CORE_CLAUSAL_ARGS]

    noncorenom = [x for x in node.children if x.deprel in NONCORENOMDEPS]
    noncorecl = [x for x in node.children if x.deprel in NONCORECLDEPS]

    mods = [x for x in node.children if x.deprel in MODWORDS]
    marks = [x for x in node.children if x.deprel in MARKER]
    rest = [
        x
        for x in node.children
        if (x.deprel not in CORE_RELS and x.deprel not in ["punct"])
    ]
    # Mi 05 Jul 2023 [ KW27 ] exluding punct here!
    allrels = [x for x in node.children if x.deprel not in ["punct", "conj"]]

    return (
        corenomargs,
        coreclausalargs,
        noncorenom,
        noncorecl,
        mods,
        marks,
        rest,
        allrels,
    )


PUNKDICT = {".": "Period", "!": "Exclamation", "?": "Question mark"}


def compute_text_and_label_no_punct(knoten, use_mwt=True):
    """Return a string representing this subtree's text (detokenized); uses UD syntax.

    Compute the string by concatenating forms of nodes
    (words and multi-word tokens) and joining them with a single space,
    unless the node has SpaceAfter=No in its misc.
    If called on root this method returns a string suitable for storing
    in root.text (but it is not stored there automatically).

    Technical details:
    If called on root, the root's form (<ROOT>) is not included in the string.
    If called on non-root nodeA, nodeA's form is included in the string,
    i.e. internally descendants(add_self=True) is used.
    Note that if the subtree is non-projective, the resulting string may be misleading.

    Args:
    use_mwt: consider multi-word tokens? (default=True)
    """
    if knoten.deprel == "punct":
        return ""
    string = ""
    last_mwt_id = 0
    for node in knoten.descendants(add_self=not knoten.is_root()):
        mwt = node.multiword_token
        if use_mwt and mwt:
            if node._ord > last_mwt_id:
                last_mwt_id = mwt.words[-1]._ord
                string += mwt.form
                if mwt.misc["SpaceAfter"] != "No":
                    string += " "
        else:
            if node.deprel not in ["punct"]:
                string += node.form
                if node.misc["SpaceAfter"] != "No":
                    string += " "
            else:
                string += " "
    return string.rstrip() + "_" + knoten.deprel


def map_punct_to_text(string):
    """map a punctuation symbol to a text representation"""
    if string in PUNKDICT:
        return PUNKDICT[string]
    else:
        return "UNDEF"


# def get_child_rels_of_node(node: Node) -> List[str]:
#   kidrel_list = []
#   for kid in node.children:
#       kidrel_list.append(kid.deprel)
#   return kidrel_list


def get_ancestors(node: Node) -> List[Node]:
    """return the list of the current node's ancestors"""
    ancestors = []  # used to be a set
    while node.parent:
        ancestors.append(node)
        node = node.parent
    return ancestors


def path_to_root(node: Node) -> List:
    """get the ancestor nodes on the path from node to the ROOT"""
    path_list = []
    while node.parent:
        path_list.append((node, node.deprel))
        node = node.parent
    return path_list


def get_positions_of_descendants(node: Node) -> List[int]:
    desc_inds = [x.ord for x in node.descendants]
    desc_inds.append(node.ord)
    return sorted(desc_inds)


def determine_node_order(node1: Node, node2: Node) -> str:
    """
    return the position of node 1 relative to node 2;
    "P" if node 1 precedes node 2   ,
    "F" if node 1 follows node 2
    """
    return determine_index_order(node1.ord, node2.ord)


def determine_index_order(ix1: int, ix2: int) -> str:
    """
    return the relative ordering of index1 to index2, where both indices represent
    the position of a node within a sentence

    Args:
                    ix1 (int): first index
                    ix2 (int): second index
    """
    if ix1 < ix2:
        return "P"
    else:
        return "F"


def get_tops_in_interval(lboundix: int, rboundix: int, root: Node) -> List[Node]:
    """get nodes between two boundary nodes (represented by their indices)
    that don't have their parent within the interval"""
    tops = []
    for d in root.descendants:
        if (
            d.ord < rboundix
            and d.ord > lboundix
            and d.form not in [".", ",", ":", "!", "?"]
        ):
            tops.append(d)

    tops = eliminate_non_tops(tops)
    return sorted(tops)


def get_left_tops(bound):
    """get one or more nodes to the left of a boundary node
    that do not have an ancestor to the left of the boundary node"""
    lefttops = []
    for d in bound.descendants:
        if d.ord < bound.ord:
            lefttops.append(d)
    # get rid of nodes whose parents is also to the left
    lefttops = eliminate_non_tops(lefttops)
    return lefttops


def compute_text_in_bounds(
    node: Node, leftbix: int, rightbix: int, logger: logging.Logger
) -> str:
    """Return a string representing this node/subtree's text - to the extent
    that the tokens are found within the specified boundaries"""
    logger.indebugfo("computing text for current node %s ", node.form)
    nlist = [node]

    for knode in node.descendants():
        if (knode.ord - 1) >= leftbix and (knode.ord - 1) < rightbix:
            nlist.append(knode)
    strlist = [kn.form for kn in sorted(nlist)]
    xstr = " ".join(strlist)
    logger.debug("getting text of subtree for node %s_ >%s<", str(node.form), xstr)
    return xstr


def eliminate_non_tops(nodelist):
    """among the nodes in a list, get rid of those whose parent is itself on the list"""
    todel = []
    for cand in nodelist:
        if cand.parent in nodelist:
            todel.append(cand)
    for tod in todel:
        nodelist.remove(tod)
    return nodelist


def retrieve_node_of_type_from_list(nl: List[Node], rel: str) -> Union[None, Node]:
    """if any node with a certain relation is found on a list of nodes, return the first matching such node"""
    for node in nl:
        if node.deprel == rel:
            return node
    return None


def has_child_with_given_rel(node, deprel):
    """check if node is a verbal node NOT marked by _zu_; uses Tiger syn"""
    val = False
    if True in [True for k in node.children if k.deprel == deprel]:
        val = True

    return val


def read_conllu_doc_to_udapi_doc(
    infile: str, logger: logging.Logger
) -> Tuple[Document, str]:
    """read a single conllu file into a udapi document"""
    logger.info("Processing %s", infile)
    basename = os.path.basename(infile)
    document = Document(filename=infile)
    docid = re.sub(r"\.conllu", "", basename)

    return (document, docid)


