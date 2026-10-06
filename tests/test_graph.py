import subprocess

import pytest

from rca.analysis import analyze
from rca.data.generator import generate
from rca.ui.graph import _q, build_dot


def _dot(scenario="A"):
    return build_dot(analyze(generate(scenario, seed=1)[0]))


def test_dot_links_evidence_to_hypotheses_and_hypotheses_to_checks():
    dot = _dot()
    assert dot.startswith("digraph G {") and dot.rstrip().endswith("}")
    assert '"H1"' in dot and '"EV-002"' in dot and "verify" in dot and "signal" in dot


def test_quoting_escapes_quotes_and_backslashes():
    assert _q('say "hi"\\') == '"say \\"hi\\"\\\\"'


@pytest.mark.parametrize("scenario", ["A", "B", "C"])
def test_dot_is_valid_graphviz_when_dot_is_installed(scenario):
    try:
        done = subprocess.run(["dot", "-Tsvg"], input=_dot(scenario), text=True, capture_output=True, timeout=20)
    except FileNotFoundError:
        pytest.skip("graphviz is not installed")
    assert done.returncode == 0 and "<svg" in done.stdout
