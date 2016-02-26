# -*- coding: utf-8 -*-
"""
Seasonal Adjustment
==========================================

Robustly estimate and remove trend and periodicity in a noisy timeseries.

Functions
---------
fit_slope      -- estimate slope of a timeseries
fit_seasons    -- estimate periodicity and seasonal offsets for a timeseries
adjust_trend   -- de-trend a timeseries
adjust_seasons -- de-trend and de-seasonalize a timeseries
periodogram    -- compute a periodogram of the data
periodogram_peaks -- return a list of intervals containg high-scoring periods

Author
------
Will Welch (github@quietplease.com)

"""
from .version import __version__, VERSION
from .trend import fit_trend
from .seasonal import fit_seasons, adjust_seasons, rsquared_cv
from .periodogram import periodogram, periodogram_peaks
