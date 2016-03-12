# test seasonal.fit_seasons() using synthetic sources
#
# Generate de-trended synthetic waveforms at varying periods and
# noise levels. Test for an estimated period safely
# within empirical bounds, rather than tightly -- these tests are not
# meant to follow confidence boundaries, just catch blunders
#
from __future__ import division
import numpy as np
import seasonal # pylint:disable=import-error
import seasonal.sequences as sequences # pylint:disable=import-error

CYCLES = 3
REPEATS = 10
PERIODS = [12, 52, 113]
NOISE = [0.05, 0.1]
EPS = 2

def setup_function(_):
    np.random.seed(0)

def fit_period(s):
    seasons, _ = seasonal.fit_seasons(s, trend=None)
    return None if seasons is None else len(seasons)

def try_zeros(noise=0, reps=1):
    npass = 0
    for _ in range(reps):
        s = sequences.add_noise(np.zeros(1000), noise)
        if fit_period(s) == None:
            npass += 1
    print("try_zeros noise {0} -> {1}%".format(noise, (100 * npass) / reps))
    return npass

def try_aperiodic(n, noise=0, reps=1):
    npass = 0
    for _ in range(reps):
        s = sequences.aperiodic(1.0, n)
        s = sequences.add_noise(s, noise)
        s = s - s.mean()
        if fit_period(s) == None:
            npass += 1
    print("try_aperiod noise {0} -> {1}%".format(noise, (100 * npass) / reps))
    return npass

def try_square_wave(period, noise=0.0, reps=1):
    npass = 0
    s = sequences.square(1.0, 0.30, period, CYCLES, period // 3)
    for _ in range(reps):
        ns = sequences.add_noise(sequences.mix(s, 0, noise), noise)
        p = fit_period(ns)
        if period - EPS <= p and p <= period + EPS:
            npass += 1
    print("try_square noise {0} period {1} -> {2}%".format(
        noise, period, (100 * npass) / reps))
    return npass

def try_sawtooth(period, noise=0.0, reps=1):
    eps = 3 # why is sawtooth so flaky?
    npass = 0
    s = sequences.sawtooth(1.0, period, CYCLES, period // 3)
    for _ in range(reps):
        ns = sequences.add_noise(sequences.mix(s, 0, noise), noise)
        ns = ns - ns.mean()
        p = fit_period(ns)
        if period - eps <= p and p <= period + eps:
            npass += 1
        else:
            print("saw {0} got {1}".format(period, p))
    print("try_sawtooth noise {0} period {1} -> {2}%".format(
        noise, period, (100 * npass) / reps))
    return npass

def try_sine(period, noise=0.0, reps=1):
    npass = 0
    s = sequences.sine(1.0, period, CYCLES, period // 3)
    for _ in range(reps):
        ns = sequences.add_noise(sequences.mix(s, 0, noise), noise)
        ns = ns - ns.mean()
        p = fit_period(ns)
        if period - EPS <= p and p <= period + EPS:
            npass += 1
    print("try_sine noise {0} period {1} -> {2}%".format(
        noise, period, (100 * npass) / reps))
    return npass

def test_zeros():
    for noise in NOISE:
        npass = try_zeros(noise=noise, reps=REPEATS)
        assert npass == REPEATS, \
            "zeros passed {0}/{1} for noise={2}".format(
                npass, REPEATS, noise)

def test_aperiodic():
    for n in [52, 100, 1000]:
        assert try_aperiodic(n), \
            "test_aperiodic failed for n={0}".format(n)

def test_square_wave():
    for period in PERIODS:
        assert try_square_wave(period), \
            "test_square_wave failed for period={0}".format(period)

def test_noisy_square_wave():
    for noise in NOISE:
        for period in PERIODS:
            npass = try_square_wave(period, noise=noise, reps=REPEATS)
            assert npass == REPEATS, \
                "square_wave passed {0}/{1} for period={2}, noise={3}".format(
                    npass, REPEATS, period, noise)

def test_sawtooth():
    for period in PERIODS:
        assert try_sawtooth(period), \
            "test_sawtooth failed for period={0}".format(period)

def test_noisy_sawtooth():
    for noise in NOISE:
        for period in PERIODS:
            npass = try_sawtooth(period, noise=noise, reps=REPEATS)
            assert npass == REPEATS, \
                "sawtooth passed {0}/{1} for period={2}, noise={3}".format(
                    npass, REPEATS, period, noise)

def test_sine():
    for period in PERIODS:
        assert try_sine(period), \
            "test_sine failed for period={0}".format(period)

def test_noisy_sine():
    for noise in NOISE:
        for period in PERIODS:
            npass = try_sine(period, noise=noise, reps=REPEATS)
            assert npass == REPEATS, \
                "sine passed {0}/{1} for period={2}, noise={3}".format(
                    npass, REPEATS, period, noise)

def test_explicit_period():
    period = 200
    s = sequences.sine(1.0, period, CYCLES, period // 3)
    # wrong but plausible
    seasons, _ = seasonal.fit_seasons(s, period=period - 2)
    assert seasons is not None and len(seasons) == period - 2
    # flat out wrong
    seasons, _ = seasonal.fit_seasons(s, period=period // 2)
    assert seasons is None
