# Linguistic Features in Text (LiFT)

LiFT is a library for extracting linguistic features from textual data.

LiFT is currently maintained by:
* [Procoli](https://www.fernuni-hagen.de/computerlinguistik/), FernUniversität in Hagen
* [Educational Measurement and Data Science](https://www.leibniz-ipn.de/en/the-ipn/about-us/staff/andrea-horbach), IPN Kiel

## First steps

See: [First Steps with LiFT](docs/first-steps.md)

## Philosophy
We rely on a UIMA CAS repesentation model based on the [DKPro Core](https://dkpro.github.io/dkpro-core/) type system and preprocessing components.
This makes LiFT multi-lingual, supporting all the [languages](https://dkpro.github.io/dkpro-core/releases/2.2.0/docs/model-reference.html) included in DKPro Core.
However, not all structures might be supported in each language.

LiFT distinguishes betwen linguistic structures (lemmas, POS tags, syllables, spelling errors, etc.) and features (based on these structures).
Structures are represented in the document model and can be visualized.
Features are numeric values that represent properties of the document, e.g. SpellingErrorRatio may have a value of 0.06 meaning that 6% of all tokens in the text contain a spelling error.

The project is under heavy development, but we are working towards a stable release.

We plan to implement the following types of structures:
* casing
* lemmas
* quotations
* POS tags
* phrases
* spelling errors
* stems
* syllables
* tokens
* T-units
* voice

We also support various meta-features of linguistic complexity:
* readability measures
* type-token ratio (TTR)


