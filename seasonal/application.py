# -*- coding: utf-8 -*-
"""Application

commandline functions published as entry points in setup.py

(matplotlib is not a listed package dependency, but is required
 when commands are invoked with the --plot option.)

"""
from __future__ import division
from sys import stderr
import os.path
from optparse import OptionParser
from textwrap import dedent
import numpy as np
import pandas as pd
try:
    import matplotlib
    import matplotlib.pyplot as plt
    matplotlib.style.use('ggplot')
except ImportError:
    plt = None
from .version import __version__
from .seasonal import fit_seasons, adjust_seasons, rsquared_cv
from .trend import fit_trend
from .periodogram import periodogram, periodogram_peaks

def read_csv(path, column=-1, split=None):
    """read an index and value column from a csv file.

    Parameters
    ----------
    path : string
        path to a CSV file
    column : int or string
        column to select. colname (string) or index (integer)
    split : number
        return the leading split*100% of the data (if split <=1.0)
        or N=split points (if split > 1)

    Returns
    -------
    index, data, colname : pandas.tseries.index.DatetimeIndex, ndarray, str

    """
    data = pd.read_csv(path, index_col=0, parse_dates=[0])
    try:
        colidx = int(column)
        if colidx > 0:
            colidx -= 1 # index column not included
        column = data.columns[colidx] # pylint: disable=no-member
    except ValueError:
        pass
    if split is None:
        splitidx = len(data)
    elif split > 1.0:
        splitidx = int(split)
    else:
        splitidx = int(split * len(data))
    return (data.index[:splitidx],
            np.array(data[column][:splitidx], dtype=float),
            column) # pylint: disable=no-member

def seasonal_cmd():
    """commandline seasonal fitting"""

    parser = OptionParser(
        usage="usage: %prog [options] csv-files...",
        description=dedent("""\
        Summarize trend and seasonality in a timeseries to stderr.
        The TEV (trend explained variance) is the in-sample variance removed
        by detrending.
        The EEV (expected explained variance) is the cross-validated
        out-of-sample detrended variance explained by seasonality.
        """),
        version=__version__
    )
    parser.add_option("--column", default=-1,
                      help="csv column to use (name or 0-based index, default rightmost)")
    parser.add_option("--split", type="float", default=None,
                      help=("split data at the split*100%  or int(split) " +
                            "point and use the intial segment"))
    parser.add_option("--trend", default="spline",
                      help="trend function (line, mean, median, spline). Default is spline.")
    parser.add_option("--thresh", type="float", default=0.9,
                      help="Periodogram periods must score above thresh*maxscore (default 0.9)")
    parser.add_option("--minev", type="float", default=0.05,
                      help=dedent("""\
                      reject seasonality if it does not explain this
                      percentage of variance. Default is 0.05"""))
    parser.add_option("--period", type="int",
                      help="seasonally adjust using this period")
    parser.add_option("--csv", action="store_true",
                      help="write adjusted timeseries to stdout as CSV")
    parser.add_option("-p", "--plot", action="store_true",
                      help="display trend and seasonality using matplotlib")
    parser.add_option("--demo", action="store_true",
                      help="demonstrate seasonal with some beer data")
    (options, args) = parser.parse_args()

    if options.demo:
        args = [os.path.join(os.path.dirname(__file__), "data/beer.csv")]
        options.plot = True

    if not args:
        parser.print_help()
        exit(-1)

    if options.plot and not plt:
        stderr.write(
            "Error: matplotlib must be installed to use the --plot option\n")
        exit(-1)

    stderr.write("period\t%TEV\t%EEV\tN\tcycles\tfile\n")
    for csvpath in args:
        index, data, column = read_csv(
            csvpath, column=options.column, split=options.split)
        seasons, trend = fit_seasons(
            data, trend=options.trend, period=options.period,
            periodogram_thresh=options.thresh, min_ev=options.minev)
        detrended = data - trend
        tev = 1.0 - detrended.var() / data.var()
        if seasons is not None:
            deseasoned = adjust_seasons(data, trend=trend, seasons=seasons)
            fev = rsquared_cv(detrended, len(seasons))
        else:
            deseasoned = data.copy()
            fev = 0
        period = len(seasons) if seasons is not None else None
        if period is None:
            stderr.write("0\t0.0\t0.0\t{}\t1\t{}\n".format(len(data), csvpath))
        else:
            stderr.write(
                "{}\t{:.2f}\t{:.2f}\t{}\t{}\t{}\n".format(
                    period, tev*100, fev*100, len(data), len(data) // period,
                    csvpath))

        if options.csv:
            print(pd.DataFrame(
                index=index,
                data={column:data,
                      'trend':trend,
                      'detrended':detrended,
                      'adjusted':deseasoned,
                      'residual':deseasoned - trend}
            ).to_csv())

        if options.plot:
            _seasonal_plot(os.path.basename(csvpath), column, index, data, trend, deseasoned)

