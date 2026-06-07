"""Tests for the CAS-view -> udapi adapter (py_lift.stage.cas_adapter)."""
from py_lift.stage.cas_adapter import cas_view_to_conllu, cas_view_to_udapi_doc
from py_lift.tests.stage_fixtures import build_german_ctok_cas


def _token_rows(conllu):
    return [
        line.split("\t")
        for line in conllu.splitlines()
        if line and not line.startswith("#")
    ]


def test_conllu_columns_and_misc():
    view = build_german_ctok_cas().get_view("ctok")
    rows = _token_rows(cas_view_to_conllu(view, "ctok"))
    assert len(rows) == 6

    # The finite verb 'sieht' must get STTS VVFIN as XPOS (drives finite detection).
    verb = rows[2]
    assert verb[1] == "sieht"
    assert verb[3] == "VERB"      # UPOS
    assert verb[4] == "VVFIN"     # XPOS (STTS)
    assert verb[6] == "0"         # HEAD = root
    assert verb[7] == "root"      # DEPREL
    assert "TopoField=LK" in verb[9]
    assert "CasBegin=9" in verb[9] and "CasEnd=14" in verb[9]

    # Subject 'Kind' depends on 'sieht' (ordinal 3) via nsubj.
    subj = rows[1]
    assert subj[1] == "Kind" and subj[6] == "3" and subj[7] == "nsubj"


def test_udapi_doc_structure():
    doc = cas_view_to_udapi_doc(build_german_ctok_cas().get_view("ctok"), "ctok")
    assert len(doc.bundles) == 1
    nodes = doc.bundles[0].get_tree().descendants
    assert [n.form for n in nodes] == ["Das", "Kind", "sieht", "den", "Hund", "."]
    assert [n.ord for n in nodes] == [1, 2, 3, 4, 5, 6]

    verb = nodes[2]
    assert verb.xpos == "VVFIN"
    assert verb.deprel == "root"
    assert verb.misc["TopoField"] == "LK"
    # CAS offsets carried through for later anchoring.
    assert int(verb.misc["CasBegin"]) == 9 and int(verb.misc["CasEnd"]) == 14


def test_dependency_without_offsets_is_handled():
    # UDependency feature structures carry no begin/end; the adapter must fetch
    # them via select() (not select_covered) and still build a valid tree.
    conllu = cas_view_to_conllu(build_german_ctok_cas().get_view("ctok"), "ctok")
    rows = _token_rows(conllu)
    # exactly one root, and every non-root head points at a real ordinal
    heads = [int(r[6]) for r in rows]
    assert heads.count(0) == 1
    assert all(0 <= h <= len(rows) for h in heads)
