import pytest
from cassis import Cas

from py_lift.util import get_lift_typesystem
from py_lift.dkpro import T_SENT, T_TOKEN, T_DEP, T_LEMMA, T_POS

from py_lift.extractors_specific import (
    FE_DependencyAndTreeStats,
    FE_CountCategoryAnnotator,
    FE_Per1kTokenStats,
    FE_LG_DocumentStats
)


# ----------------------------------------------------------------------
# Hilfsfunktionen / Fixtures
# ----------------------------------------------------------------------

@pytest.fixture
def ts():
    # Nutzt das gleiche TypeSystem wie die Extractor-Klassen
    return get_lift_typesystem()


@pytest.fixture
def base_cas(ts):
    cas = Cas(typesystem=ts)
    cas.sofa_string = "Dummy text"
    return cas


def feature_map(cas):
    """
    Liefert ein Dict: name -> value für alle FeatureAnnotationNumeric
    """
    return {
        fa.name: fa.value
        for fa in cas.select("org.lift.type.FeatureAnnotationNumeric")
    }


# ----------------------------------------------------------------------
# Tests für FE_CountCategoryAnnotator
# ----------------------------------------------------------------------

def test_fe_count_category_annotator_basic(ts, base_cas):
    """
    Testet, ob FE_CountCategoryAnnotator Konjunktionen, Subordinatoren
    und Tokens korrekt zählt und als FeatureAnnotationNumeric schreibt.
    """
    cas = base_cas

    token_type = ts.get_type(T_TOKEN)
    pos_type = ts.get_type("de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS")

    # Token 1: KON
    pos1 = pos_type(PosValue="KON")
    tok1 = token_type(begin=0, end=1, pos=pos1)

    # Token 2: KOUS
    pos2 = pos_type(PosValue="KOUS")
    tok2 = token_type(begin=2, end=3, pos=pos2)

    cas.add(pos1)
    cas.add(pos2)
    cas.add(tok1)
    cas.add(tok2)

    annotator = FE_CountCategoryAnnotator()
    annotator.extract(cas)

    feats = feature_map(cas)

    # 2 Tokens insgesamt
    assert feats["TokenCount"] == pytest.approx(2.0)

    # 1 Konjunktion (KON)
    assert feats["ConjunctionCount"] == pytest.approx(1.0)

    # 1 Subordinator (KOUS)
    assert feats["SubordinatorCount"] == pytest.approx(1.0)

    # Andere Kategorien sollten hier 0 sein
    assert feats["AdpositionCount"] == pytest.approx(0.0)
    assert feats["RelativePronounCount"] == pytest.approx(0.0)


# ----------------------------------------------------------------------
# Tests für FE_Per1kTokenStats
# ----------------------------------------------------------------------

def test_fe_per1k_token_stats_basic(ts, base_cas):
    """
    Testet, ob aus den Zählern von FE_CountCategoryAnnotator
    korrekte *_per_1k_tokens-Features berechnet werden.
    """
    cas = base_cas

    token_type = ts.get_type(T_TOKEN)
    pos_type = ts.get_type("de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS")

    # Wir erzeugen 2 Tokens:
    #   1x KON → ConjunctionCount = 1
    #   1x KOUS → SubordinatorCount = 1
    pos1 = pos_type(PosValue="KON")
    tok1 = token_type(begin=0, end=1, pos=pos1)

    pos2 = pos_type(PosValue="KOUS")
    tok2 = token_type(begin=2, end=3, pos=pos2)

    cas.add(pos1)
    cas.add(pos2)
    cas.add(tok1)
    cas.add(tok2)

    # Zuerst Zählungen erzeugen
    FE_CountCategoryAnnotator().extract(cas)

    # Dann Per-1k-Statistiken
    FE_Per1kTokenStats().extract(cas)

    feats = feature_map(cas)

    # TokenCount = 2, ConjunctionCount = 1 → 1000 * 1/2 = 500
    assert feats["Conjunctions_per_1k_tokens"] == pytest.approx(500.0)

    # Ebenfalls 1 Subordinator bei 2 Tokens
    assert feats["Subordinators_per_1k_tokens"] == pytest.approx(500.0)

    # Personalpronomen wurden nicht erzeugt
    assert feats["Personal_pronouns_per_1k_tokens"] == pytest.approx(0.0)


# ----------------------------------------------------------------------
# Tests für FE_DependencyAndTreeStats
# ----------------------------------------------------------------------

def test_fe_dependency_and_tree_stats_basic(ts, base_cas):
    """
    Testet die Berechnung der durchschnittlichen Abhängigkeitslängen,
    der durchschnittlichen maximalen Dependenzlänge und der Baumtiefe.
    """
    cas = base_cas

    token_type = ts.get_type(T_TOKEN)
    dep_type = ts.get_type("de.tudarmstadt.ukp.dkpro.core.api.syntax.type.dependency.Dependency")
    tree_type = ts.get_type("org.lift.type.TreeStructure")
    sent_type = ts.get_type(T_SENT)

    # Einfacher Satz mit 3 Tokens
    cas.sofa_string = "abc"
    sent = sent_type(begin=0, end=3)
    cas.add(sent)

    t0 = token_type(begin=0, end=1)  # Index 0
    t1 = token_type(begin=1, end=2)  # Index 1
    t2 = token_type(begin=2, end=3)  # Index 2

    cas.add(t0)
    cas.add(t1)
    cas.add(t2)

    # Dependencies:
    # t1 -> t0 (diff = -1)
    # t1 -> t2 (diff = +1)
    dep1 = dep_type(Governor=t1, Dependent=t0, DependencyType="nk", begin=0, end=2)
    dep2 = dep_type(Governor=t1, Dependent=t2, DependencyType="nk", begin=1, end=3)

    cas.add(dep1)
    cas.add(dep2)

    # Eine TreeStructure mit maxDepth = 3
    tree = tree_type(maxDepth=3.0, begin=0, end=3)
    cas.add(tree)

    extractor = FE_DependencyAndTreeStats()
    extractor.extract(cas)

    feats = feature_map(cas)

    # Beide Abhängigkeiten haben Betrag 1, jeweils einmal links und rechts
    assert feats["Average_Dependency_Length_Left"] == pytest.approx(1.0)
    assert feats["Average_Dependency_Length_Right"] == pytest.approx(1.0)
    assert feats["Average_Dependency_Length_All"] == pytest.approx(1.0)

    # Maximaler Dependenzabstand pro Satz ist 1
    assert feats["Average_Maximal_Dependency_Length"] == pytest.approx(1.0)

    # Baumtiefe aus TreeStructure
    assert feats["Average_Tree_Depth"] == pytest.approx(3.0)


