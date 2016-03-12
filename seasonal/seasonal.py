# -*- coding: utf-8 -*-
#pylint: disable=too-many-arguments
"""Seasonal adjustment.

Robustly estimate trend and periodicity in a timeseries.

`Seasonal` can recover additive periodic variation from noisy
timeseries data with only a few periods.  It is intended for
estimating seasonal effects when initializing structural timeseries
models like Holt-Winters. Input samples are assumed evenly-spaced from
a continuous-time signal with noise (white or impulsive) but no
longer-term structural anomalies like level shifts.

The seasonal estimate will be a list of period-over-period averages at
each seasonal offset. You may specify a period length, or have it
estimated from the data. The latter is an interesting capability of
this package.

"""
from __future__ import division
import numpy as np
from .trend import fit_trend
from .periodogram import periodogram_peaks

def fit_seasons(data, trend="spline", period=None, min_ev=0.05,
                periodogram_thresh=0.5):
    """Estimate seasonal effects in a series.

    Estimate the major period of the data by testing seasonal
    differences for various period lengths and returning the seasonal
    offsets that best predict out-of-sample variation.

    Parameters
    ----------
    data : ndarray
        Series data. assumes at least 2 periods of data are provided.
    trend : ndarray or string ("median", "spline", "line" or None)
        If ndarray, remove this trend series prior to fitting seasons.
        If string, fit a trend of named type (see fit_trend() for details)
    period : integer or None
        Use the specified period (number of samples), or estimate if None.
        Note that if a specified period does not yield a seasonal effect that
        is better than no seasonal adjustment, None will be returned.
    min_ev : 0..1
        Minimum variance explained by seasonal adjustment.
        reject a seasonal effect if the expected explained variance of the
        specified or estimated period is less than this.
    periodogram_thresh : float (0..1) or None
        As a speedup, restrict attention to a range of periods
        derived from the input signal's periodogram (see periodogram_peaks()).
        If None, test all periods.

    Returns
    -------
    seasons, trend : ndarray or None, ndarray
        seasons: estimated seasonal factor array, or None if no
        periodicity is detected. The array length is the period.
        trend: fitted (or supplied) trend prior to seasonal fit.

    Notes
    -----
    Two steps:

    First, a range of likely periods is estimated via periodogram
    averaging [2]_.  This is an optional, ad-hoc optimization, and
    though it works well for all our tests and examples there are
    surely classes of signal that will fool it.

    Next, a time-domain period estimator chooses the best integer
    period based on cross-validated residual errors [1]_. It also
    tests the strength of the seasonal effect using the R^2 of the
    leave-one-out cross-validation. For the seasonal model used here,
    this is the expected fraction of variance explained by the best
    seasonal estimate.

    References
    ----------
    .. [1] Hastie, Tibshirani, and Friedman, _The Elements of Statistical
           Learning (2nd ed)_, eqn 7.52, Springer, 2009
    .. [2] Welch, P.D. (1967) "The Use of Fast Fourier Transform for the
           Estimation of Power Spectra: A Method Based on Time Averaging Over
           Short, Modified Periodograms", IEEE Transactions on Audio
           Electroacoustics, AU-15, 70–73.

    """
    if trend is None:
        trend = np.zeros(len(data))
    elif not isinstance(trend,  np.ndarray):
        trend = fit_trend(data, kind=trend, period=period)
    else:
        assert isinstance(trend,  np.ndarray)
    data = data - trend
    var = data.var()
    if np.isclose(var, 0.0):
        return (None, trend)
    if period:
        # compute seasonal offsets for given period
        cv_mse, cv_seasons = gcv(data, period)
        fev = 1 - cv_mse / var
        if np.isclose(cv_mse, 0.0) or fev >= min_ev:
            return (cv_seasons, trend)
        else:
            return (None, trend)
    if periodogram_thresh and period is None:
        # find intervals containing best period
        peaks = periodogram_peaks(data, thresh=periodogram_thresh)
        if peaks is None:
            return (None, trend)
        peaks = sorted(peaks)
    else:
        # search everything (XXX parameterize this)
        peaks = [(0, 0, 4, len(data) // 2)]
    cv_mse, cv_seasons = np.inf, []
    period = 0
    for interval in peaks:
        period = max(period, interval[2])
        while period <= interval[3]:
            _mse, _seasons = gcv(data, period)
            if _mse < cv_mse:
                cv_mse, cv_seasons = _mse, _seasons
            period += 1
    if np.isclose(cv_mse, 0.0) or min_ev <= 1 - cv_mse / var:
        return (cv_seasons, trend)
    else:
        return (None, trend)

def adjust_seasons(data, trend="spline", period=None, seasons=None):
    """Seasonally adjust the data.

    Remove seasonal variation (one dominant frequency), while leaving any trend.
    estimate trend and seasonal components if not provided.

    Parameters
    ----------
    data : ndarray
        series values
    trend : ndarray or string ("median", "spline", "line" or None)
        If ndarray, remove this trend series prior to fitting seasons.
        If string, fit a trend of named type (see fit_trend() for details).
        If seasons is provided, the trend parameter is ignored
    period : integer or None
        Use the specified period (number of samples), or estimate if None.
    seasons : ndarray or None
        use these seasonal offsets instead of estimating

    Returns
    -------
    adjusted : ndarray or None
        seasonally adjusted data, or None if no seasonality detected

    """
    if seasons is None:
        seasons, trend = fit_seasons(data, trend=trend, period=period)
    if seasons is not None:
        ncycles = len(data) // len(seasons) + 1
        season_reps = np.tile(seasons, ncycles)
        return data - season_reps[: len(data)]
    else:
        return None

def gcv(data, period):
    """Generalized cross-validation for seasonality.

    Use GCV [1]_ to compute leave-one-out CV error from deseasonalizing
    data using given period choice.
    yhat(x_i) = mean(y) of same-seasoned y's

    Parameters
    ----------
    data : ndarray
        series values (must be of length >= 2 * period)
    period : int
        hypothesized number of samples per period

    Returns
    -------
    cvmse, seasons : float, ndarray
        cvmse is the mean out-of-sample residual^2 after deseasonalizing.
        seasons is a vector of CV-fitted seasonal offsets.

    References
    __________
    .. [1] Hastie, Tibshirani, and Friedman, _The Elements of Statistical
           Learning (2nd ed)_, eqn 7.52, Springer, 2009

    """
    seasons = np.empty(period)
    cycles = np.zeros(period)
    sum_y2 = np.zeros(period)
    sum_y = np.zeros(period)
    idx = 0
    # for each offset (season) into the period, compute
    # period-over-period mean and variance. different seasons may have
    # different numbers of periods if uneven data.
    for yii in data:
        sum_y[idx] += yii
        sum_y2[idx] += yii * yii
        cycles[idx] += 1
        idx = (idx + 1) % period
    seasons = sum_y / cycles # period-over-period means
    sse = sum_y2 - sum_y ** 2 / cycles # period-over-period sse
    # inflate each seasonal residual by gcv's leave-one-out factor
    cv_mse = ((cycles / (cycles - 1.0)) ** 2 * sse).sum() / len(data)
    cv_mse = 0.0 if np.isclose(cv_mse, 0.0) else cv_mse # float precision noise
    return cv_mse, seasons

def rsquared_cv(data, period):
    """estimate the out-of-sample R^2 for the given period

    Parameters
    ----------
    data : ndarray
        series values (must be of length >= 2 * period)
    period : int
        hypothesized number of samples per period

    Returns
    -------
    cvmse : float

    """
    cv_mse, _ = gcv(data, period)
    return 1 - cv_mse / data.var()
