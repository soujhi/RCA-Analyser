"""Real-data stability check on UCI SECOM. Signals chosen on the first half of the timeline
must still separate failures in the second half, beyond what chance would give.

Get the data once:  mkdir -p data/secom && cd data/secom &&
  curl -O https://archive.ics.uci.edu/ml/machine-learning-databases/secom/secom.data &&
  curl -O https://archive.ics.uci.edu/ml/machine-learning-databases/secom/secom_labels.data
Run:  python -m validation.secom_stability
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd


def load_secom_files(data_path, labels_path):
    """Returns (X float array, fail bool array) sorted by test time."""
    X = pd.read_csv(data_path, sep=r"\s+", header=None, na_values="NaN").to_numpy(float)
    labels = pd.read_csv(labels_path, sep=r"\s+", header=None, names=["label", "date", "time"])
    t = pd.to_datetime(labels["date"].str.strip('"') + " " + labels["time"].str.strip('"'),
                       format="%d/%m/%Y %H:%M:%S")
    order = np.argsort(t.to_numpy())
    return X[order], (labels["label"].to_numpy()[order] == 1)


def smd(X: np.ndarray, fail: np.ndarray) -> np.ndarray:
    """Standardised mean difference between failing and passing rows, per feature."""
    a, b = X[fail], X[~fail]
    with np.errstate(all="ignore"), _quiet():
        d = (np.nanmean(a, 0) - np.nanmean(b, 0)) / np.sqrt((np.nanvar(a, 0) + np.nanvar(b, 0)) / 2)
    return np.nan_to_num(d, nan=0.0, posinf=0.0, neginf=0.0)


class _quiet:
    def __enter__(self):
        import warnings
        self._ctx = warnings.catch_warnings()
        self._ctx.__enter__()
        warnings.simplefilter("ignore")

    def __exit__(self, *exc):
        return self._ctx.__exit__(*exc)


def replication_rate(X, fail, top_k=20, min_effect=0.2, first_labels=None) -> float:
    """Fraction of the top_k first-half signals that keep their sign and size in the second half."""
    half = len(fail) // 2
    labels_first = fail[:half] if first_labels is None else first_labels
    d1, d2 = smd(X[:half], labels_first), smd(X[half:], fail[half:])
    top = np.argsort(-np.abs(d1))[:top_k]
    ok = (np.sign(d2[top]) == np.sign(d1[top])) & (np.abs(d2[top]) >= min_effect)
    return float(ok.mean())


def chance_rate(X, fail, top_k=20, min_effect=0.2, n_perm=200, seed=0) -> float:
    """Same procedure, but the first-half labels are shuffled, so any replication is luck."""
    rng = np.random.default_rng(seed)
    half = len(fail) // 2
    rates = [replication_rate(X, fail, top_k, min_effect, rng.permutation(fail[:half])) for _ in range(n_perm)]
    return float(np.mean(rates))


def run(data_dir: Path) -> dict:
    X, fail = load_secom_files(data_dir / "secom.data", data_dir / "secom_labels.data")
    return {"rows": int(len(fail)), "failures": int(fail.sum()),
            "replication_rate": replication_rate(X, fail), "chance_rate": chance_rate(X, fail)}


if __name__ == "__main__":
    result = run(Path(sys.argv[1] if len(sys.argv) > 1 else "data/secom"))
    print(result)
