# test seasonal.fit_trend() using synthetic sources
#
# Generate synthetic waveforms at varying periods, trends and noise
# levels, and repeatedly test to estimate a success rate for
# recovering the original trend. Test for a success rate safely within
# empirical bounds, rather than tightly -- these tests are not meant
# to follow confidence boundaries, just catch blunders (the random
# seed may be changed if you must work around a spot of bad luck).
#
from __future__ import division
import numpy as np
from seasonal import fit_trend
import seasonal.sequences as sequences

AMP = 1.0
CYCLES = 6
PERIODS = [12, 52, 113]
SLOPES = [0.0, 5.0, 10.0]

def setup_function(_):
    np.random.seed(0)

def test_sine_trend():
    """a linear trend with sine wave superimposed"""
    for kind in ["mean", "median", "spline", "line"]:
        for period in PERIODS:
            for slope in SLOPES:
                s = sequences.sine(AMP, period, CYCLES, period // 3)
                trend = np.arange(len(s)) * slope / len(s)
                s += trend
                a = fit_trend(s, kind=kind)
                rmse = np.sqrt(np.mean((a - trend) ** 2))
                assert rmse <= s.std() / 2.0

def test_sine_bend():
    """trend up then down, with sine wave superimposed"""
    for kind in ["mean", "median", "spline"]:
        for period in PERIODS:
            for slope in SLOPES:
                s = sequences.sine(AMP, period, CYCLES, period // 3)
                trend = np.arange(len(s)+1) * slope / len(s)
                trend = np.concatenate((trend[::2], trend[::-2]))[:len(s)]
                s += trend
                a = fit_trend(s, kind=kind)
                rmse = np.sqrt(np.mean((a - trend) ** 2))
                print(kind, period, slope, rmse, s.std())
                assert rmse <= s.std() / 2.0