# ----------------------------------------------------------------------
# Tests für FE_LG_DocumentStats
# ----------------------------------------------------------------------

def test_fe_lg_document_stats_basic(ts, base_cas):
    """
    Testet einige zentrale Kennzahlen von FE_LG_DocumentStats an einem
    einfachen Beispiel mit verbaler Koordination und einem Subjekt.
    """
    cas = base_cas

    # Typen aus dem TypeSystem
    sent_type = ts.get_type(T_SENT)
    token_type = ts.get_type(T_TOKEN)
    dep_type = ts.get_type(T_DEP)
    pos_type = ts.get_type(T_POS)
    lemma_type = ts.get_type(T_LEMMA)

    # Satz: "Er schläft und liest."
    text = "Er schläft und liest."
    cas.sofa_string = text
    sent = sent_type(begin=0, end=len(text))
    cas.add(sent)

    # Tokens + POS + Lemma
    # Er (Subjekt, PPER)
    pos_er = pos_type(PosValue="PPER")
    lem_er = lemma_type(value="er")
    t0 = token_type(begin=0, end=2, pos=pos_er, lemma=lem_er)

    # schläft (VVFIN, finites Verb)
    pos_schlaeft = pos_type(PosValue="VVFIN")
    lem_schlaeft = lemma_type(value="schlafen")
    t1 = token_type(begin=3, end=10, pos=pos_schlaeft, lemma=lem_schlaeft)

    # und (KON, Konjunktion)
    pos_und = pos_type(PosValue="KON")
    lem_und = lemma_type(value="und")
    t2 = token_type(begin=11, end=14, pos=pos_und, lemma=lem_und)

    # liest (VVFIN, finites Verb)
    pos_liest = pos_type(PosValue="VVFIN")
    lem_liest = lemma_type(value="lesen")
    t3 = token_type(begin=15, end=20, pos=pos_liest, lemma=lem_liest)

    cas.add(pos_er); cas.add(lem_er)
    cas.add(pos_schlaeft); cas.add(lem_schlaeft)
    cas.add(pos_und); cas.add(lem_und)
    cas.add(pos_liest); cas.add(lem_liest)

    cas.add(t0); cas.add(t1); cas.add(t2); cas.add(t3)

    # Dependencies:
    #  t1 --SB--> t0  (Er ist Subjekt von schläft)
    dep_sb = dep_type(Governor=t1, Dependent=t0, DependencyType="SB", begin=t0.begin, end=t1.end)

    #  t1 --cd--> t2  (und als Koordinator)
    dep_cd = dep_type(Governor=t1, Dependent=t2, DependencyType="cd", begin=t1.begin, end=t2.end)

    #  t2 --cj--> t3  (liest als verbales Konjunkt)
    dep_cj = dep_type(Governor=t2, Dependent=t3, DependencyType="cj", begin=t2.begin, end=t3.end)

    cas.add(dep_sb)
    cas.add(dep_cd)
    cas.add(dep_cj)

    extractor = FE_LG_DocumentStats()
    extractor.extract(cas)

    feats = feature_map(cas)

    # Nur 1 Konj-Use mit Rel 'cd', keine 'ju' → Anteil ohne linke Klausel = 0
    assert feats["Share_of_conj_uses_without_left_clause"] == pytest.approx(0.0)

    # Es gibt 1 Satz mit 2 finiten Verben → kein satz ohne finites Verb
    assert feats["Proportion_S_without_finite_verb"] == pytest.approx(0.0)

    # Modalverben = 0, Verben insgesamt = 2
    assert feats["Proportion_of_modal_verbs_out_of_all_verbs"] == pytest.approx(0.0)

    # 1 Satz, der Verben enthält → keine sätze ohne Verb
    assert feats["Proportion_S_without_verb"] == pytest.approx(0.0)

    # Subjektposition: Subjekt vor erstem finiten Verb → keine Inversion
    assert feats["Proportion_of_Subj_Vfin_Inversions"] == pytest.approx(0.0)

    # 2 finite Verben, eines davon ohne eigenes Subjekt (liest)
    assert feats["Proportion_of_subjectless_finite_verbs"] == pytest.approx(0.5)

    # Es gibt eine Koordination, und sie ist zwischen Verben → Anteil = 1
    assert feats["Proportion_of_coordination_between_verbs"] == pytest.approx(1.0)

    # Keine lexikalischen NPs (NN/NE) → Durchschnittsgröße = 0
    assert feats["Average_Size_Of_Lexical_NP"] == pytest.approx(0.0)

    # 2 finite Verben im einzigen Satz
    assert feats["Average_Number_Of_Finite_Verbs"] == pytest.approx(2.0)

    # 2 Verben insgesamt im einzigen Satz
    assert feats["Average_Number_Of_Verbs"] == pytest.approx(2.0)