"""
CoNLL-U parsing module for German verb placement analysis.

This module contains functions for parsing CoNLL-U files and extracting
information about finite verbs and their arguments.
"""

import glob
import os
import random
from typing import Any, Dict, List, Optional

import udapi
from udapi.core.node import Node

from py_lift.stage.constants import MAX_SENTENCES, RANDOM_SEED, get_logger
from py_lift.stage.stage_rules import apply_stage_rules
from py_lift.stage.udapi_node_helper import (
    FINAL_PUNCT,
    POT_EMBEDDED_WH_WORDS,
    POT_QUESTION_EMBEDDING_PREDS,
    SIMPLEWH,
    clause_gov_has_pronominal_adverb_as_child,
    eliminate_non_tops,
    find_attached_final_punctuation,
    has_marker_for_embedded_yn_question,
    has_non_that_subordinator,
    has_that_complementizer,
    is_left_most_dep_wh_element,
)

logger = get_logger(__name__)


def _classify_dependent_formtype(deprel: str) -> Optional[str]:
    """
    Classify a dependent's form type based on its dependency relation.

    Args:
        deprel: The dependency relation label.

    Returns:
        The form type string, or None if the dependent should be skipped.
    """
    if deprel in ["nsubj", "iobj", "obj", "obl", "vocative", "dislocated"]:
        return "nominal"
    elif deprel in ["csubj", "ccomp", "xcomp", "advcl", "acl"]:
        return "clausal"
    elif deprel in ["mark"]:
        return "subordinator"
    elif deprel in ["advmod", "discourse"]:
        return "modifier_word"
    elif deprel in ["punct", "conj"]:
        return None  # Skip these
    else:
        return "minor"


def _process_dependent(
    dependent: Any,
    verb_data: Dict[str, Any],
    verb: Any,
    semroot: Any,
) -> None:
    """
    Process a single dependent of a verb and update verb_data accordingly.

    Args:
        dependent: The dependent node to process.
        verb_data: The verb data dictionary to update.
        verb: The finite verb token.
        semroot: The semantic root token.
    """

    # if semroot.upos in  ["ADJ","NOUN"]:
    # RBEAK

    deprel = dependent.deprel
    formtype = _classify_dependent_formtype(deprel)
    logger.info(f"processing dependent {dependent.form} {formtype}")
    if formtype is None:
        return  # Skip this dependent

    # Categorize by argument type
    if deprel in ["nsubj", "csubj"]:
        verb_data["subj"].append(dependent)
    elif deprel in ["iobj", "obj", "ccomp", "xcomp"]:
        verb_data["obj"].append(dependent)
    elif deprel in ["obl"]:
        verb_data["obl"].append(dependent)
    elif deprel in ["advcl"]:
        verb_data["modclauses"].append(dependent)
    elif deprel in ["advmod", "discourse", "vocative", "advmod:neg"]:
        verb_data["mod"].append(dependent)
    elif deprel in ["expl"]:
        verb_data["expl"].append(dependent)

    # Build argument tuple
    dep_phrase = dependent.compute_text()
    argument_tuple = (
        deprel,
        dependent.form,
        dependent.ord,
        formtype,
        dep_phrase,
    )

    # Determine topology field
    topo_field = dependent.misc.get("TopoField")
    if not topo_field:
        topo_field = "undef"

    # we leave null cases as is
    if topo_field == "null":
        pass

    # Adjust cases of  VC if they are in another clause
    # Maria WAR ganz zitttig, nachdem sie es GEHÖRT hatte.
    if dependent.deprel in ["advcl"] and topo_field == "VC":
        if dependent.ord > verb.ord and dependent.ord > semroot.ord:
            topo_field = "NF"

        elif dependent.ord < verb.ord and verb.misc.get("TopoField") in ["LK"]:
            logger.info(f"pre_VF candidate {dependent.form}")
            if len(verb_data["topology"]["VF"]) == 0:
                # verb_data["topology"]["VF"].append(dependent)
                topo_field = "VF"
            else:
                # verb_data["topology"]["pre_VF"].append(dependent)
                topo_field = "pre_VF"

    # Ich WAR froh, dass du GEKOMMEN bist.
    #  Macht man gewisse Information öffentlich zugänglich, KANN es sein , dass das ungeahnte Ausmaße ANNIMMT.
    if dependent.deprel in ["ccomp", "csubj"] and topo_field == "VC":
        if dependent.ord > verb.ord and dependent.ord > semroot.ord:
            topo_field = "NF"

    # Will ein Unternehmen sehr große Exponate AUSSTELLEN, was im touristischen Bereich eher selten VORKOMMT, sollte ein Freigeländestand gewählt werden.
    if dependent.deprel in ["acl", "acl:relcl", "parataxis"] and topo_field == "VC":
        if dependent.ord > verb.ord and dependent.ord > semroot.ord:
            topo_field = "NF"

    # Add to topology
    if topo_field not in verb_data["topology"]:
        verb_data["topology"][topo_field] = []
    # verb_data["topology"][topo_field].append(argument_tuple)
    verb_data["topology"][topo_field].append(dependent)


