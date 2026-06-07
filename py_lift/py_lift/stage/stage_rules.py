"""
Stage classification rules for German verb placement analysis.

This module contains the rules for classifying German clauses according to
developmental stages based on word order patterns.
"""

from typing import Any, Dict, Union

from py_lift.stage.constants import (
    PLAUSIBLE_NP_INTERNAL_ADVS,
    STAGE_NAMES,
    FineLabel,
    FineStageClassification,
    get_logger,
)
from py_lift.stage.udapi_node_helper import PRONOMINAL_ADVERBS

logger = get_logger(__name__)


def apply_stage_rules(verb_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply German word order stage classification rules to a verb clause.

    Evaluates the clause against five developmental stages:
    - ADV: Adverb fronting (multiple elements in Vorfeld)
    - SVO: Subject-Verb-Object canonical order
    - INV: Subject-verb inversion
    - SEP: Verbal bracket separation
    - VEND: Verb-final position in subordinate clauses

    Args:
        verb_data: Dictionary containing clause analysis with topology,
                   verb position, and argument information.

    Returns:
        The input dictionary with added 'stages' key (coarse boolean values)
        and 'fine_stages' key (fine-grained FineLabel values).
    """
    logger.info("")
    logger.info("<<>>")
    logger.info(
        f"Applying stage rules to FINITE : {verb_data['finite_verb_form']} , SEMROOT  {verb_data['semroot']} in {verb_data['sent_id']}"
    )

    # initialize dict for the stages (coarse get boolean labels, fine get zero values as default)
    verb_data["stages"] = {
        "ADV": False,
        "SVO": False,
        "INV": False,
        "SEP": False,
        "VEND": False,
        "fine_ADV": "ADV_zero",
        "fine_INV": "INV_zero",
        "fine_SVO": "SVO_zero",
        "fine_SEP": "SEP_zero",
        "fine_VEND": "VEND_zero",
    }
    stage_dict = verb_data["stages"]
    topology = verb_data["topology"]

    # Note that the rules may result in no stage applying at all.
    #
    # Further note that we do some rule ordering here: for  SVO, the core vs peri distinction is in part dependent
    # on the presence of SEP. So we want o determine SEP first.

    # VEND
    _apply_vend_rule(verb_data, stage_dict)

    # SEP
    _apply_sep_rule(verb_data, stage_dict)

    # ADV
    _apply_adv_rule(stage_dict, topology, verb_data)

    # SVO
    _apply_svo_rule(verb_data, stage_dict, topology)

    # INV
    _apply_inv_rule(verb_data, stage_dict, topology)

    # look for interactions
    _check_interactions(verb_data, stage_dict, topology)

    # Derive coarse-grained labels from fine-grained labels
    _derive_coarse_from_fine(stage_dict)

    # Log which stages were triggered
    triggered_stages = []
    for cstage in STAGE_NAMES:
        val = stage_dict.get(cstage)
        if val:
            triggered_stages.append(cstage)

    if triggered_stages:
        logger.info(f"Stages triggered: {', '.join(triggered_stages)}")
    else:
        logger.info("No stages triggered")

    return verb_data


def _check_interactions(verb_data, stage_dict, topology):
    # SVO with SEP should be SVO_peri only
    if stage_dict["fine_SEP"] in ["SEP_core", "SEP_peri"] and stage_dict[
        "fine_SVO"
    ] in ["SVO_core", "SVO_peri"]:
        stage_dict["fine_SVO"] = "SVO_peri"


def _derive_coarse_from_fine(
    stage_dict: Dict[str, Union[str, Union[str, bool]]],
) -> None:
    """
    Derive coarse-grained boolean stage values from fine-grained labels.

    For each stage (ADV, SVO, INV, SEP, VEND), sets the coarse value to True
    if the corresponding fine label ends either in '_core' or in '_peri'.

    Args:
        stage_dict: Dictionary containing both coarse (boolean) and fine (string)
                    stage values. Is being modified in place.
    """
    for stage in STAGE_NAMES:
        fine_key = f"fine_{stage}"
        # if key does not exist, we'll treat this as a zero case, i.e. the stage does not apply
        fine_value = stage_dict.get(fine_key, f"{stage}_zero")
        # Coarse is True if fine ends in _core or _peri
        stage_dict[stage] = fine_value.endswith("_core") or fine_value.endswith("_peri")  # pyright: ignore[reportAttributeAccessIssue]


def _apply_vend_rule(
    verb_data: Dict[str, Any], stage_dict: Dict[str, Union[str, bool]]
) -> None:
    """
    Apply the VEND (verb-final) stage rule.

    VEND is triggered when the finite verb is in the VC (verb cluster) position,
    indicating verb-final order typical of subordinate clauses.

    PERI:
        - free standing subordinate clauses

    NOEV: we are not in a prohibited context but we have only a subject before a final V(C)-

    VERBOTEN CONTEXTS => _anti + ! (obey or violate prohibition):
        - VEND is not allowed when the clause is not appropriately marked (see under obligatory contexts)

    OBLIGATORY CONTEXTS => NO_  ( we violate a mandate):
    - VEND is obligatory when the clause is appropriately marked:
        (i) that [marked ccomp]
        (ii) non-that adverbial clause markers [advcl]
        (iii) `ob `as marker of embedded y/n questions
        (iv) ?? relative clauses that are not presentational [acl]

    """
    if verb_data["finite_verb_topo"] == "VC":
        if verb_data["VEND_verboten"]:
            stage_dict["fine_VEND"] = "!VEND"
            logger.info(
                f"VEND_verboten {verb_data['clause_text']} {verb_data['finite_verb']}"
            )
            return

        # finite verb in RSK
        if verb_data["semroot_topo"] == "VC" and verb_data["semroot"].upos == "VERB":
            if verb_data["matrix"] is True:
                stage_dict["fine_VEND"] = "VEND_peri"
            else:
                stage_dict["fine_VEND"] = "VEND_core"

        # copular clause
        if (
            verb_data["semroot_topo"] in ["MF", "C"]
            and verb_data["semroot"].upos != "VERB"
        ):
            if verb_data["matrix"] is True:
                stage_dict["fine_VEND"] = "VEND_peri"
            else:
                stage_dict["fine_VEND"] = "VEND_core"

        # funky copular
        if (
            verb_data["semroot_topo"] == "VC"
            and verb_data["semroot"] == verb_data["finite_verb"]
            and verb_data["finite_verb"].upos == "AUX"
            and verb_data["finite_verb"].lemma in ["sein", "werden"]
        ):
            # NB: we're not checcking length of MF right now
            if verb_data["matrix"] is True:
                stage_dict["fine_VEND"] = "VEND_peri"
            else:
                stage_dict["fine_VEND"] = "VEND_core"

        # post-editing check for noev
        # we have only one element (usu subj) in MF before the final verb cluster (VC)
        midfield_length = verb_data["topo_MF_count"]
        if midfield_length > 1:
            pass
        elif midfield_length == 1 and verb_data["topology"]["MF"][0].deprel in [
            "subj",
            "csubj",
            "csubj:pass",
        ]:
            stage_dict["fine_VEND"] = "VEND_noev"
        elif midfield_length == 0 and (
            verb_data["topo_C_count"] > 0 or verb_data["topo_LK_count"] > 0
        ):
            stage_dict["fine_VEND"] = "VEND_noev"
        else:
            pass


def _apply_sep_rule(
    verb_data: Dict[str, Any], stage_dict: Dict[str, Union[str, bool]]
) -> None:
    """
    Apply the SEP (separation) stage rule.

    SEP is triggered when there is a verbal bracket with material between
    the finite verb and other verbal elements.

    PERI:
        - copular clauses
        - separable prefix  verb

    NOEV: we are not in  a prohibited context but we have only a pre-finitum subject.

    OBLIGATORY CONTEXTS => NO_ ( we violate a mandate):
    - SEP is obligatory when the verbal cluster has a non-clausal argument in addition to the subject and VEND is not allowed.

    VERBOTEN CONTEXTS => _anti + ! ( we obey or violate a prohibition)
    - SEP is not allowed where LSK and RSK could be filled but VEND is obligatory
    - SEP is not allowed if a clausal constituent would be in MF

    """

    # right now we're not doing anything here about cases of rsk material fronted to the left of lsk
    if not verb_data["both_brackets_filled"]:
        return
    logger.info(f"considering for SEP {verb_data['clause_text']}")
    # Case 0:
    if verb_data["separated_verb_prefix"] is True:
        if len(verb_data["topology"]["MF"]) > 0:
            stage_dict["fine_SEP"] = "SEP_peri"
        else:
            stage_dict["fine_SEP"] = "SEP_noev"

    # Case 1: classic bracket with two verbal elements (kann empfehlen, wird gehen, ist gegangen)
    if (
        verb_data["semroot"] != verb_data["finite_verb"]
        and verb_data["semroot"].upos == "VERB"
        # and verb_data["semroot"].ord - verb_data["finite_verb"].ord > 1
    ):
        logger.info("non-copular SEP bracket")
        if len(verb_data["topology"]["MF"]) > 0:
            stage_dict["fine_SEP"] = "SEP_core"
        else:
            stage_dict["fine_SEP"] = "SEP_noev"

    # Case 2: bracket with copular or aux (ist krank gewesen ;/ Lehrerin ist sie  gewesen)
    if (
        verb_data["semroot"] != verb_data["finite_verb"]
        and verb_data["semroot"].upos != "VERB"
        and verb_data["is_copular_verb_present"]
        # TODO: ist X gewesen: we need to make sure semroot is
        # and len(verb_data["verb_cluster_other"]) > 0
        # and verb_data["verb_cluster_other"][0].misc["TopoField"].startswith("VC")
        # and verb_data["semroot"].ord - verb_data["finite_verb"].ord > 1
    ):
        logger.debug("copular SEP bracket!")
        if len(verb_data["topology"]["MF"]) > 0:
            stage_dict["fine_SEP"] = "SEP_peri"
        else:
            stage_dict["fine_SEP"] = "SEP_noev"
        stage_dict["fine_SEP"] = "SEP_peri"


def _apply_svo_rule(
    verb_data: Dict[str, Any],
    stage_dict: Dict[str, Union[bool, str]],
    topology: Dict[str, Any],
) -> None:
    """
     Apply the SVO (Subject-Verb-Object) stage rule.

     SVO is triggered when the subject is in the Vorfeld (before LK)
     and an object or oblique is in the Mittelfeld (after LK).


    PERI:
        - copular clauses
        - in case of co-occurring SEP
        - expletive S or O
        - clausal S or O
        - intrans with adjuncts
        - obligue A (e.g. oblig. PP)

     NOEV: not a prohibited context but we have only S (i.e. SV)

     OBLIGATORY CONTEXTS = > NO_ ( we violate a mandate):
    - SVO vs INV depends mainly on givenness and topic/focus. We can't do any extensive pragmatic reasoning and thus cannot identify cases where on pragmatic ground SVO might be strongly preferred ( ~ obl).

     VERBOTEN CONTEXTS => anti + ! (we obey or violate a prohibition):
     - SVO cannot occur in cases where VEND is obligatory.

    """
    # Check if subject is in VF (before LK)
    has_subj_before_lk = (
        len(verb_data["subj"]) > 0
        and "LK" in topology
        and len(topology["LK"]) > 0
        and verb_data["subj"][0].ord < topology["LK"][0].ord
    )
    semroot = verb_data["semroot"]
    finverb = verb_data["finite_verb"]

    # copular clauses
    if (
        verb_data["is_copular_verb_present"]
        and has_subj_before_lk
        and semroot.deprel in ["xcomp", "root"]
    ):
        # present tense copular clause
        if finverb.deprel in ["cop"]:
            stage_dict["fine_SVO"] = "SVO_peri"
        else:  # complex tense
            if semroot.ord > finverb.ord:
                stage_dict["fine_SVO"] = "SVO_peri"
            else:
                logger.warning(f"unexpected copular config")

    # non-copular clauses
    # first check for presence of subject
    if (
        has_subj_before_lk
        and "MF" in topology
        and not verb_data["is_copular_verb_present"]
    ):
        subj_is_nominal = True
        if verb_data["subj"][0].deprel in ["csubj", "csubj:pass"]:
            subj_is_nominal = False
        lk_position = topology["LK"][0].ord  # [2]

        # first, check on obl
        if len(verb_data["obl"]) > 0:
            for obl in verb_data["obl"]:
                obl_tf = obl.misc.get("TopoField")
                if obl_tf in ["MF", "NF"]:
                    stage_dict["fine_SVO"] = "SVO_peri"

        # next, check on non-clausal modifiers
        if len(verb_data["mod"]) > 0:
            for mod in verb_data["mod"]:
                mod_tf = mod.misc.get("TopoField")
                if mod_tf in ["MF", "NF"]:
                    stage_dict["fine_SVO"] = "SVO_peri"

        # next, check on non-clausal modifiers
        if len(verb_data["modclauses"]) > 0:
            for mod in verb_data["modclauses"]:
                if mod.ord > finverb.ord:
                    stage_dict["fine_SVO"] = "SVO_peri"

        # next, check on object
        if len(verb_data["obj"]) > 0:
            for obj in verb_data["obj"]:
                obj_tf = obj.misc.get("TopoField")
                if obj_tf in ["MF", "NF"]:
                    if obj.deprel in ["obj", "iobj"]:
                        if subj_is_nominal:
                            stage_dict["fine_SVO"] = "SVO_core"
                        else:
                            stage_dict["fine_SVO"] = "SVO_peri"
                        break

                if obj.deprel in ["ccomp", "xcomp"]:
                    stage_dict["fine_SVO"] = "SVO_peri"

        # post-processing: finally check if the clause is actually marked as incompatible with SVO
        if (
            stage_dict["fine_SVO"] in ["SVO_peri", "SVO_core"]
            and verb_data["SVO_verboten"] is True
        ):
            logger.info("flipping SVO to !SVO")
            stage_dict["fine_SVO"] = "!SVO"


def _apply_inv_rule(
    verb_data: Dict[str, Any],
    stage_dict: Dict[str, Union[str, bool]],
    topology: Dict[str, Any],
) -> None:
    """
    Apply the INV (inversion) stage rule.

    INV is triggered when the subject is to the right of LK (inverted)
    and there is a non-empty Vorfeld.


    PERI:
        - copular clauses ++
        - existential clauses
        - VP in VF
        - polar question (empty VF) ++
        - narrative V1

    NOEV: not a prohibited context, but we only have post-verbal S

    VERBOTEN CONTEXTS => anti + ! (we obey or violate a prohibition):
    - INV cannot occur in cases where VEND is obligatory.

    OBLIGATORY CONTEXTS => NO ( we violate a mandate):
    - INV(_peri) is obligatory in cases of object topic  drop (Kenn ich nicht). However, we have no valence info and cannot reason about expected but uninstantiated objects.
    - INV(_peri) is obligatory in neutral YN questions. However, we cannot reason about the pragmatic context and distinguish between neutral and biased questions.
    - SVO vs INV depends mainly on givenness and topic/focus. We can't do any extensive pragmatic reasoning and thus cannot identify cases where on pragmatic grounds INV might be  strongly preferred ( ~ obl).
    - all cases of ADV(_core) (with Adj +  Subj before V-fin)  should really be INV

    """
    logger.info(f"considering INV with topology {topology}")
    logger.info(f"els in subjects {len(verb_data['subj'])}")
    if (
        len(verb_data["subj"]) > 0
        and "LK" in topology
        and len(topology["LK"]) > 0
        # subj is post-LK
        and verb_data["subj"][0].ord > topology["LK"][0].ord
        and "VF" in topology
        and len(topology["VF"]) > 0
        # we need more than just the subject in post verbal  pos
        and len(topology["MF"]) + len(topology["VC"]) + len(topology["NF"]) > 1
    ):
        logger.info(f"finding non-empty VF for {verb_data['clause_text']}")
        # copular clauses
        if verb_data["is_copular_verb_present"]:
            stage_dict["fine_INV"] = "INV_peri"

        else:
            stage_dict["fine_INV"] = "INV_core"

    # empty VF
    if (
        len(verb_data["subj"]) > 0
        and "LK" in topology
        and len(topology["LK"]) > 0
        and verb_data["subj"][0].ord > topology["LK"][0].ord
        and "VF" in topology
        and len(topology["VF"]) == 0
    ):
        logger.info(f"finding empty VF for {verb_data['clause_text']}")
        # we need more than just the subject in post verbal  pos
        if len(topology["MF"]) + len(topology["VC"]) + len(topology["NF"]) > 1:
            stage_dict["fine_INV"] = "INV_peri"
        elif len(topology["MF"]) + len(topology["VC"]) + len(topology["NF"]) == 1:
            stage_dict["fine_INV"] = "INV_noev"
        else:
            stage_dict["fine_INV"] = "INV_zero"

    # funky cases where a Left dislocation is treated as the root clause and the finite  clause is a parataxis


def _apply_adv_rule(
    stage_dict: Dict[str, Union[str, bool]],
    topology: Dict[str, Any],
    verb_data: Dict[str, Any],
) -> None:
    """
    Apply the ADV (adverb fronting) stage rule.

    ADV is triggered when there are multiple constituents in the Vorfeld,
    indicating adverb fronting or complex prefield structures.


    PERI:
    - copular clauses
    - in VF, S follows an argument rather than an adjunct
    - in VF S precedes an adjunct

    NOEV:  ADV without a post-verbal element ( we have an ambiguity with VEND_peri anyway (Warum er das kauft?))

    OBLIGATORY CONTEXTS => NO ( we violate a mandate):
    - ADV is never obligatory.

    VERBOTEN CONTEXTS => anti + ! (we obey or violate a prohibition):
    - ADV is never allowed, so it's trivially always a violation but  we don't mark that specially


    """
    # for ADV to make any sense, LK needs to be filled
    if (
        "LK" in topology
        and len(topology["LK"]) > 0
        and "VF" in topology
        and len(topology["VF"])
    ):
        # for ADV, we want to find two constituents pre-LK

        logger.info("looking for adv")

        # easy case: VF has multiple items
        if len(topology["VF"]) > 1:
            logger.info("VF has multiple items")
            goodns = len(topology["VF"])
            # we visit the items and see if we can discount them as incorrectly
            # unintegrated into a larger NP
            for item in topology["VF"]:
                if item.lemma in PLAUSIBLE_NP_INTERNAL_ADVS:
                    goodns = goodns - 1
            if goodns > 1:
                stage_dict["fine_ADV"] = "ADV_core"

        # maybe an element in VF looks like it should be split up into distinct
        # bits
        elif len(topology["VF"]) == 1:
            vfe = topology["VF"][0]
            logger.info(f"VF has a single item :  {vfe.form} <> {vfe.compute_text()}")

            if vfe.upos in ["PRON", "NOUN"] and vfe.deprel in ["nsubj"]:
                logger.info("subject in vf")
                for vkid in vfe.children:
                    logger.info(f"Np-internal child {vkid.form}")
                    if vkid.deprel in ["advmod", "obl"] and vkid.ord < vfe.ord:
                        logger.info(f"found cand for adv! {vkid.form}")
                        if vkid.lemma not in PLAUSIBLE_NP_INTERNAL_ADVS:
                            logger.info("adv assigned!")
                            stage_dict["fine_ADV"] = "ADV_core"
                            break

                    if vkid.deprel in ["nmod"] and vkid.ord < vfe.ord:
                        logger.info(f"found cand for adv! {vkid.form}")
                        if vkid.lemma not in PLAUSIBLE_NP_INTERNAL_ADVS:
                            if vkid.misc.get("TopoField") not in ["LV"]:
                                logger.info("adv assigned!")
                                stage_dict["fine_ADV"] = "ADV_core"
                                break

            head_mod_pairs = {"Richtung": ["weiter"]}
            if vfe.upos in ["NOUN", "PRON"] and vfe.deprel in ["obj", "iobj", "obl"]:
                logger.info(f"obj or obl in vf {vfe.lemma}")
                for vkid in vfe.children:
                    logger.info(f"Np-internal child {vkid.form}")
                    if vkid.deprel in ["advmod", "obl"] and vkid.ord < vfe.ord:
                        logger.info(f"found cand for adv! {vkid.form}")
                        if (
                            vfe.lemma in head_mod_pairs
                            and vkid.lemma in head_mod_pairs[vfe.lemma]
                        ):
                            logger.info(f"ok combo! {vfe.lemma} {vkid.lemma}")

                        elif vkid.lemma in PLAUSIBLE_NP_INTERNAL_ADVS:
                            logger.info(f"plausible np-internl adv {vkid.lemma}")

                        else:
                            logger.info("adv assigned!")
                            stage_dict["fine_ADV"] = "ADV_peri"
                            break

                    if vkid.deprel in ["nmod"] and vkid.ord < vfe.ord:
                        logger.info(f"found cand for adv! {vkid.form}")
                        if vkid.lemma not in PLAUSIBLE_NP_INTERNAL_ADVS:
                            if vkid.misc.get("TopoField") not in ["LV"]:
                                logger.info("adv assigned!")
                                stage_dict["fine_ADV"] = "ADV_core"
                                break

            if "pre_VF" in topology and len(topology["pre_VF"]) > 0:
                logger.info(f"checking what's in pre_VF {topology['pre_VF']}")
                if topology["VF"][0].lemma in PRONOMINAL_ADVERBS and topology["pre_VF"][
                    0
                ].deprel in ["advcl"]:
                    logger.info(
                        "left-dislocated averbial  clause with resumptive pronominal adverb?"
                    )
                elif (
                    topology["VF"][0].lemma in ["das"]
                    and topology["pre_VF"][0].deprel in ["advcl"]
                    and verb_data["finite_verb"].deprel == "cop"
                ):
                    logger.info("pseudo-cleft cand!")

                else:
                    logger.info("adv assigned!")
                    stage_dict["fine_ADV"] = "ADV_core"

            # # BREAK
            # if (
            #     topology["VF"][0].lemma in ["das"]
            #     and len(topology["pre_VF"]) > 0
            #     and topology["pre_VF"][0].deprel in ["advcl"]
            #     and verb_data["finite_verb"].deprel == "cop"
            # ):
            #     logger.info("pseudo-cleft cand!")

            # else:
            #     logger.info("pseudo-cleft cand: no")
            #     logger.info("adv assigned!")
            #     stage_dict["fine_ADV"] = "ADV_core"

            if "null" in topology and len(topology["null"]) > 0:
                for nullo in topology["null"]:
                    logger.info(f"null for adv? {nullo.form}")
                    if nullo.ord < topology["VF"][0].ord:
                        if (
                            nullo.deprel not in ["cc"]
                            and nullo.form not in PLAUSIBLE_NP_INTERNAL_ADVS
                        ):
                            logger.info("adv assigned!")
                            stage_dict["fine_ADV"] = "ADV_core"
                            break

        elif (
            "KOORD" in topology
            and len(topology["KOORD"]) == 1
            and len(topology["VF"]) == 1
        ):
            # We might want to keep track of these later
            pass