def _seasonal_plot(title, column, index, data, trend, deseasoned):\
    #pylint: disable=too-many-arguments
    """display seasonal results using matplotlib"""

    plt.figure(1)
    plt.subplot(411)
    plt.title(title)
    plt.plot(index, data, label=column)
    plt.plot(index, trend, linewidth=3, label="trend")
    plt.plot(index,
             trend + data - deseasoned, ls='-', label="trend+seasonal")
    leg = plt.legend(loc='upper left')
    leg.get_frame().set_alpha(0.5)
    plt.subplot(412)
    plt.title("detrended")
    plt.plot(index, data - trend, label="detrended")
    plt.plot(index, data - deseasoned, ls='-', label="seasonal")
    leg = plt.legend(loc='upper left')
    leg.get_frame().set_alpha(0.5)
    plt.subplot(413)
    plt.title("seasonally adjusted")
    plt.plot(index, deseasoned, label=column)
    plt.subplot(414)
    plt.title("residual (after trend and seasonal)")
    plt.plot(index, deseasoned - trend, label="residual")
    plt.tight_layout()
    plt.show()

def trend_cmd():
    """Fit a trend to data"""

    parser = OptionParser(
        usage="usage: %prog [options] csv-files...",
        description=dedent("""\
        Summarize trend in a timeseries to stderr. The %EV (explained variance)
        is the in-sample variance removed by detrending."""),
        version=__version__
    )
    parser.add_option("--column", default=-1,
                      help="csv column to use (name or 0-based index, default rightmost")
    parser.add_option("-p", "--plot", action="store_true",
                      help="display trend results using matplotlib")
    parser.add_option("--trend", default="spline",
                      help="trending function (line, mean, median, spline). Default is spline")
    parser.add_option("--period", type="int",
                      help=dedent("""\
                      with --trend, adjust trend while preserving variation at
                      this periodicity (default based on data length)"""))
    parser.add_option("--split", type="float", default=None,
                      help=("split data at the split*100%  or int(split) " +
                            "point and use the intial segment"))
    parser.add_option("--csv", action="store_true",
                      help="write adjusted timeseries to stdout as CSV")

    (options, args) = parser.parse_args()
    if not args:
        parser.print_help()
        exit(-1)

    if options.plot and not plt:
        stderr.write(
            "Error: matplotlib must be installed to use the --plot option\n")
        exit(-1)

    stderr.write("%EV\tN\tfile\n")
    for csvpath in args:
        index, data, column = read_csv(
            csvpath, column=options.column, split=options.split)
        trend = fit_trend(data, kind=options.trend, period=options.period)
        detrended = data - trend
        tev = 1.0 - detrended.var() / data.var()
        stderr.write("{:.2f}\t{}\t{}\n".format(tev*100, len(data), csvpath))

        if options.plot:
            _trend_plot(os.path.basename(csvpath), column, data, trend)

        elif options.csv:
            print(pd.DataFrame(
                index=index,
                data={column:data, 'trend':trend, 'adjusted':detrended}
            ).to_csv())