def _create_verb_data(
    token: Any,
    verb: Node,
    semroot: Node,
    sent_text: str,
    filename: str,
    sid: str,
    nodes: Any,
    root: Node,
) -> Dict[str, Any]:
    """
    Create the initial verb data dictionary for a finite verb clause.

    Args:
        token: The finite verb token.
        verb: The verb (same as token).
        semroot: The semantic root of the clause.
        sent_text: The full sentence text.
        filename: The source filename.
        sid: The sentence ID.
        nodes: All nodes in the sentence.

    Returns:
        A dictionary containing the initial verb clause data.
    """
    clause_gov = semroot.parent
    if clause_gov.is_root():
        clause_gov = None

    is_matrix_verb = semroot.deprel in ["root", "ROOT"]
    verb_topo = token.misc.get("TopoField")
    semroot_topo = semroot.misc.get("TopoField")
    clause_text = semroot.compute_text()
    is_copular_verb_present = False
    if verb.deprel == "cop":
        is_copular_verb_present = True
    for sem_chile in semroot.children:
        if sem_chile.deprel == "cop":
            is_copular_verb_present = True

    clause_props = {
        "topology": {
            "pre_VF": [],
            "VF": [],
            "MF": [],
            "NF": [],
            "LV": [],
            "RV": [],
            "C": [],
            "LK": [],
            "RSK": [],
            "VC": [],
            "VCE": [],
            "FKONJ": [],
            "FKOORD": [],
            "KOORD": [],
            "PARORD": [],
            "null": [],
        },  #  mapping from topological field names to lists of tuples such as ("_", verb.form, verb.ord, "finitum")
        "nodes": nodes,
        "full sentence": sent_text,
        "_filename": os.path.basename(filename),
        "sent_id": sid,
        "subj": [],
        "obj": [],
        "expl": [],
        "obl": [],
        "mod": [],
        "modclauses": [],
        "finite_verb": token,
        "finite_verb_form": token.form,
        "finite_verb_index": token.ord,
        "finite_verb_topo": verb_topo,
        "finite_verb_deprel": verb.deprel,  # deprel of finite verb: may be relation to semroot
        "finite_verb_type": "",  # one of :cop, aux, full, modal
        "finite_verb_is_semroot": False,  # default
        "lsk": [],  # list of nodes in left sentence bracket
        "rsk": [],  # list of nodes in right sentence bracket
        "both_brackets_filled": False,
        "separated_verb_prefix": False,
        "semroot": semroot,  # semantic root of clause that finite verb heads syntactically; may be predicative or a non-finite verb
        "semroot_form": semroot.form,  # token form of semantic root
        "semroot_topo": semroot_topo,  # topological field in which semantic root is found
        "semroot_index": semroot.ord,  # sentence position of semantic root (index)
        "semroot_deprel": semroot.deprel,  #
        "clause_type": semroot.deprel,
        "is_copular_verb_present": is_copular_verb_present,
        "clausal_governor": clause_gov,  # the node that governs semroot
        "matrix": is_matrix_verb,  # boolean for whether or not the clause is a matrix clause
        "is_marked_as_non_that_subordinate_clause": has_non_that_subordinator(semroot),
        "is_marked_as_yn_embedded_clause": has_marker_for_embedded_yn_question(semroot),
        "is_marked_as_that_subordinate_clause": has_that_complementizer(semroot),
        "clause_text": clause_text,
        "final_punctuation": "",  # potentially relevant sentence-final punctuation
        "VEND_obligatory": False,
        "SVO_obligatory": False,
        "INV_obligatory": False,
        "ADV_obligatory": False,
        "SEP_obligatory": False,
        "SVO_verboten": False,
        "INV_verboten": False,
        "ADV_verboten": False,
        "SEP_verboten": False,
        "VEND_verboten": False,
    }
    clause_props["clause_type"] = determine_clause_type(
        verb, semroot, nodes, root, clause_text
    )

    return clause_props


