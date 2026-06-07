"""Tests for SE_StageAnnotator (py_lift.annotators.stage)."""
import contextlib
import io
import logging

from py_lift.annotators.stage import SE_StageAnnotator
from py_lift.dkpro import T_STAGE, T_STAGED_VERB
from py_lift.tests.stage_fixtures import build_german_ctok_cas
from py_lift.util import load_lift_typesystem

# The vendored engine logs verbosely; keep test output clean.
logging.getLogger("stage_classification").setLevel(logging.ERROR)


def _run(cas, **kwargs):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        return SE_StageAnnotator(**kwargs).process(cas)


def test_writes_stage_and_stagedverb():
    cas = build_german_ctok_cas()
    assert _run(cas, views=["ctok"]) is True

    view = cas.get_view("ctok")
    stages = list(view.select(T_STAGE))
    assert [(s.name, s.fine) for s in stages] == [("SVO", "SVO_core")]
    assert all(s.origin == "rule_based" for s in stages)
    # anchored on the finite verb 'sieht' (offsets 9-14)
    assert (stages[0].begin, stages[0].end) == (9, 14)

    staged = list(view.select(T_STAGED_VERB))
    assert len(staged) == 1
    sv = staged[0]
    assert (sv.begin, sv.end) == (9, 14)
    assert sv.clauseType == "dec"
    assert sv.finiteVerbIsSemroot is True
    assert sv.separatedVerbPrefix is False
    assert sv.semrootOrd == 3
    assert sv.clausalGovernorOrd == 0
    assert sv.topology == "VF:2|MF:5"
    assert sv.origin == "rule_based"


def test_topology_fields_are_configurable():
    cas = build_german_ctok_cas()
    _run(cas, views=["ctok"], topology_fields=["LK"])
    sv = next(iter(cas.get_view("ctok").select(T_STAGED_VERB)))
    # only the LK field (the finite verb, ordinal 3) is recorded now
    assert sv.topology == "LK:3"


def test_refuses_spacy_view():
    cas = build_german_ctok_cas(view_name="spacy_ctok")
    assert _run(cas, views=["spacy_ctok"]) is False
    view = cas.get_view("spacy_ctok")
    assert list(view.select(T_STAGE)) == []
    assert list(view.select(T_STAGED_VERB)) == []


def test_missing_view_is_skipped():
    cas = build_german_ctok_cas()
    assert _run(cas, views=["does_not_exist"]) is False


def test_overwrite_is_idempotent():
    cas = build_german_ctok_cas()
    _run(cas, views=["ctok"], overwrite=True)
    view = cas.get_view("ctok")
    first = (len(list(view.select(T_STAGE))), len(list(view.select(T_STAGED_VERB))))
    _run(cas, views=["ctok"], overwrite=True)
    second = (len(list(view.select(T_STAGE))), len(list(view.select(T_STAGED_VERB))))
    assert first == second == (1, 1)


def test_gold_annotations_are_preserved():
    # A pre-existing gold Stage (no origin) must survive an overwrite run.
    cas = build_german_ctok_cas()
    view = cas.get_view("ctok")
    Stage = load_lift_typesystem().get_type(T_STAGE)
    view.add(Stage(begin=9, end=14, name="SVO"))  # gold-like: origin unset

    _run(cas, views=["ctok"], overwrite=True)

    gold = [s for s in view.select(T_STAGE) if s.origin is None]
    predicted = [s for s in view.select(T_STAGE) if s.origin == "rule_based"]
    assert len(gold) == 1
    assert len(predicted) == 1
