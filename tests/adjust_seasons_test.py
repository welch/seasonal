# test seasonal.adjust_seasons() options handling
#
# adjust_seasons() handles a variety of optional arguments.
# verify that adjust_trend() correctly calledfor different option combinations.
#
# No noise in this test set.
#
from __future__ import division
import numpy as np
from seasonal import fit_trend, adjust_seasons # pylint:disable=import-error
from seasonal.sequences import sine # pylint:disable=import-error

PERIOD = 25
CYCLES = 4
AMP = 1.0
TREND = AMP / PERIOD
LEVEL = 1000.0
SEASONS = sine(AMP, PERIOD, 1)
DATA = LEVEL + np.arange(PERIOD * CYCLES) * TREND + np.tile(SEASONS, CYCLES)
ZEROS = np.zeros(PERIOD * CYCLES)

def iszero(a):
    return np.all(np.isclose(a, ZEROS))

def isseasons(a):
    return np.all(np.isclose(a, SEASONS))

def test_auto():
    adjusted = adjust_seasons(DATA)
    assert adjusted.std() < DATA.std()

def test_trend_line():
    adjusted = adjust_seasons(DATA, trend="line")
    assert adjusted.std() < DATA.std()

def test_explicit_trend():
    trend = fit_trend(DATA, kind="line")
    adjusted = adjust_seasons(DATA, trend=trend)
    assert adjusted.std() < DATA.std()

def test_trend_period():
    adjusted = adjust_seasons(DATA, trend="line", period=PERIOD)
    assert adjusted.std() < DATA.std()

def test_trend_seasons():
    adjusted = adjust_seasons(DATA, trend="line", seasons=SEASONS)
    assert adjusted.std() < DATA.std()

def test_trend_spline():
    adjusted = adjust_seasons(DATA, trend="spline")
    assert adjusted.std() < DATA.std()

def test_period():
    adjusted = adjust_seasons(DATA, period=PERIOD)
    assert adjusted.std() < DATA.std()
    adjusted = adjust_seasons(DATA, period=PERIOD // 2) # no seasonality
    assert adjusted is None

def test_seasons():
    adjusted = adjust_seasons(DATA, seasons=SEASONS)
    assert adjusted.std() < DATA.std()
