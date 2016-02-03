seasonal
========
Robustly estimate and remove trend and periodicity in a timeseries.

`Seasonal` can recover sharp trend and period estimates from noisy
timeseries data with only a few periods.  It is intended for
estimating season, trend, and level when initializing structural
timeseries models like Holt-Winters. Input samples are
assumed evenly-spaced from a continuous-time signal with noise but
no anomalies.

In this package, trend removal is in service of isolating and
estimating periodic (non-trend) variation. "trend" is in the sense of
Cleveland's STL decomposition -- a lowpass smoothing of
the data, rather than a single linear trend (though you can opt for
this). Detrending is accomplishd by a coarse fitted spline or a median
filter.

The seasonal estimate will be a list of period-over-period averages at
each seasonal offset. You may specify a period length, or have it
estimated from the data. The latter is an interesting capability of
this package.

See README.md for details on installation, API, theory, and examples.

Dependencies
-------------
package: numpy, scipy
extras:  pandas, matplotlib
