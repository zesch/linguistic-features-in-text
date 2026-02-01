import pytest
import cassis
from cassis import Cas, TypeSystem

from py_lift.dkpro import T_FEATURE

from py_lift.extractors import (
    FEL_AnnotationCounter,
    FEL_FeatureValueCounter,
    FEL_AnnotationRatio,
    FEL_Length,
    FEL_Min_Max_Mean,
    FE_NumberOfSpellingAnomalies,
    FE_NounPhrasesPerSentence,
    FE_TokensPerSentence,
    FE_EasyWordRatio,
    FE_AbstractnessStats,
)
from py_lift.extractors_specific import FE_DependencyAndTreeStats, FE_Per1kTokenStats
import pytest
from collections import namedtuple, Counter, defaultdict

# Dummy-Annotation und Dummy-CAS für den Test
DummyAnno = namedtuple('DummyAnno', ['get'])
class DummyCAS:
    def __init__(self, data):
        self.data = data  # dict: annotation_type -> list of dicts

    def select(self, annotation_type):
        return [DummyAnno(lambda key, d=d: d[key]) for d in self.data.get(annotation_type, [])]

    def add(self, feature):
        if not hasattr(self, 'features'):
            self.features = []
        self.features.append(feature)

    @property
    def typesystem(self):
        return self

    def get_type(self, featpath):
        return lambda **kwargs: kwargs

@pytest.fixture
def cas_dep_and_tree():
    # Für FE_DependencyAndTreeStats
    return DummyCAS({
        "de.tudarmstadt.ukp.dkpro.core.api.syntax.type.dependency.Dependency": [
            {"Governor": DummyAnno(lambda k: {"begin": 10}[k]), "Dependent": DummyAnno(lambda k: {"begin": 12}[k]), "DependencyType": "nk"},
            {"Governor": DummyAnno(lambda k: {"begin": 20}[k]), "Dependent": DummyAnno(lambda k: {"begin": 15}[k]), "DependencyType": "sb"},
            {"Governor": DummyAnno(lambda k: {"begin": 30}[k]), "Dependent": DummyAnno(lambda k: {"begin": 32}[k]), "DependencyType": "nk"},
        ],
        "org.lift.type.TreeStructure": [
            {"maxDepth": 7},
            {"maxDepth": 5}
        ]
    })

@pytest.fixture
def cas_per_1k():
    # Für FE_Per1kTokenStats
    return DummyCAS({
        "TokenCount": [{"value": 100}, {"value": 100}],
        "ConjunctionCount": [{"value": 3}, {"value": 2}],
        "SubordinatorCount": [{"value": 1}, {"value": 1}],
        "AdpositionCount": [{"value": 10}, {"value": 5}],
        "PrepositionCount": [{"value": 6}, {"value": 4}],
        "PostpositionCount": [{"value": 2}, {"value": 1}],
        "RelativePronounCount": [{"value": 1}, {"value": 0}],
        "PersonalPronounCount": [{"value": 5}, {"value": 3}],
    })

def test_dependency_and_tree_stats(cas_dep_and_tree):
    extractor = FE_DependencyAndTreeStats()
    result = extractor.extract(cas_dep_and_tree)
    assert result is True
    features = {f['name']: f['value'] for f in cas_dep_and_tree.features}

    # Berechnung:
    # Dependency-Längen: (12-10)=2 (nk), (15-20)=-5 (sb), (32-30)=2 (nk)
    # nk: [2,2], sb: [-5]
    # left: abs(-5)=5, count=1, avg=5/1=5.0
    # right: 2+2=4, count=2, avg=4/2=2.0
    # all: 5+4=9, count=3, avg=9/3=3.0
    # maxDepth: (7+5)/2=6.0

    assert features["Average_Dependency_Length_Left"] == pytest.approx(5.0)
    assert features["Average_Dependency_Length_Right"] == pytest.approx(2.0)
    assert features["Average_Dependency_Length_All"] == pytest.approx(3.0)
    assert features["Average_Tree_Depth"] == pytest.approx(6.0)

def test_per_1k_token_stats(cas_per_1k):
    extractor = FE_Per1kTokenStats()
    result = extractor.extract(cas_per_1k)
    assert result is True
    features = {f['name']: f['value'] for f in cas_per_1k.features}

    # doc_length = 200
    # Conjunctions: 5/200*1000 = 25.0
    assert features["Conjunctions_per_1k_tokens"] == pytest.approx(25.0)
    # Subordinators: 2/200*1000 = 10.0
    assert features["Subordinators_per_1k_tokens"] == pytest.approx(10.0)
    # Adpositions: 15/200*1000 = 75.0
    assert features["Adpositions_per_1k_tokens"] == pytest.approx(75.0)
    # Prepositions: 10/200*1000 = 50.0
    assert features["Prepositions_per_1k_tokens"] == pytest.approx(50.0)
    # Postpositions: 3/200*1000 = 15.0
    assert features["Postpositions_per_1k_tokens"] == pytest.approx(15.0)
    # Relative_pronouns: 1/200*1000 = 5.0
    assert features["Relative_pronouns_per_1k_tokens"] == pytest.approx(5.0)
    # Personal_pronouns: 8/200*1000 = 40.0
    assert features["Personal_pronouns_per_1k_tokens"] == pytest.approx(40.0)