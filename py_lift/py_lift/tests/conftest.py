import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--run-model-tests",
        action="store_true",
        default=False,
        help="Run tests marked with 'requires_models' that depend on external NLP models.",
    )


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "requires_models: tests that require external NLP models to be installed",
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--run-model-tests"):
        return

    skip_model_tests = pytest.mark.skip(
        reason="requires external NLP models; run with --run-model-tests",
    )
    for item in items:
        if "requires_models" in item.keywords:
            item.add_marker(skip_model_tests)
