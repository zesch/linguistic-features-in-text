"""Tests for the batch runner (py_lift.stage.runner)."""
import logging

import cassis
import pytest

from py_lift.dkpro import T_STAGE, T_STAGED_VERB
from py_lift.stage.runner import run
from py_lift.tests.stage_fixtures import build_german_ctok_cas
from py_lift.utils.core import get_lift_typesystem

logging.getLogger("stage_classification").setLevel(logging.ERROR)


def test_runner_writes_annotated_output(tmp_path):
    in_path = tmp_path / "doc.xmi"
    build_german_ctok_cas().to_xmi(str(in_path))

    written = run(
        [str(in_path)],
        views=["ctok"],
        output_dir=str(tmp_path / "out"),
        overwrite=True,
    )
    assert len(written) == 1

    out = cassis.load_cas_from_xmi(
        open(written[0], "rb"), typesystem=get_lift_typesystem(), lenient=False
    )
    view = out.get_view("ctok")
    predicted = [s for s in view.select(T_STAGE) if s.origin == "rule_based"]
    assert len(predicted) == 1
    assert len(list(view.select(T_STAGED_VERB))) == 1


def test_runner_refuses_spacy_views():
    # Refusal happens before any file is touched.
    with pytest.raises(ValueError):
        run(["nonexistent.xmi"], views=["spacy_ctok"])


def test_runner_does_not_overwrite_input(tmp_path):
    # With a suffix that would collide with the input name, the input is kept.
    in_path = tmp_path / "doc.xmi"
    build_german_ctok_cas().to_xmi(str(in_path))
    written = run([str(in_path)], views=["ctok"], suffix=".xmi", output_dir=str(tmp_path))
    assert written == []  # would have overwritten input -> skipped