def _check_for_separable_verb_prefix_in_rsk(verb_data, semroot, verb):
    """check if we have a finite clause with a verb particle in rsk"""
    lk = verb_data["topology"]["LK"]
    rsk = verb_data["topology"]["VC"] + verb_data["topology"]["VCE"]

    part_in_rsk = False
    for item in rsk:
        if item.deprel == "compound:prt":
            part_in_rsk = True

    if len(lk) == 1 and lk[0].upos == "VERB" and part_in_rsk:
        verb_data["separated_verb_prefix"] = True
        return True
    else:
        return False


def _clause_has_compl_child(node: Node):
    """free matrix subordinate-form clauses have C filled"""
    for kid in node.children:
        if kid.misc.get("TopoField") == "C":
            return True
    return False


def _check_obligatoriness_and_prohibition_of_stages(clause_props, semroot, verb):
    """check if there is expectation that particular stages should occur"""

    #######
    # VEND #
    # #####
    if (
        clause_props["is_marked_as_non_that_subordinate_clause"]
        or clause_props["is_marked_as_that_subordinate_clause"]
        or clause_props["is_marked_as_yn_embedded_clause"]
        or semroot.deprel.startswith("acl")
        or _clause_has_compl_child(semroot)
    ):
        clause_props["VEND_obligatory"] = True
    else:
        # VEND is not allowed when the clause is not appropriately marked (see under obligatory contexts)
        clause_props["VEND_verboten"] = True

    #####
    # SEP #
    # ####

    # - SEP is obligatory (i) when the verb+semroot  have a non-clausal argument in addition to the subject and (ii)  when VEND is not allowed.
    # if clause_props["VEND_verboten"] and verb_cluster has argument or modifier in addition to subject:
    # clause_props["SEP_expected"] = True

    #  SEP is not allowed where LSK and RSK could be filled but VEND is obligatory
    if clause_props["VEND_obligatory"] is True:
        clause_props["SEP_verboten"] = True

    # SEP is not allowed if a clausal constituent is in MF
    # TODO

    ######
    # SVO #
    # ####

    # We **cannot** capture the cases where SVO is obligatory
    # SVO vs INV depends mainly on givenness and topic/focus. We can't do any extensive pragmatic reasoning and thus cannot identify cases where on pragmatic ground SVO might be strongly preferred.

    #   SVO may not occur in cases where VEND is obligatory.
    if clause_props["VEND_obligatory"] is True:
        clause_props["SVO_verboten"] = True

    #####
    # INV #
    # ####

    # INV is obligatory under certain circumstances that are hard to capture
    #
    #  INV(_peri) is obligatory in cases of object topic  drop (Kenn ich nicht). However, we have no valence info and cannot reason about expected but uninstantiated objects.
    #  INV(_peri) is obligatory in neutral YN questions. However, we cannot reason about the pragmatic context and distinguish between neutral and biased questions.
    #  SVO vs INV depends mainly on givenness and topic/focus. We can't do any extensive pragmatic reasoning and thus cannot identify cases where on pragmatic grounds INV might be  strongly preferred ( ~ obl).
    #  all cases of ADV(_core) (with Adj +  Subj before V-fin)  should really be INV

    #
    #  INV may not occur in cases where VEND is obligatory.
    if clause_props["VEND_obligatory"] is True:
        clause_props["INV_verboten"] = True

    ######
    # ADV  #
    # #####

    # ADV is more specifically  proscribed when we have an expectation of VEND
    # i.e. ADV in a marked subordinate is bad
    if clause_props["VEND_obligatory"] is True:
        clause_props["ADV_verboten"] = True


def _get_semroot(token, verb):
    # Determine semantic head **before working on clause props**
    if token.deprel in ["aux", "aux:pass", "cop"]:
        semroot = verb.parent
    else:
        semroot = verb
    return semroot


def _get_finitum_for_semroot(semroot):
    finitum = None
    if semroot.xpos.endswith("FIN") or semroot.xpos.endswith("IMP"):
        finitum = semroot
    else:
        for chile in semroot.children:
            if (
                chile.xpos.endswith("FIN") or chile.xpos.endswith("IMP")
            ) and chile.deprel in ["cop", "aux", "aux:pass"]:
                finitum = chile
                break
    return finitum


