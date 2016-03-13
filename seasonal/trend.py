# -*- coding: utf-8 -*-
"""Trend estimation for timeseries.

Estimate and remove trend in a timeseries.

In this package, trend removal is in service of isolating and
estimating periodic (non-trend) variation. "trend" is in the sense of
Cleveland's STL decomposition -- a lowpass smoothing of
the data that, when removed from the original series, preserves
original seasonal variation.  Detrending is accomplishd by a coarse
fitted spline, mean or median filters, or a fitted line.

Input samples are assumed evenly-spaced from an anomaly-free
continuous-time signal.

"""
from __future__ import division
import numpy as np
from scipy import stats
from scipy.interpolate import LSQUnivariateSpline
from .periodogram import periodogram_peaks

def fit_trend(data, kind="spline", period=None, ptimes=2):
    """Fit a trend for a possibly noisy, periodic timeseries.

    Trend may be modeled by a line, cubic spline, or mean or median
    filtered series.

    Parameters
    ----------
    data : ndarray
        list of observed values
    kind : string ("mean", "median", "line", "spline", None)
        if mean, apply a period-based mean filter
        if median, apply a period-based median filter
        if line, fit a slope to median-filtered data.
        if spline, fit a piecewise cubic spline to the data
        if None, return zeros
    period : number
        seasonal periodicity, for filtering the trend.
        if None, will be estimated.
    ptimes : number
        multiple of period to use as smoothing window size

    Returns
    -------
    trend : ndarray

    """
    if kind is None:
        return np.zeros(len(data)) + np.mean(data)
    if period is None:
        period = guess_trended_period(data)
    window = (int(period * ptimes) // 2) * 2 - 1 # odd window
    if kind == "median":
        filtered = aglet(median_filter(data, window), window)
    elif kind == "mean":
        filtered = aglet(mean_filter(data, window), window)
    elif kind == "line":
        filtered = line_filter(data, window)
    elif kind == "spline":
        nsegs = len(data) // (window * 2) + 1
        filtered = aglet(spline_filter(data, nsegs), window)
    else:
        raise Exception("adjust_trend: unknown filter type {}".format(kind))
    return filtered

def guess_trended_period(data):
    """return a rough estimate of the major period of trendful data.

    Periodogram wants detrended data to score periods reliably. To do
    that, apply a broad median filter based on a reasonable maximum
    period.  Return a weighted average of the plausible periodicities.

    Parameters
    ----------
    data : ndarray
        list of observed values, evenly spaced in time.

    Returns
    -------
    period : int

    """
    max_period = min(len(data) // 3, 512)
    broad = fit_trend(data, kind="median", period=max_period)
    peaks = periodogram_peaks(data - broad)
    if peaks is None:
        return max_period
    periods, scores, _, _ = zip(*peaks)
    period = int(round(np.average(periods, weights=scores)))
    return period

def aglet(src, window, dst=None):
    """straigten the ends of a windowed sequence.

    Replace the window/2 samples at each end of the sequence with
    lines fit to the full window at each end.  This boundary treatment
    for windowed smoothers is better behaved for detrending than
    decreasing window sizes at the ends.

    Parameters
    ----------
    src : ndarray
        list of observed values
    window : int
        odd integer window size (as would be provided to a windowed smoother)
    dst : ndarray
        if provided, write aglets into the boundaries of this array.
        if dst=src, overwrite ends of src in place. If None, allocate result.

    Returns
    -------
    dst : ndarray
        array composed of src's infield values with aglet ends.

    """
    if dst is None:
        dst = np.array(src)
    half = window // 2
    leftslope = stats.theilslopes(src[: window])[0]
    rightslope = stats.theilslopes(src[-window :])[0]
    dst[0:half] = np.arange(-half, 0) * leftslope + src[half]
    dst[-half:] = np.arange(1, half + 1) * rightslope + src[-half - 1]
    return dst

def median_filter(data, window):
    """Apply a median filter to the data.

    This implementation leaves partial windows at the ends untouched

    """
    filtered = np.copy(data)
    for i in range(window // 2, len(data) - window // 2):
        filtered[i] = np.median(data[max(0, i - window // 2) : i + window // 2 + 1])
    return filtered

def mean_filter(data, window):
    """Apply a windowed mean filter to the data.

    This implementation leaves partial windows at the ends untouched

    """
    filtered = np.copy(data)
    cum = np.concatenate(([0], np.cumsum(data)))
    half = window // 2
    filtered[half : -half] = (cum[window:] - cum[:-window]) / window
    return filtered

def line_filter(data, window):
    """fit a line to the data, after filtering"""
    # knock down seasonal variation with a median filter first
    half = window // 2
    coarse = median_filter(data, window)[half : -half] # discard crazy ends
    slope, _, lower, upper = stats.theilslopes(coarse)
    if lower <= 0.0 and upper >= 0.0:
        filtered = np.zeros(len(data)) + np.median(data)
    else:
        intercept = np.median(data) - (len(data) - 1) / 2 * slope
        filtered = slope * np.arange(len(data)) + intercept
    return filtered

def spline_filter(data, nsegs):
    """Detrend a possibly periodic timeseries by fitting a coarse piecewise
       smooth cubic spline

    Parameters
    ----------
    data : ndarray
        list of observed values
    nsegs : number
        number of spline segments

    Returns
    -------
    filtered : ndarray

    """
    index = np.arange(len(data))
    nknots = max(2, nsegs + 1)
    knots = np.linspace(index[0], index[-1], nknots + 2)[1:-2]
    return LSQUnivariateSpline(index, data, knots)(index)
