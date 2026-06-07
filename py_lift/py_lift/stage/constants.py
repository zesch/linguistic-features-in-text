"""
Constants and data structures for German verb placement stage classification.

This module contains all shared constants, configuration values, and dataclasses
used across the stage classification system.
"""

import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from udapi.core.node import Node

# Set up logging with TSV format
LOG_FILE = os.path.join(
    os.path.dirname(__file__), "simple_rule_based_stage_baseline.log.tsv"
)

# Flag to track if logging has been configured
_logging_configured = False

# Default output filename suffix for CoNLL-U files with predicted stages
DEFAULT_OUTPUT_SUFFIX = "_predictedVerbStages.conllu"

# Maximum character length for text fields in Excel output
TEXT_TRUNCATION_LIMIT = 150

# Random seed for reproducible file ordering
RANDOM_SEED = 42

# Maximum number of sentences to process per file (0 = unlimited)
MAX_SENTENCES = 100000

# Dependency relations that indicate clause heads
CLAUSE_HEAD_RELATIONS = ["root", "advcl", "acl", "csubj", "ccomp", "xcomp"]

# Dependency relations for functional verbs (auxiliaries, copulas)
FUNCTIONAL_VERB_RELATIONS = ["aux", "aux:pass", "cop"]

# German topological fields
TOPOLOGICAL_FIELDS = ["VF", "LK", "MF", "VC", "NF", "C", "KOORD"]

# Stage names for classification
STAGE_NAMES = ["ADV", "SVO", "INV", "SEP", "VEND"]

FINE_STAGE_NAMES = [f"fine_{stage}" for stage in STAGE_NAMES]

PLAUSIBLE_NP_INTERNAL_ADVS = ["auch", "also", "besten", "nur", "sogar"]
# comment: above, "besten" really repsresents "am besten"


class FineLabel(Enum):
    """
    Fine-grained stage classification labels.

    Each label represents a different relationship between the clause
    and the target word order structure:

    - CORE: Prototypical use of the structure
    - PERI: Less prototypical but valid use of the structure
    - ZERO: No evidence for the structure (default)
    - NOEV: Insufficient evidence (close but not quite)
    - ANTI: Structure correctly avoided (non-use is grammatically preferred)
    - NO: Structure not used but should have been (omission error)
    - NEGATED: Structure used but ungrammatical in context (commission error)
    """

    CORE = "core"  # SVO_core - prototypical use
    PERI = "peri"  # SVO_peri - peripheral/less prototypical use
    ZERO = "zero"  # SVO_zero - no evidence (default)
    NOEV = "noev"  # SVO_noev - insufficient evidence (close but not quite)
    ANTI = "anti"  # SVO_anti - correctly avoided
    NO = "NO"  # NO_SVO - should have been used but wasn't
    NEGATED = "!"  # !SVO - used but ungrammatical in context

    def to_coarse(self) -> bool:
        """
        Convert fine label to coarse boolean.

        Returns:
            True for CORE and PERI (positive evidence),
            False for all other labels.
        """
        return self in {FineLabel.CORE, FineLabel.PERI}

    def format_for_stage(self, stage_name: str) -> str:
        """
        Format the fine label for a specific stage.

        Args:
            stage_name: The stage name (e.g., "SVO", "ADV")

        Returns:
            Formatted string like "SVO_core", "NO_SVO", or "!SVO"
        """
        if self == FineLabel.NEGATED:
            return f"!{stage_name}"
        elif self == FineLabel.NO:
            return f"NO_{stage_name}"
        else:
            return f"{stage_name}_{self.value}"


@dataclass
class FineStageClassification:
    """
    Fine-grained stage classification for all five developmental stages.

    Each stage is assigned a FineLabel indicating the relationship between
    the clause and the target word order structure. Default is ZERO
    (no evidence).
    """

    ADV: FineLabel = FineLabel.ZERO
    SVO: FineLabel = FineLabel.ZERO
    INV: FineLabel = FineLabel.ZERO
    SEP: FineLabel = FineLabel.ZERO
    VEND: FineLabel = FineLabel.ZERO

    def to_coarse(self) -> "StageClassification":
        """
        Derive coarse boolean labels from fine-grained labels.

        Returns:
            StageClassification with boolean values derived from fine labels.
        """
        return StageClassification(
            ADV=self.ADV.to_coarse(),
            SVO=self.SVO.to_coarse(),
            INV=self.INV.to_coarse(),
            SEP=self.SEP.to_coarse(),
            VEND=self.VEND.to_coarse(),
        )

    def to_dict(self) -> Dict[str, str]:
        """
        Convert to dictionary with formatted fine label strings.

        Returns:
            Dictionary mapping stage names to formatted fine label strings.
        """
        return {
            "ADV": self.ADV.format_for_stage("ADV"),
            "SVO": self.SVO.format_for_stage("SVO"),
            "INV": self.INV.format_for_stage("INV"),
            "SEP": self.SEP.format_for_stage("SEP"),
            "VEND": self.VEND.format_for_stage("VEND"),
        }

    @classmethod
    def from_coarse_booleans(cls, stages: Dict[str, bool]) -> "FineStageClassification":
        """
        Create FineStageClassification from coarse boolean values.

        This is a compatibility layer for existing rules that return booleans.
        Maps True -> CORE, False -> ZERO.

        Args:
            stages: Dictionary with boolean values for each stage.

        Returns:
            FineStageClassification with CORE for True, ZERO for False.
        """
        return cls(
            ADV=FineLabel.CORE if stages.get("ADV", False) else FineLabel.ZERO,
            SVO=FineLabel.CORE if stages.get("SVO", False) else FineLabel.ZERO,
            INV=FineLabel.CORE if stages.get("INV", False) else FineLabel.ZERO,
            SEP=FineLabel.CORE if stages.get("SEP", False) else FineLabel.ZERO,
            VEND=FineLabel.CORE if stages.get("VEND", False) else FineLabel.ZERO,
        )


