# -*- coding: utf-8 -*-
"""Frequency estimation via periodograms

"""
from __future__ import division
import numpy as np
import scipy.signal

# by default, assume at least this many cycles of data when
# establishing FFT window sizes.
MIN_FFT_CYCLES = 3.0

# by default, assume periods of no more than this when establishing
# FFT window sizes.
MAX_FFT_PERIOD = 512

def periodogram_peaks(data, min_period=4, max_period=None, thresh=0.90):
    """return a list of intervals containg high-scoring periods

    Use a robust periodogram to estimate ranges containing
    high-scoring periodicities in possibly short, noisy data. Returns
    each peak period along with its adjacent bracketing periods from
    the FFT coefficient sequence.

    Data should be detrended for sharpest results, but trended data
    can be accommodated by lowering thresh (resulting in more
    intervals being returned)

    Parameters
    ----------
    data : ndarray
        Data series, evenly spaced samples.
    min_period : int
        Disregard periods shorter than this number of samples.
        Defaults to 4
    max_period : int
        Disregard periods longer than this number of samples.
        Defaults to the smaller of len(data)/MIN_FFT_CYCLES or MAX_FFT_PERIOD
    thresh : float (0..1)
        Retain periods scoring above thresh*maxscore. Defaults to 0.9

    Returns
    -------
    periods : array of quads, or None
        Array of (period, power, period-, period+), maximizing period
        and its score, and FFT periods bracketing the maximizing
        period, returned in decreasing order of score

    """
    periods, power = periodogram(data, min_period, max_period)
    if np.all(np.isclose(power, 0.0)):
        return None # DC
    result = []
    keep = power.max() * thresh
    while True:
        peak_i = power.argmax()
        if power[peak_i] < keep:
            break
        min_period = periods[min(peak_i + 1, len(periods) - 1)]
        max_period = periods[max(peak_i - 1, 0)]
        result.append([periods[peak_i], power[peak_i], min_period, max_period])
        power[peak_i] = 0
    return result if len(result) else None

def periodogram(data, min_period=4, max_period=None):
    """score periodicities by their spectral power.

    Produce a robust periodogram estimate for each possible periodicity
    of the (possibly noisy) data.

    Parameters
    ----------
    data : ndarray
        Data series, having at least three periods of data.
    min_period : int
        Disregard periods shorter than this number of samples.
        Defaults to 4
    max_period : int
        Disregard periods longer than this number of samples.
        Defaults to the smaller of len(data)/MIN_FFT_CYCLES or MAX_FFT_PERIOD

    Returns
    -------
    periods, power : ndarray, ndarray
        Periods is an array of Fourier periods in descending order,
        beginning with the first one greater than max_period.
        Power is an array of spectral power values for the periods

    Notes
    -----
    This uses Welch's method (no relation) of periodogram
    averaging[1]_, which trades off frequency precision for better
    noise resistance. We don't look for sharp period estimates from
    it, as it uses the FFT, which evaluates at periods N, N/2, N/3, ...,
    so that longer periods are sparsely sampled.

    References
    ----------
    .. [1]: https://en.wikipedia.org/wiki/Welch%27s_method

    """
    if max_period is None:
        max_period = int(min(len(data) / MIN_FFT_CYCLES, MAX_FFT_PERIOD))
    nperseg = min(max_period * 2, len(data) // 2) # FFT window
    freqs, power = scipy.signal.welch(
        data, 1.0, scaling='spectrum', nperseg=nperseg)
    periods = np.array([int(round(1.0 / freq)) for freq in freqs[1:]])
    power = power[1:]
    # take the max among frequencies having the same integer part
    idx = 1
    while idx < len(periods):
        if periods[idx] == periods[idx - 1]:
            power[idx-1] = max(power[idx-1], power[idx])
            periods, power = np.delete(periods, idx), np.delete(power, idx)
        else:
            idx += 1
    power[periods == nperseg] = 0 # disregard the artifact at nperseg
    min_i = len(periods[periods >= max_period]) - 1
    max_i = len(periods[periods < min_period])
    periods, power = periods[min_i : -max_i], power[min_i : -max_i]
    return periods, power