def _trend_plot(title, column, data, trend):
    """display trend results using matplotlib"""

    plt.figure(1)
    plt.subplot(211)
    plt.title(title)
    plt.plot(data, label=column)
    plt.plot(trend, linewidth=3, label="trend")
    leg = plt.legend(loc='upper left')
    leg.get_frame().set_alpha(0.5)
    plt.subplot(212)
    plt.title("detrended")
    plt.plot(data - trend)
    plt.tight_layout()
    plt.show()

def periodogram_cmd():
    """display a periodogram, optionally with detrending

    This is a visualization to help understand how seasonal decides on
    a particular periodicity. It shows the first stage of period
    estimation, resulting in a range of possible periods that are
    considered for later cross-validation. Specifying a detrending
    method can sharpen period estimates for short sequences with
    non-seasonal variation.

    """
    parser = OptionParser(
        usage="usage: %prog [options] csv-files...",
        description="Display a periodogram, optionally detrending first.",
        version=__version__
    )
    parser.add_option("--column", default=-1,
                      help="csv column to use (name or 0-based index, default rightmost)")
    parser.add_option("--thresh", type="float", default=0.9,
                      help="Retain periods scoring above thresh*maxscore (default 0.9)")
    parser.add_option("-p", "--plot", action="store_true",
                      help="display using matplotlib")
    parser.add_option("--trend", default=None,
                      help=dedent("""\
                      trending function (line, mean, median, spline).
                      If specified, perform an initial detrending using this
                      filter"""))
    parser.add_option("--period", type="int",
                      help=dedent("""\
                      with --trend, adjust trend while preserving variation at
                      this periodicity (default based on data length)"""))
    parser.add_option("--split", type="float", default=None,
                      help=dedent("""\
                      split data at the split*100%  or int(split)
                      point and use the intial segment"""))
    (options, args) = parser.parse_args()
    if not args:
        parser.print_help()
        exit(-1)

    if not plt:
        stderr.write("Error: matplotlib must be installed\n")
        exit(-1)

    for csvpath in args:
        _, data, column = read_csv(csvpath, column=options.column, split=options.split)
        if options.trend:
            trend = fit_trend(data, kind=options.trend, period=options.period)
            detrended = data - trend
        else:
            trend = None
            detrended = data
        peaks = periodogram_peaks(detrended, thresh=options.thresh,
                                  max_period=options.period)
        if peaks is None:
            stderr.write("no periodicity detected\n")
        else:
            periods, scores, _, _ = zip(*peaks)
            period = int(round(np.average(periods, weights=scores)))
            print("avg_period:{} N:{} {}".format(period, len(data), csvpath))
            print("period\tpmin\tpmax\tscore")
            for peak in peaks:
                print("{}\t{}\t{}\t{:.3f}".format(peak[0], peak[2], peak[3], peak[1]))
        if options.plot:
            _periodogram_plot(os.path.basename(csvpath), column, data, trend, peaks)

def _periodogram_plot(title, column, data, trend, peaks):
    """display periodogram results using matplotlib"""

    periods, power = periodogram(data)
    plt.figure(1)
    plt.subplot(311)
    plt.title(title)
    plt.plot(data, label=column)
    if trend is not None:
        plt.plot(trend, linewidth=3, label="broad trend")
        plt.legend()
        plt.subplot(312)
        plt.title("detrended")
        plt.plot(data - trend)
    else:
        plt.legend()
        plt.subplot(312)
        plt.title("(no detrending specified)")
    plt.subplot(313)
    plt.title("periodogram")
    plt.stem(periods, power)
    for peak in peaks:
        period, score, pmin, pmax = peak
        plt.axvline(period, linestyle='dashed', linewidth=2)
        plt.axvspan(pmin, pmax, alpha=0.2, color='b')
        plt.annotate("{}".format(period), (period, score * 0.8))
        plt.annotate("{}...{}".format(pmin, pmax), (pmin, score * 0.5))
    plt.tight_layout()
    plt.show()