# Create a custom formatter for TSV output
class TSVFormatter(logging.Formatter):
    """Custom log formatter that outputs tab-separated values."""

    def format(self, record):
        # Format: timestamp\tlevel\tfunction\tmessage
        timestamp = self.formatTime(record, self.datefmt)
        return (
            f"{timestamp}\t{record.levelname}\t{record.funcName}\t{record.getMessage()}"
        )


def configure_logging() -> None:
    """
    Configure the root logger for the application.

    This should be called once at application startup (in the main entry point).
    All modules will then share the same logging configuration.
    """
    global _logging_configured
    if _logging_configured:
        return

    # Get the root logger for this package
    root_logger = logging.getLogger("stage_classification")
    root_logger.setLevel(logging.DEBUG)

    # File handler for TSV log
    # we use "w", not "a" as we want a new log run
    file_handler = logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(TSVFormatter(datefmt="%Y-%m-%d %H:%M:%S"))

    # Console handler for important messages
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))

    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    _logging_configured = True


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.

    All loggers are children of the 'stage_classification' logger,
    so they inherit its handlers and configuration.

    Args:
        name: The name for the logger (typically __name__).

    Returns:
        A configured logging.Logger instance.
    """
    # Use a common parent logger so all modules share the same handlers
    return logging.getLogger(f"stage_classification.{name}")


@dataclass
class StageClassification:
    """Boolean flags for each developmental stage."""

    ADV: bool = False
    SVO: bool = False
    INV: bool = False
    SEP: bool = False
    VEND: bool = False

    def to_dict(self) -> Dict[str, bool]:
        """Convert to dictionary format for backward compatibility."""
        return {
            "ADV": self.ADV,
            "SVO": self.SVO,
            "INV": self.INV,
            "SEP": self.SEP,
            "VEND": self.VEND,
        }


@dataclass
class ClauseData:
    """
    Data structure representing a finite verb clause with its syntactic properties.

    This dataclass holds all information about a clause including verb position,
    semantic root, topological fields, arguments, and stage classifications.
    """

    # Source information
    filename: str
    sent_id: str
    full_sentence: str

    # Verb information
    verb: Any  # udapi Node
    verb_form: str
    verb_index: int
    verb_topo: Optional[str]
    verb_deprel: str

    # Semantic root information
    semroot: Any  # udapi Node
    semroot_form: str
    semroot_index: int
    semroot_topo: str
    semroot_deprel: str

    # Clause properties
    matrix: bool
    clause_text: str
    clause_type: str
    clausal_governor: Optional[Any]  # udapi Node or None
    nodes: Any  # list of udapi Nodes

    # Arguments (lists of udapi Nodes)
    subj: List[Any] = field(default_factory=list)
    obj: List[Any] = field(default_factory=list)
    obl: List[Any] = field(default_factory=list)

    # Verb cluster
    verb_cluster_other: List[Any] = field(default_factory=list)

    # Topology mapping
    # topology: Dict[str, List[tuple]] = field(default_factory=dict)
    topology: Dict[str, List[Node]] = field(default_factory=dict)

    # Stage classifications
    fine_stages: Optional[FineStageClassification] = None
    stages: Optional[StageClassification] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary format for backward compatibility with existing code.

        Returns:
            Dictionary with all clause data in the legacy format.
        """
        return {
            "topology": self.topology,
            "full sentence": self.full_sentence,
            "_filename": self.filename,
            "sent_id": self.sent_id,
            "subj": self.subj,
            "obj": self.obj,
            "obl": self.obl,
            "verb": self.verb,
            "verb_form": self.verb_form,
            "verb_index": self.verb_index,
            "verb_topo": self.verb_topo,
            "verb_deprel": self.verb_deprel,
            "semroot": self.semroot,
            "semroot_form": self.semroot_form,
            "semroot_topo": self.semroot_topo,
            "semroot_index": self.semroot_index,
            "semroot_deprel": self.semroot_deprel,
            "matrix": self.matrix,
            "clause_text": self.clause_text,
            "clause_type": self.clause_type,
            "clausal_governor": self.clausal_governor,
            "nodes": self.nodes,
            "verb_cluster_other": self.verb_cluster_other,
            "fine_stages": self.fine_stages,
            "fine_stages_dict": self.fine_stages.to_dict()
            if self.fine_stages
            else None,
            "stages": self.stages.to_dict() if self.stages else None,
        }