def _check_if_both_brackets_are_filled(verb_data, semroot, verb):
    if len(verb_data["topology"]["LK"]) > 0 and (
        len(verb_data["topology"]["VC"]) > 0 or len(verb_data["topology"]["VCE"]) > 0
    ):
        verb_data["both_brackets_filled"] = True


def get_clause_type_of_first_conjunct(
    r_verb: Node, r_sem: Node, r_nodes: List[Node], root: Any, clause_text: str
):
    left_semroot = r_sem.parent
    left_finite = _get_finitum_for_semroot(left_semroot)
    logger.info(f"as left finite for {left_semroot} we got {left_finite}")
    left_head = None
    if left_finite != None:
        left_head = left_finite
    else:
        left_head = left_semroot

    first_coord_clause_type = determine_clause_type(
        left_head, left_semroot, r_nodes, root, clause_text
    )
    logger.info(
        f"for first conjunct with H:{left_head}_S:{left_semroot} we have {first_coord_clause_type}"
    )
    return first_coord_clause_type


def determine_clause_type(
    verb: Node, semroot: Node, nodes: List[Node], root: Any, clause_text: str
):
    clause_type = "undef"

    # s-final punctuation should be attached to the overall sentence root : Not true!
    # sent_root = None
    # for n in nodes:
    #   if n.deprel.lower() == "root":  # pyright: ignore[reportOptionalMemberAccess]
    #      sent_root = n
    #       break
    # logger.info(f"sent_root we found {sent_root}")
    # if sent_root != None:
    #     logger.info(f"looking for punkt in {sent_root.children[-1:]}")
    #     sent_punct = find_attached_final_punctuation(sent_root)
    # else:
    #     sent_punct = None
    # logger.info(f"found  punctuation {sent_punct} for {verb}{semroot}")
    # if verb.deprel.lower() == "root" or semroot.deprel.lower() == "root":
    #     if sent_punct is not None:
    #         if sent_punct.form in FINAL_PUNCT:
    #             has_matrix_punct = True

    # logger.info(
    #     f"matrix_punct? {has_matrix_punct} for V:{verb.form}/S:{semroot.form}/R:{root.form} : {clause_text}"
    # )

    matrix_punct = None
    punct_head = None
    final_token = nodes[-1]
    if final_token.deprel in ["punct"] and final_token.form in FINAL_PUNCT:
        matrix_punct = final_token
        punct_head = final_token.parent
    logger.info(f"maxtrix_punct = {matrix_punct}, punct_head {punct_head}")
    if semroot.deprel == "conj":
        logger.info(f"following up on conj for {verb}/{semroot}")
        clause_type = get_clause_type_of_first_conjunct(
            verb, semroot, nodes, root, clause_text
        )
        return clause_type

    if semroot.deprel == "parataxis":
        logger.info(f"following up on parataxis for {verb}/{semroot}")
        clause_type = get_clause_type_of_first_conjunct(
            verb, semroot, nodes, root, clause_text
        )
        logger.info(f"after parataxis head inspection , we have {clause_type}")
        if clause_type == "undef" and matrix_punct != None:
            if matrix_punct.form == "?":
                # check if left most  is a wh item
                if not is_left_most_dep_wh_element(semroot, logger):
                    clause_type = "qsyn"
                else:
                    clause_type = "qswh"
            elif matrix_punct.form == ".":
                clause_type = "dec"
            elif matrix_punct.form == "!":
                clause_type = "other"
            else:
                pass
            return clause_type

    if semroot.deprel.startswith("acl"):
        if (
            has_marker_for_embedded_yn_question(semroot)
            and semroot.parent.lemma in POT_QUESTION_EMBEDDING_PREDS
        ):
            clause_type = "subind"
        if (
            is_left_most_dep_wh_element(semroot, logger)
            and semroot.parent.lemma in POT_QUESTION_EMBEDDING_PREDS
        ):
            clause_type = "subind"
        else:
            clause_type = "subrel"

    elif semroot.deprel == "advcl":
        logger.info(f"advcl for {verb}{semroot}")
        if has_that_complementizer(
            semroot
        ) and clause_gov_has_pronominal_adverb_as_child(semroot):
            clause_type = "subcomp"
        else:
            clause_type = "subadv"

    elif verb.xpos.endswith("IMP"):
        clause_type = "imp"
    elif (
        has_marker_for_embedded_yn_question(semroot) != None
        and semroot.deprel.lower() != "root"
    ):
        clause_type = "subind"

    # this next rule needs to precede the left most dep wh one
    elif semroot.deprel in ["csubj", "csubj:pass", "ccomp"]:
        logger.info("found cand for subj or obj clause ")
        if (
            semroot.upos == "VERB"
            and semroot.parent.lemma in POT_QUESTION_EMBEDDING_PREDS
            and is_left_most_dep_wh_element(semroot, logger) != None
        ):
            clause_type = "subind"
        elif semroot.lemma in POT_EMBEDDED_WH_WORDS:
            clause_type = "subind"
        elif (
            semroot.upos != "VERB"
            and semroot.parent.lemma in POT_QUESTION_EMBEDDING_PREDS
            and is_left_most_dep_wh_element(semroot, logger) != None
        ):
            clause_type = "subind"
        else:
            clause_type = "subcomp"

    elif (
        is_left_most_dep_wh_element(semroot, logger) != None
        or semroot.form.lower() in SIMPLEWH
    ):
        # TODO control for exclamative punctuation!
        if semroot.deprel in ["root", "ROOT"]:
            clause_type = "qswh"
        elif semroot.deprel in ["ccomp"]:
            clause_type = "subind"
        else:
            pass

    elif semroot.deprel.lower() in ["root"] and semroot == punct_head:
        logger.info("current semroot is sentence root")
        if matrix_punct.form == "?":
            clause_type = "qsyn"
        elif matrix_punct.form == ".":
            clause_type = "dec"
        elif matrix_punct.form == "!":
            clause_type = "other"
    # default
    elif semroot.deprel.lower() in ["root"] and matrix_punct == None:
        clause_type = "dec"
    # TODO: deal with parataxis and coordination
    else:
        pass
    logger.info(f"found {clause_type} for  {verb}/{semroot}")
    return clause_type


