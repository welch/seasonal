seasonal
========
Robustly estimate and remove trend and periodicity in a timeseries.

`Seasonal` can recover sharp trend and period estimates from noisy
timeseries data with only a few periods.  It is intended for
estimating season, trend, and level when initializing structural
timeseries models like Holt-Winters. Input samples are
assumed evenly-spaced from a continuous real-valued signal with noise but
no anomalies.

The seasonal estimate will be a list of period-over-period averages at
each seasonal offset. You may specify a period length, or have it
estimated from the data. The latter is an interesting capability of
this package.

Trend removal in this package is in service of isolating and
estimating the periodic (non-trend) variation. A lowpass smoothing of
the data is removed from the original series, preserving original
seasonal variation.  Detrending is accomplishd by a coarse fitted
spline, mean or median filters, or a fitted line.

See https://github.com/welch/seasonal/README.md for details on installation, API, theory, and examples.

Dependencies
-------------
* package: numpy, scipy
* extras:  pandas, matplotlib
