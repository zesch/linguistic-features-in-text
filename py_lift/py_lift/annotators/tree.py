import logging
from cassis import Cas
from cassis.typesystem import TypeNotFoundError

from py_lift.decorators import supported_languages
from py_lift.util import load_lift_typesystem, read_tsv_to_dict, require_same_typesystem
from spellchecker import SpellChecker
from cassis.typesystem import TYPE_NAME_FS_ARRAY
from py_lift.dkpro import T_TREE, T_SENT
from py_lift.annotators.api import SEL_BaseAnnotator
from py_lift.tree import TreeBuilder
from rwse_checker import rwse
from pathlib import Path
from typing import Union, List

class SE_TreeStructureAnnotator(SEL_BaseAnnotator):
    """
        # TODO
    """

    def __init__(self):
        super().__init__(language=None)

    def _process(self, cas: Cas) -> bool:
        Tree = self.get_type(T_TREE)

        tb = TreeBuilder()

        for sentence in cas.select(T_SENT):
            tree = tb.build_tree(cas, sentence)
            print(tree.draw())
            
            anno = Tree(
                begin=sentence.begin,
                end=sentence.end,
                maxDepth=tb._get_max_subtree_depth(tree),
            )
            cas.add(anno)

        return True