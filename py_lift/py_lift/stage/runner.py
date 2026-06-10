"""Batch runner: apply the German stage annotator to a set of XMI files.

Loads each XMI under the singleton LIFT TypeSystem, runs
:class:`py_lift.annotators.stage.SE_StageAnnotator` on the desired views
(``ctok`` by default; ``*_th1`` etc. allowed; ``spacy_*`` refused), and writes
a new XMI carrying the predicted ``org.dakoda.Stage`` / ``org.dakoda.StagedVerb``
annotations.

Usage::

    python -m py_lift.stage.runner -d DATA_DIR -r "*.xmi" \\
        --views ctok mbartgec_th1 --overwrite --output-dir OUT
"""
from __future__ import annotations

import argparse
import glob
import logging
import os
from typing import List, Sequence

from py_lift.annotators.stage import (
    SE_StageAnnotator,
    DEFAULT_TOPOLOGY_FIELDS,
    SPACY_VIEW_PREFIX,
)
from py_lift.dkpro import T_STAGE, T_STAGED_VERB
from py_lift.utils.core import load_cas_from_xmi_with_lift_ts

logger = logging.getLogger(__name__)

DEFAULT_PATTERN = "*.xmi"
DEFAULT_SUFFIX = "_staged.xmi"
DEFAULT_VIEWS = ("ctok",) # by default, only ctok


def _output_path(in_path: str, suffix: str, output_dir: str | None) -> str:
    base = os.path.basename(in_path)
    stem = base[:-4] if base.lower().endswith(".xmi") else base
    out_name = stem + suffix
    return os.path.join(output_dir or os.path.dirname(in_path), out_name)


def _count_predicted(cas, views: Sequence[str], origin: str) -> int:
    total = 0
    available = {sofa.sofaID for sofa in cas.sofas}
    for name in views:
        if name not in available:
            continue
        view = cas.get_view(name)
        for type_name in (T_STAGE, T_STAGED_VERB):
            total += sum(
                1 for fs in view.select(type_name) if getattr(fs, "origin", None) == origin
            )
    return total


def run(
    files: Sequence[str],
    views: Sequence[str] = DEFAULT_VIEWS,
    *,
    language: str = "de",
    topology_fields: Sequence[str] = DEFAULT_TOPOLOGY_FIELDS,
    origin: str = "rule_based",
    overwrite: bool = False,
    suffix: str = DEFAULT_SUFFIX,
    output_dir: str | None = None,
    strict: bool = True,
) -> List[str]:
    """Annotate every file in ``files``; return the list of written output paths."""
    spacy_views = [v for v in views if v.startswith(SPACY_VIEW_PREFIX)]
    if spacy_views:
        raise ValueError(f"Refusing to label spaCy views: {spacy_views}")

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    annotator = SE_StageAnnotator(
        language=language,
        views=views,
        topology_fields=topology_fields,
        origin=origin,
        overwrite=overwrite,
        strict=strict,
    )

    written: List[str] = []
    for in_path in files:
        out_path = _output_path(in_path, suffix, output_dir)
        if os.path.abspath(out_path) == os.path.abspath(in_path):
            logger.error("Output would overwrite input file %s; skipping", in_path)
            continue
        try:
            cas = load_cas_from_xmi_with_lift_ts(in_path)
            annotator.process(cas)
            n = _count_predicted(cas, views, origin)
            cas.to_xmi(out_path)
            written.append(out_path)
            logger.info("%s -> %s (%d predicted annotations)", in_path, out_path, n)
        except Exception as e:  # keep the batch going on per-file failures
            logger.error("Failed to process %s: %s", in_path, e)
    return written


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Apply rule-based German verb-placement (= stage) annotation to XMI files."
    )
    parser.add_argument(
        "-d", dest="data_dir", default=".", help="Directory with XMI input files."
    )
    parser.add_argument(
        "-r",
        dest="pattern",
        default=DEFAULT_PATTERN,
        help=f"Glob pattern for input files (default: {DEFAULT_PATTERN}).",
    )
    parser.add_argument(
        "--views",
        nargs="+",
        default=list(DEFAULT_VIEWS),
        help="View(s) to annotate (default: ctok). NB: spaCy views are refused.",
    )
    parser.add_argument(
        "--topology-fields",
        nargs="+",
        default=list(DEFAULT_TOPOLOGY_FIELDS),
        help=f"Topological fields recorded on StagedVerb (default: {' '.join(DEFAULT_TOPOLOGY_FIELDS)}).",
    )
    parser.add_argument("--origin", default="rule_based", help="origin feature value.")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Remove previously written annotations of the same origin before writing.",
    )
    parser.add_argument(
        "--suffix",
        default=DEFAULT_SUFFIX,
        help=f"Suffix for output filenames (default: {DEFAULT_SUFFIX}).",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Directory for output files (default: alongside each input).",
    )
    parser.add_argument("--language", default="de")
    parser.add_argument(
        "--no-strict",
        dest="strict",
        action="store_false",
        help="Do not raise on language mismatch / missing types.",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    # The rule engine would log verbosely at INFO per node; we keep it quiet.
    # All engine modules log under the "stage_classification" namespace.
    logging.getLogger("stage_classification").setLevel(logging.WARNING)

    pattern = os.path.join(args.data_dir, args.pattern)
    files = sorted(glob.glob(pattern))
    if not files:
        logger.warning("No files matched %s", pattern)
        return

    logger.info("Found %d file(s); views=%s", len(files), args.views)
    try:
        written = run(
            files,
            views=args.views,
            language=args.language,
            topology_fields=args.topology_fields,
            origin=args.origin,
            overwrite=args.overwrite,
            suffix=args.suffix,
            output_dir=args.output_dir,
            strict=args.strict,
        )
    except ValueError as e:
        parser.error(str(e))  # clean message + exit code 2
    logger.info("Done. Wrote %d file(s).", len(written))


if __name__ == "__main__":
    main()
