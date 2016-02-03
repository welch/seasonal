# test trend.adjust_trend() options handling
#
import numpy as np
from seasonal import fit_trend
from seasonal.sequences import sine

N = 100
TREND = 1.0
LEVEL = 10.0
DATA = LEVEL + np.arange(N) * TREND
ZEROS = np.zeros(N)

def iszero(a):
    return np.all(np.isclose(a, ZEROS))

def test_none():
    adjusted = DATA - fit_trend(DATA, kind=None)
    assert iszero(DATA - adjusted)

def test_trend_line():
    adjusted = DATA - fit_trend(DATA, kind="line")
    adjusted = adjusted - adjusted.mean()
    assert iszero(adjusted)

def test_trend_spline():
    adjusted = DATA - fit_trend(DATA, kind="spline")
    adjusted = adjusted - adjusted.mean()
    assert iszero(adjusted)

def test_trend_mean():
    adjusted = DATA - fit_trend(DATA, kind="mean")
    adjusted = adjusted - adjusted.mean()
    assert iszero(adjusted)

def test_trend_median():
    # median filter doesn't *quite* cancel a straight line
    adjusted = DATA - fit_trend(DATA, kind="median")
    adjusted = adjusted - adjusted.mean()
    assert iszero(adjusted)