def analyze_single_document(
    udapi_doc: udapi.Document, filename: str
) -> List[Dict[str, Any]]:
    """
    Analyze a udapi Document to extract information about finite verbs and their arguments.

    Args:
        udapi_doc: A udapi Document object to process.
        filename: The source filename (used for logging and metadata).

    Returns:
        A list of dictionaries, where each dictionary represents a finite verb clause
        with its syntactic properties and arguments. Each dictionary contains keys for
        topology, verb information, semantic root, clause type, and stage assignments.
    """
    clauses = []
    sct = 0
    for bundle in udapi_doc.bundles:
        sct += 1
        if MAX_SENTENCES != 0 and sct > MAX_SENTENCES:
            logger.debug(
                f"Reached MAX_SENTENCES limit ({MAX_SENTENCES}), stopping processing"
            )
            break
        logger.info("")
        logger.info("<<>><<>>")
        logger.info(f"Processing sentence {sct} in {filename}")
        logger.debug(f"Processing sentence {sct}")
        if len(bundle.trees) > 1:
            logger.warning(f"Multiple roots found in sentence {sct}")
        # get_tree yields an obj of type udapi.core.root.Root
        root = bundle.get_tree()
        sent_text = root.text
        sid = root.sent_id
        nodes = root.descendants
        verb_data = None
        # Iterate over each token (node) in the sentence to find finite verbs.

        for token in nodes:
            # A finite verb has a UPOS of 'VERB' or 'AUX' and an XPOS ending in 'FIN'.
            is_verb_or_aux = token.upos in ["VERB", "AUX"]
            is_finite = token.xpos is not None and token.xpos.endswith("FIN")

            if is_verb_or_aux and is_finite:
                verb = token
                logger.debug(f"Found finite verb: {verb.form} ({verb.upos}) in sentence {sct}")

                semroot = _get_semroot(token, verb)

                # Perform check for **required** TopoField for semroot
                semroot_topo = semroot.misc.get("TopoField")
                if not semroot_topo:
                    logger.warning(
                        f"Missing TopoField for semroot '{semroot.form}' in sentence {sct}, skipping clause"
                    )
                    continue

                # Create verb data using helper function
                verb_data = _create_verb_data(
                    token, verb, semroot, sent_text, filename, sid, nodes, root
                )

                logger.debug(
                    f"Topology fields - verb: {verb_data['finite_verb_topo']}, semroot: {semroot_topo}"
                )
                logger.debug(f"Processing clause: {verb_data['clause_text'][:80]}...")

                # Add semroot to topology

                if semroot != verb:
                    verb_data["topology"][semroot_topo].append(
                        # ("_", semroot.form, semroot.ord, "semroot")
                        semroot
                    )
                else:
                    # set flag for identity of semroot and finitum
                    verb_data["finite_verb_is_semroot"] = True
                    verb_data["topology"][semroot_topo].append(
                        # ("_", semroot.form, semroot.ord, "finitum")
                        semroot
                    )
                # Add finite verb to topology if different from semroot
                if semroot != verb:
                    verb_topo = verb_data["finite_verb_topo"]
                    if verb_topo not in verb_data["topology"]:
                        verb_data["topology"][verb_topo] = []
                    verb_data["topology"][verb_topo].append(
                        # ("_", verb.form, verb.ord, "finitum")
                        verb
                    )

                # Collect other verbal elements in the cluster
                other_vc = []
                if semroot != verb:
                    for skid in semroot.children:
                        if skid != verb and skid.upos in ["VERB", "AUX"]:
                            other_vc.append(skid)
                verb_data["verb_cluster_other"] = other_vc

                # Process all dependent children of verb & semroot.
                # Iteration order matters: many downstream rules read
                # ``subj[0]``, ``topology["LK"][0]`` etc., so we walk the
                # dependents in sentence order to keep the lists stable
                # across runs (a plain ``set`` would be ordered by Node
                # id-hash and so vary with PYTHONHASHSEED).
                all_kids = sorted(
                    set(token.children + semroot.children) - {token},
                    key=lambda n: n.ord,
                )
                for dependent in all_kids:
                    _process_dependent(dependent, verb_data, verb, semroot)
                    logger.info(
                        f"after processing {dependent.form} , VC  field has {verb_data['topology']['VC']}"
                    )

                # Add topology field counts and content for all fields in the clause
                all_topo_fields = list(verb_data["topology"].keys())
                for field in all_topo_fields:
                    field_data = verb_data["topology"].get(field, [])
                    verb_data[f"topo_{field}_count"] = len(field_data)

                # determine which stages may be required / expected or probhibited given the current clause
                _check_obligatoriness_and_prohibition_of_stages(
                    verb_data, semroot, verb
                )

                # check if both brackets are filled
                _check_if_both_brackets_are_filled(verb_data, semroot, verb)

                # check for separable prefix verb
                _check_for_separable_verb_prefix_in_rsk(verb_data, semroot, verb)

                # if semroot is in verb_data["VF"], remove its dependents that are also in VF
                if verb_data and "VF" in verb_data["topology"]:
                    logger.info(f"checking on VF ")
                    verb_data["topology"]["VF"] = eliminate_non_tops(
                        verb_data["topology"]["VF"]
                    )

                #########################
                # Apply stage classification rules    #
                # ########################
                verb_data = apply_stage_rules(verb_data)

                # Add the completed dictionary for this verb to the list
                clauses.append(verb_data)

    return clauses


