# test trend.adjust_trend() options handling
#
from __future__ import division
import numpy as np
from seasonal import fit_trend
from seasonal.sequences import sine

N = 101
TREND = 1.0
LEVEL = 10.0
DATA = LEVEL + np.arange(N) * TREND
MID = LEVEL + (N - 1) / 2 * TREND
ZEROS = np.zeros(N)

def iszero(a):
    return np.all(np.isclose(a, ZEROS))

def test_zero():
    adjusted = fit_trend(ZEROS + MID, kind="line")
    assert adjusted.mean() == MID

def test_none():
    fitted = fit_trend(DATA, kind=None)
    assert np.isclose(fitted.mean(), MID)

def test_trend_line():
    fitted = fit_trend(DATA, kind="line")
    assert np.isclose(fitted.mean(), MID)
    assert iszero(DATA - fitted)

def test_trend_spline():
    fitted = fit_trend(DATA, kind="spline")
    assert np.isclose(fitted.mean(), MID)
    assert iszero(DATA - fitted)

def test_trend_mean():
    fitted = fit_trend(DATA, kind="mean")
    assert np.isclose(fitted.mean(), MID)
    assert iszero(DATA - fitted)

def test_trend_median():
    # median filter doesn't *quite* cancel a straight line
    fitted = fit_trend(DATA, kind="median")
    assert np.isclose(fitted.mean(), MID)
    assert iszero(DATA - fitted)
