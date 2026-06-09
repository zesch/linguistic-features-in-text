import argparse
import os
import subprocess
import sys
from typing import Sequence

import spacy

DEFAULT_SPACY_MODELS = {
    "en": "en_core_web_md",
    "de": "de_core_news_lg",
    "fr": "fr_core_news_lg",
    "sl": "sl_core_news_sm",
    "tr": "tr_core_news_md",
}

DEFAULT_MODEL_URLS = {
    "tr": "https://pypi.cats.fernuni-hagen.de/packages/tr_core_news_md-1.0-py3-none-any.whl",
}


def get_default_spacy_model(language: str) -> str:
    try:
        return DEFAULT_SPACY_MODELS[language]
    except KeyError as exc:
        supported = ", ".join(sorted(DEFAULT_SPACY_MODELS.keys()))
        raise ValueError(f"Language '{language}' not supported. Supported: {supported}") from exc


def _run(cmd: Sequence[str]) -> None:
    subprocess.run(cmd, check=True)


def _parse_model_url_overrides(values: Sequence[str] | None) -> dict[str, str]:
    overrides: dict[str, str] = {}
    if not values:
        return overrides

    for raw in values:
        if "=" not in raw:
            raise ValueError(f"Invalid --model-url value '{raw}'. Expected format: <lang>=<url>")
        lang, url = raw.split("=", 1)
        lang = lang.strip().lower()
        url = url.strip()
        if not lang or not url:
            raise ValueError(f"Invalid --model-url value '{raw}'. Expected format: <lang>=<url>")
        overrides[lang] = url
    return overrides


def _resolve_model_url(language: str, model_urls: dict[str, str] | None = None) -> str | None:
    language = language.lower()
    env_url = os.getenv(f"PY_LIFT_MODEL_URL_{language.upper()}")
    if env_url:
        return env_url

    if model_urls and language in model_urls:
        return model_urls[language]

    return DEFAULT_MODEL_URLS.get(language)


def install_spacy_model(language: str, model_name: str, model_urls: dict[str, str] | None = None) -> None:
    url = _resolve_model_url(language, model_urls=model_urls)
    if url:
        _run([sys.executable, "-m", "pip", "install", url])
        return

    _run([sys.executable, "-m", "spacy", "download", model_name])


def ensure_spacy_model(
    language: str,
    model_name: str | None = None,
    auto_install: bool = False,
    model_urls: dict[str, str] | None = None,
):
    resolved_model = model_name or get_default_spacy_model(language)
    try:
        return spacy.load(resolved_model)
    except OSError as exc:
        if not auto_install:
            raise OSError(
                f"spaCy model '{resolved_model}' is not installed. "
                "Install it via 'python -m py_lift.model_setup --languages "
                f"{language}' or enable auto-install in Spacy_Preprocessor."
            ) from exc

        install_spacy_model(language=language, model_name=resolved_model, model_urls=model_urls)
        return spacy.load(resolved_model)


def main() -> int:
    parser = argparse.ArgumentParser(description="Install optional spaCy models used by py_lift.")
    parser.add_argument(
        "--languages",
        nargs="+",
        required=True,
        help="Language codes to install default models for (e.g., en de fr sl tr)",
    )
    parser.add_argument(
        "--model-url",
        action="append",
        default=[],
        help="Optional override in format <lang>=<url>. Can be provided multiple times.",
    )
    args = parser.parse_args()
    model_urls = _parse_model_url_overrides(args.model_url)

    failed = False
    for language in args.languages:
        model_name = get_default_spacy_model(language)
        try:
            install_spacy_model(language=language, model_name=model_name, model_urls=model_urls)
            print(f"Installed model for {language}: {model_name}")
        except Exception as exc:
            failed = True
            print(f"Failed to install model for {language} ({model_name}): {exc}", file=sys.stderr)

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
