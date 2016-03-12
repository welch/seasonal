# tests of seasonal.periodogram_mode() using synthetic centered sources
#
# Generate synthetic waveforms at varying periods and test for
# periodogram_mode's ability to estimate an interval containing the
# original period.
#
from __future__ import division
import pytest
import numpy as np
from seasonal import periodogram_peaks
import seasonal.sequences as sequences

PERIODS = [12, 52, 113, 288]
CYCLES = 3

def setup_function(function):
    np.random.seed(0)

def test_zeros():
    assert periodogram_peaks(np.zeros(1000)) == None

def test_square_wave():
    for period in PERIODS:
        s = sequences.impulses(period // 5, period, CYCLES, period // 3)
        p = periodogram_peaks(s, thresh=1.0)
        assert len(p) == 1 and p[0][2] <= period and p[0][3] >= period

def test_sawtooth():
    for period in PERIODS:
        s = sequences.sawtooth(period // 5, period, CYCLES, period // 3)
        p = periodogram_peaks(s, thresh=1.0)
        assert len(p) == 1 and p[0][2] <= period and p[0][3] >= period

def test_sine():
    for period in PERIODS:
        s = sequences.sine(1.0, period, CYCLES, period // 3)
        p = periodogram_peaks(s, thresh=1.0)
        assert len(p) == 1 and p[0][2] <= period and p[0][3] >= period
