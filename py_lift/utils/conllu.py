import pandas as pd
import re

from dkpro import *

def cas_to_str(cas, sentence):
    
    id_list = []
    form_list = []
    lemma_list = []
    udpos_list = []
    pos_list = []
    morph_list = []
    head_list = []
    rel_list = []
    enhanced_deps_list = []
    misc_list = []

    deps_list = cas.select(T_DEP)

    # NB: we need to filter out empty tokens that have no annotations
    unfiltered_token_list = cas.select_covered(T_TOKEN, sentence)
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
        x.get_covered_text for x in cas.select_covered(T_LEMMA, sentence)
    ]
    pos_list = [x.PosValue for x in cas.select_covered(T_POS, sentence)]
    morph_list = [x.morphTag for x in cas.select_covered(T_MORPH, sentence)]
    
    # TODO why like this?
    udpos_list = ["FM"] * len(token_list)

    enhanced_deps_list = ["_"] * len(token_list)
    misc_list = ["_"] * len(token_list)

    for token in token_list:
        token_id = token.xmiID
        dep_matches = []
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

    lists = [
        id_list,
        form_list,
        lemma_list,
        udpos_list,
        pos_list,
        morph_list,
        head_list,
        rel_list,
        enhanced_deps_list,
        misc_list
    ]
    
    df = pd.DataFrame(lists, colnames).T

    sent_id_line = "# sent_id = 1"
    s_text_line = "# text = " + re.sub("\n", " ", sentence.get_covered_text())
    df_str = df.to_csv(index=False, header=False, sep="\t")
    conllu_string = sent_id_line + "\n" + s_text_line + "\n" + df_str
    conllu_string = re.sub("\n{2,}", "\n", conllu_string).strip()

    return conllu_string