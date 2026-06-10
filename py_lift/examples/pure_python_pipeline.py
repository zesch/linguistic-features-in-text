"""Standalone non-visual py_lift example.

This script runs a small pipeline and prints results to stdout.
"""

from py_lift.annotators.misc import SE_SpellErrorAnnotator
from py_lift.dkpro import T_ANOMALY
from py_lift.extractors import FEL_AnnotationCounter
from py_lift.preprocessing import Spacy_Preprocessor
from py_lift.readability import FE_TextstatFleschIndex
from py_lift.utils.core import detect_language, df_features


def main() -> None:
    text = "This is a tast. A smoll one."
    language = detect_language(text)
    if language != "en":
        raise RuntimeError(
            f"This example expects English input but detected '{language}'."
        )

    preprocessor = Spacy_Preprocessor(language="en", auto_install_models=True)
    cas = preprocessor.run(text)

    SE_SpellErrorAnnotator("en").process(cas)
    FE_TextstatFleschIndex("en").extract(cas)
    FEL_AnnotationCounter("SpellingAnomaly").extract(cas)

    anomalies = list(cas.select(T_ANOMALY))
    print("Detected language:", language)
    print("Spelling anomalies:", len(anomalies))

    features = df_features(cas)
    print("\nExtracted features:")
    print(features)


if __name__ == "__main__":
    main()
