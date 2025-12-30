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

@pytest.fixture
def typesystem() -> TypeSystem:
    ts = cassis.TypeSystem()

    # Feature-Container-Typ (Name aus py_lift.dkpro.T_FEATURE)
    F = ts.create_type(name=T_FEATURE, supertypeName="uima.tcas.Annotation")
    ts.create_feature(domainType=F, name="name", rangeType="uima.cas.String")
    ts.create_feature(domainType=F, name="value", rangeType="uima.cas.Double")

    # Annotationtypen
    Token = ts.create_type(name="Token", supertypeName="uima.tcas.Annotation")
    ts.create_feature(domainType=Token, name="tag", rangeType="uima.cas.String")  # für FeatureValueCounter

    ts.create_type(name="Sentence", supertypeName="uima.tcas.Annotation")
    ts.create_type(name="NC", supertypeName="uima.tcas.Annotation")
    ts.create_type(name="EasyWord", supertypeName="uima.tcas.Annotation")
    ts.create_type(name="SpellingAnomaly", supertypeName="uima.tcas.Annotation")
    ts.create_type(name="Foo", supertypeName="uima.tcas.Annotation")  # leerer Typ für Zero-Division-Tests

    AC = ts.create_type(
        name="org.lift.type.AbstractnessConcreteness", supertypeName="uima.tcas.Annotation"
    )
    ts.create_feature(domainType=AC, name="value", rangeType="uima.cas.Double")

    return ts


@pytest.fixture
def cas(typesystem: TypeSystem) -> Cas:
    cas = cassis.Cas(typesystem=typesystem)

    # Dokumenttext
    text = "This is a test."
    cas.sofa_string = text
    # Indizes:
    # "This"(0,4) " "(4,5) "is"(5,7) " "(7,8) "a"(8,9) " "(9,10) "test"(10,14) "."(14,15)

    Token = typesystem.get_type("Token")
    Sentence = typesystem.get_type("Sentence")
    NC = typesystem.get_type("NC")
    EasyWord = typesystem.get_type("EasyWord")
    SpellingAnomaly = typesystem.get_type("SpellingAnomaly")
    AC = typesystem.get_type("org.lift.type.AbstractnessConcreteness")

    # Tokens (inkl. 1 Duplikat für Unique-Zähltest)
    cas.add(Token(begin=0, end=4, tag="hard"))   # "This"
    cas.add(Token(begin=5, end=7, tag="easy"))   # "is"
    cas.add(Token(begin=8, end=9, tag="easy"))   # "a"
    cas.add(Token(begin=10, end=14, tag="hard")) # "test"
    cas.add(Token(begin=8, end=9, tag="easy"))   # Duplikat von "a"

    # Sentence
    cas.add(Sentence(begin=0, end=len(text)))

    # NC (2 Phrasen)
    cas.add(NC(begin=0, end=4))     # "This"
    cas.add(NC(begin=8, end=14))    # "a test"

    # EasyWords (2 Stück)
    cas.add(EasyWord(begin=5, end=7))  # "is"
    cas.add(EasyWord(begin=8, end=9))  # "a"

    # SpellingAnomaly (1 Stück)
    cas.add(SpellingAnomaly(begin=0, end=1))

    # Abstractness/Concreteness Scores
    cas.add(AC(begin=0, end=4, value=4.0))
    cas.add(AC(begin=5, end=7, value=1.0))
    cas.add(AC(begin=8, end=9, value=2.0))
    cas.add(AC(begin=10, end=14, value=3.0))

    return cas


def _get_feature_value_map(cas: Cas) -> dict:
    """Hilfsfunktion: Liefert Map name->value für alle T_FEATURE-Annotationen im CAS."""
    F = cas.typesystem.get_type(T_FEATURE)
    return {f.name: f.value for f in cas.select(T_FEATURE)}


def test_annotation_counter_total(cas: Cas, typesystem: TypeSystem):
    counter = FEL_AnnotationCounter("Token", unique=False)
    assert counter.count(cas) == 5  # inkl. 1 Duplikat
    assert counter.feature_name() == "Token_COUNT"

    # extract erzeugt Feature-Annotation
    counter.extract(cas)
    feats = _get_feature_value_map(cas)
    assert feats["Token_COUNT"] == pytest.approx(5.0)


def test_annotation_counter_unique_with_custom_to_string(cas: Cas, typesystem: TypeSystem):
    # Unique anhand der Spanne (begin,end) – der Duplikat-Token zählt dann nicht doppelt
    to_str = lambda a: f"{a.begin}-{a.end}"
    counter = FEL_AnnotationCounter("Token", unique=True, custom_to_string=to_str)
    assert counter.count(cas) == 4
    assert counter.feature_name() == "Token_COUNT_UNIQUE"

    counter.extract(cas)
    feats = _get_feature_value_map(cas)
    assert feats["Token_COUNT_UNIQUE"] == pytest.approx(4.0)


def test_feature_value_counter_specific_values(cas: Cas, typesystem: TypeSystem):
    # Zählt nur Tokens mit tag=="easy"
    fvc = FEL_FeatureValueCounter("Token", feature_path="tag", feature_values="easy")
    assert fvc.count(cas) == 3  # is, a, a(duplikat)
    assert fvc.feature_name() == "Token_easy_FEATURECOUNT"

    fvc.extract(cas)
    feats = _get_feature_value_map(cas)
    assert feats["Token_easy_FEATURECOUNT"] == pytest.approx(3.0)


