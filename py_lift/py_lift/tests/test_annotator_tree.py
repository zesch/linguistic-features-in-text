import pytest
from py_lift.dkpro import T_TREE, T_DEP
from py_lift.preprocessing import Spacy_Preprocessor
from py_lift.util import load_lift_typesystem
from py_lift.annotators.tree import SE_TreeStructureAnnotator
from cas_visualizer.visualizer import DependencyVisualizer

def test_tree_structure_annotator_german():
    """Test SE_TreeStructureAnnotator with German text."""
    text = "Das ist ein Beispiel. Die Katze sitzt auf der Matte."
    spacy = Spacy_Preprocessor(language='de')
    cas = spacy.run(text)
    
    annotator = SE_TreeStructureAnnotator()
    annotator.process(cas)
    
    # Check that tree annotations were created for each sentence
    trees = cas.select(T_TREE)
    assert len(trees) == 2
    
    assert hasattr(trees[0], 'maxDepth')
    assert trees[0].maxDepth == 3

    assert hasattr(trees[1], 'maxDepth')
    assert trees[1].maxDepth == 4
