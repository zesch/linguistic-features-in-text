"""Rule-based German verb-placement stage classification.

Vendored into py_lift from the standalone
``simple_rule_based_stage_classification`` project so that no outside-folder
dependency is required. Dead Tiger-dependency code and the Excel / CoNLL-U
file I/O (exporters) were intentionally left out; the active pipeline is
UD-dependency + topological-field based only.

Entry point for callers: :func:`py_lift.stage.parser.analyze_single_document`,
which takes a udapi ``Document`` and returns a list of per-finite-verb clause
dicts with coarse and fine-grained stage labels applied.
"""
