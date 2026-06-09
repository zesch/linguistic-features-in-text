PyLift is the Python branch of the [LiFT library](https://github.com/zesch/linguistic-features-in-text).

## Installation

Core package:

```bash
pip install py_lift
```

Optional tooling dependencies (examples/workbench):

```bash
poetry install --with examples
```

spaCy language models are optional and must be installed separately when using
`Spacy_Preprocessor` with the default model names:

```bash
python -m py_lift.model_setup --languages en de fr sl tr
```

For Turkish (`tr_core_news_md`) and for `SE_AbstractnessAnnotator`
(`lift-resources-lists`), install the required internal packages from your
organization's package source.

`py_lift.model_setup` supports language-specific wheel URLs via built-in defaults
and overrides. Turkish currently uses this built-in URL by default:

`https://pypi.cats.fernuni-hagen.de/packages/tr_core_news_md-1.0-py3-none-any.whl`

You can override sources for any language via environment variables:

```bash
export PY_LIFT_MODEL_URL_TR="https://your-internal-source/tr_core_news_md-1.0-py3-none-any.whl"
python -m py_lift.model_setup --languages tr
```

Or via CLI:

```bash
python -m py_lift.model_setup --languages tr --model-url tr=https://your-internal-source/tr_core_news_md-1.0-py3-none-any.whl
```

You can also let the preprocessor auto-install missing models at runtime:

```python
from py_lift.preprocessing import Spacy_Preprocessor

prep = Spacy_Preprocessor("en", auto_install_models=True)
```

## Standalone Python example

Run a non-visual end-to-end pipeline example:

```bash
python examples/pure_python_pipeline.py
```

The script is located at `examples/pure_python_pipeline.py` and demonstrates:

- language detection
- spaCy preprocessing
- spelling anomaly annotation
- readability + count feature extraction
- plain stdout output (no visualization)

Other examples (now also in top-level `examples/`):

- `examples/visualization_streamlit.py`
- `examples/visualization_notebook.ipynb`

## Release (PyPI)

Short release checklist:

1. Update the version in `pyproject.toml`.
2. Run tests:

    ```bash
    poetry install --with dev
    poetry run pytest
    ```

3. Build distribution artifacts:

    ```bash
    poetry build
    ```

4. Publish:

    ```bash
    export POETRY_PYPI_TOKEN_PYPI="pypi-XXXXXXXXXXXXXXXXXXXX"
    poetry publish
    ```