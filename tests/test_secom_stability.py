import numpy as np

from validation.secom_stability import chance_rate, replication_rate, smd


def _toy(n=400, features=40, seed=0):
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(n, features))
    fail = rng.random(n) < 0.15
    X[fail, 0] += 1.5      # a real signal that persists across the whole timeline
    X[fail, 1] -= 1.2
    return X, fail


def test_smd_has_the_right_sign_for_a_planted_signal():
    X, fail = _toy()
    d = smd(X, fail)
    assert d[0] > 1.0 and d[1] < -0.8


def test_planted_signals_replicate_far_above_chance():
    X, fail = _toy()
    real = replication_rate(X, fail, top_k=5)
    chance = chance_rate(X, fail, top_k=5, n_perm=50)
    assert real >= 0.4 and real > chance + 0.15


def test_pure_noise_does_not_replicate_beyond_chance():
    rng = np.random.default_rng(1)
    X, fail = rng.normal(size=(400, 40)), rng.random(400) < 0.15
    assert replication_rate(X, fail, top_k=10) <= 0.3
