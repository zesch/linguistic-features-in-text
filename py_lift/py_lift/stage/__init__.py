"""Rule-based German verb-placement stage classification.

Contributed to py_lift from a standalone python project. Configured so that no outside-folder
dependency is required. The active pipeline is UD-dependency + topological-field based only.

Entry point: :func:`py_lift.stage.parser.analyze_single_document`,
which takes a udapi ``Document`` and returns a list of per-finite-verb clause
dicts with coarse and fine-grained stage labels applied.
"""