def analyze_german_verb_placement(file_path_pattern: str) -> List[Dict[str, Any]]:
    """
    Parse German CoNLL-U files to extract information about finite verbs and their arguments.

    Args:
        file_path_pattern: A glob pattern for finding the CoNLL-U files
                           (e.g., "data/*.conllu").

    Returns:
        A list of dictionaries, where each dictionary represents a finite verb clause
        with its syntactic properties and arguments. Each dictionary contains keys for
        topology, verb information, semantic root, clause type, and stage assignments.
    """
    clauses = []
    # Find all files matching the specified path pattern.
    flist = glob.glob(file_path_pattern)
    if not flist:
        logger.warning(f"No files found matching pattern: {file_path_pattern}")
        return clauses
    logger.info(f"Found {len(flist)} files matching pattern: {file_path_pattern}")
    random.seed(RANDOM_SEED)
    random.shuffle(flist)

    for filename in flist:
        logger.info(f"Processing file: {filename}")
        # NB: we use udapi for extracting info on the verbs and their arguments.
        # Later for outputting modified conllu files, we use pyconll because
        # that is easier.
        try:
            udapi_doc = udapi.Document(filename)
        except Exception as e:
            logger.error(f"Failed to parse file {filename}: {str(e)}")
            continue
        document_clauses = analyze_single_document(udapi_doc, filename)
        clauses.extend(document_clauses)

    return clauses