def test_feature_value_counter_all_when_no_values_specified(cas: Cas, typesystem: TypeSystem):
    # Keine Allowed-Values => zählt alle Annotations des Typs
    fvc = FEL_FeatureValueCounter("Token", feature_path="tag", feature_values=None)
    assert fvc.count(cas) == 5
    assert fvc.feature_name() == "Token_FEATURECOUNT"

    fvc.extract(cas)
    feats = _get_feature_value_map(cas)
    assert feats["Token_FEATURECOUNT"] == pytest.approx(5.0)


def test_annotation_ratio_tokens_per_sentence(cas: Cas, typesystem: TypeSystem):
    ratio = FEL_AnnotationRatio(
        FEL_AnnotationCounter("Token"),
        FEL_AnnotationCounter("Sentence"),
    )
    assert ratio.feature_name() == "Token_COUNT_PER_Sentence_COUNT"

    ratio.extract(cas)
    feats = _get_feature_value_map(cas)
    # 5 Tokens (inkl. Duplikat) / 1 Sentence
    assert feats["Token_COUNT_PER_Sentence_COUNT"] == pytest.approx(5.0)


def test_annotation_ratio_zero_divisor_returns_zero(typesystem: TypeSystem):
    cas = cassis.Cas(typesystem=typesystem)
    cas.sofa_string = "X"

    # 1 Token, 0 Foo (Divisor)
    Token = typesystem.get_type("Token")
    cas.add(Token(begin=0, end=1, tag="x"))

    ratio = FEL_AnnotationRatio(
        FEL_AnnotationCounter("Token"),
        FEL_AnnotationCounter("Foo"),  # existiert im TS, aber es gibt keine Instanzen
    )

    ratio.extract(cas)
    feats = _get_feature_value_map(cas)
    assert feats["Token_COUNT_PER_Foo_COUNT"] == pytest.approx(0.0)


def test_annotation_ratio_zero_divisor_raises_in_strict(typesystem: TypeSystem):
    cas = cassis.Cas(typesystem=typesystem)
    cas.sofa_string = "X"

    # 1 Token, 0 Foo (Divisor)
    Token = typesystem.get_type("Token")
    cas.add(Token(begin=0, end=1, tag="x"))

    ratio = FEL_AnnotationRatio(
        FEL_AnnotationCounter("Token"),
        FEL_AnnotationCounter("Foo"),
    )
    # strict pro Instanz setzen (Klassenattribut wird dadurch überschrieben)
    ratio.strict = True

    with pytest.raises(ZeroDivisionError):
        ratio.extract(cas)


def test_length_on_token(cas: Cas, typesystem: TypeSystem):
    # Token-Längen: [4,2,1,4,1] -> min=1, max=4, mean=12/5=2.4
    length_extractor = FEL_Length("Token")
    assert length_extractor.extract(cas) is True

    feats = _get_feature_value_map(cas)
    assert feats["Token_length_min"] == pytest.approx(1.0)
    assert feats["Token_length_max"] == pytest.approx(4.0)
    assert feats["Token_length_mean"] == pytest.approx(2.4)


def test_min_max_mean_on_abstractness(cas: Cas, typesystem: TypeSystem):
    # Werte: [4.0, 1.0, 2.0, 3.0] -> min=1.0, max=4.0, mean=2.5
    mmm = FEL_Min_Max_Mean("org.lift.type.AbstractnessConcreteness", "value")
    assert mmm.extract(cas) is True

    feats = _get_feature_value_map(cas)
    assert feats["org.lift.type.AbstractnessConcreteness_min"] == pytest.approx(1.0)
    assert feats["org.lift.type.AbstractnessConcreteness_max"] == pytest.approx(4.0)
    assert feats["org.lift.type.AbstractnessConcreteness_mean"] == pytest.approx(2.5)


def test_convenience_extractors(cas: Cas, typesystem: TypeSystem):
    # FE_NumberOfSpellingAnomalies
    fe_sp = FE_NumberOfSpellingAnomalies()
    fe_sp.extract(cas)

    # FE_NounPhrasesPerSentence: 2 NC / 1 Sentence = 2.0
    fe_np = FE_NounPhrasesPerSentence()
    fe_np.extract(cas)

    # FE_TokensPerSentence: 5 Tokens / 1 Sentence = 5.0
    fe_tps = FE_TokensPerSentence()
    fe_tps.extract(cas)

    # FE_EasyWordRatio: 2 EasyWord / 5 Token = 0.4
    fe_ew = FE_EasyWordRatio()
    fe_ew.extract(cas)

    # FE_AbstractnessStats: identisch zu obigem Min/Max/Mean-Test
    fe_abs = FE_AbstractnessStats()
    fe_abs.extract(cas)

    feats = _get_feature_value_map(cas)
    assert feats["SpellingAnomaly_COUNT"] == pytest.approx(1.0)
    assert feats["NC_COUNT_PER_Sentence_COUNT"] == pytest.approx(2.0)
    assert feats["Token_COUNT_PER_Sentence_COUNT"] == pytest.approx(5.0)
    assert feats["EasyWord_COUNT_PER_Token_COUNT"] == pytest.approx(0.4)

    assert feats["org.lift.type.AbstractnessConcreteness_min"] == pytest.approx(1.0)
    assert feats["org.lift.type.AbstractnessConcreteness_max"] == pytest.approx(4.0)
    assert feats["org.lift.type.AbstractnessConcreteness_mean"] == pytest.approx(2.5)