import pandas as pd
import re
from py_lift.dkpro import *

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
        if not re.match(r"^\s*$", x.get_covered_text())
    ]

    if len(unfiltered_token_list)!=len(token_list):
        print("some tokens are empty!")
    form_list = [x.get_covered_text() for x in token_list]
    print("form_list %s" %(str(form_list)))

    orig_id_list = [x.xmiID for x in token_list]
    id_list = list(range(1, len(token_list) + 1))

    id_map = dict(zip(orig_id_list, id_list))
    print("id_map:\n %s" %(id_map))
    lemma_list = [
        #
        x.value for x in cas.select_covered(T_LEMMA, sentence)
    ]
    pos_list = [x.PosValue for x in cas.select_covered(T_POS, sentence)]
    morph_list = [x.morphTag for x in cas.select_covered(T_MORPH, sentence)]
    if len(morph_list) == 0:
        morph_list = ["_"] * len(token_list)

    # TODO why like this?
    udpos_list = ["FM"] * len(token_list)

    enhanced_deps_list = ["_"] * len(token_list)
    #misc_list = ["_"] * len(token_list)
    print("id_map %s " %(str(id_map)))
    for token in token_list:
        token_id = token.xmiID
        print("processing token_id %s : %s" %(str(token_id), str(token.get_covered_text())))
        misc_list.append("t_start="+str(token.begin)+"|"+"t_end="+str(token.end))
        dep_matches = []
        for dep in deps_list:
            if (
                dep.Governor.xmiID not in id_map
                and dep.Dependent.xmiID not in id_map
            ):
                pass#sys.stderr.write("oops! both goveror and dep not in id map "+str(dep.Governor.xmiID)+"_"+str(dep.Dependent.xmiID)+"\n")
            else:
                if dep.Dependent.xmiID == token_id:
                    dep_matches.append(dep)
                    print("dependency is %s" %(str(dep)))
                    # root node (in Merlin) has its own id as head!
                    if dep.Governor.xmiID == token_id:
                        head_list.append(0)
                        rel_list.append("root")
                    else:
                        print("dep.Governor.xmiID %s %s" %(str(dep.Governor.xmiID),dep.Governor.get_covered_text()))
                        head_list.append(id_map[dep.Governor.xmiID])
                        rel_list.append(dep.DependencyType)
                else:
                    pass
        if len(dep_matches) == 0:
            raise RuntimeError(
                "No dependency matches for token %s !\n" % token.get_covered_text()
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
    print(conllu_string)
    return conllu_string