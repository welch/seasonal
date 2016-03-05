#
# holt-winters forecasting
#
# H-W is a structural timeseries model with level, trend, and seasonal
# components that are estimated by exponential smoothing as data
# arrives (https://en.wikipedia.org/wiki/Exponential_smoothing).
# Only the additive seasonality model is implemented.
#
from sys import stderr
from copy import deepcopy
from collections import namedtuple
import numpy as np
from scipy.optimize import fmin_l_bfgs_b
import seasonal

HWState = namedtuple('HWState', 't level trend seasons')
HWParams = namedtuple('HWParams', 'alpha beta gamma')

def estimate_state(data):
    """estimate initial state for Holt Winters

    HWState estimates are for t=-1, the step before y[0].

    Parameters
    ----------
    data : ndarray
        observations

    """
    seasons, trended = seasonal.fit_seasons(data)
    if seasons is None:
        seasons = np.zeros(1)
    trend = trended[1] - trended[0]
    level = trended[0] - trend
    return HWState(-1, level, trend, seasons)

def forecast(state, steps=1):
    """return a single or multi-step forecast from the current state

    Parameters
    ----------
    state : HWState
        current model state
    steps : int
        number of steps out to forecast

    """
    season = state.seasons[(state.t + steps) % len(state.seasons)]
    return state.level + state.trend * steps + season

def advance(y, params, state):
    """incorporate the next observation into the state estimate.

    This returns updated state, using Hyndman's error correction form of H-W [1]
    It mutates state's seasonal array.

    Parameters
    ----------
    y : float
        observed value at time state.t + 1
    params : HWParams
        alpha, beta, gamma params for HW
    state : HWState
        current HW state

    Returns
    -------
    state, err : HWState, float
        state: updated state
        one-step forecast error for y

    References
    ----------
    .. [1] https://www.otexts.org/fpp/7/5, Holt-Winters additive method

    """
    seasons = state.seasons
    e = y - forecast(state)
    level = state.level + state.trend + params.alpha * e
    trend = state.trend + params.alpha * params.beta * e
    seasons[(state.t + 1) % len(state.seasons)] += params.gamma * e
    # in a proper implementation, we would enforce seasons being 0-mean.
    return HWState(state.t+1, level, trend, seasons), e

def estimate_params(data, state, alpha0=0.3, beta0=0.1, gamma0=0.1):
    """Estimate Holt Winters parameters from data

    Parameters
    ----------
    data : ndarray
        observations
    state : HWState
        initial state for HW (one step prior to first data value)
    alpha0, beta0, gamma0 : float, float, float
        initial guess for HW parameters

    Returns
    -------
    params : HWParams

    Notes
    -----
    This is a not a demo about estimating Holt Winters parameters, and
    this is not a great way to go about it, because it does not
    produce good out-of-sample error. In this demo, we unrealistically
    train the HW parameters over all the data, not just the training
    prefix used for the initial seasonal state estimate.

    """
    def _forecast_error(x0, state, data):
        """bfgs HW parameter error callback."""
        E = 0
        state = deepcopy(state)
        params = HWParams(*x0)
        for y in data:
            state, e = advance(y, params, state)
            E += e * e
        return E / len(data)

    alpha, beta, gamma = fmin_l_bfgs_b(
        _forecast_error, x0=[alpha0, beta0, gamma0], bounds=[[0, 1]] * 3,
        args=(state, data), approx_grad=True)[0]
    return HWParams(alpha, beta, gamma)

def hw(data, split=None, params=None):
    """fit a HW model and return the 1-step forecast and smoothed series.

    Parameters
    ----------
    data : array of float
        observations
    split : number
        initialize using the leading split*100% of the data (if split <=1.0)
        or N=split points (if split > 1)

    Returns
    -------
    forecast, smoothed : ndarray, ndarray

    """
    if split is None:
        splitidx = len(data)
    elif split > 1.0:
        splitidx = int(split)
    else:
        splitidx = int(split * len(data))
    state = estimate_state(data[:splitidx])
    print "||seasons|| = {:.3f}".format(np.sqrt(np.sum(state.seasons ** 2)))
    if params is None:
        params = estimate_params(data, state)
        print "estimated alpha={:.3f}, beta={:.3f}, gamma={:.3f}".format(*params)
    level = np.empty(len(data))
    fcast = np.empty(len(data))
    for y in data:
        yhat = forecast(state)
        state, _ = advance(y, params, state)
        level[state.t], fcast[state.t] = state.level, yhat
    print "RMSE = ", np.sqrt(np.sum((fcast - data) ** 2) / len(data))
    print "final ||seasons|| = {:.3f}".format(np.sqrt(np.sum(state.seasons ** 2)))
    return fcast, level

def main():
    import os.path
    from optparse import OptionParser
    from textwrap import dedent
    import matplotlib
    import matplotlib.pyplot as plt
    matplotlib.style.use('ggplot')
    from seasonal.application import read_csv

    parser = OptionParser(
        usage="usage: %prog [options] csv-files...",
        description="Holt-Winters demo using the seasonal package"
    )
    parser.add_option("--column", default=-1,
                      help="csv column to use (name or 0-based index, default rightmost)")
    parser.add_option("--split", type="float", default=None,
                      help=("split data at the split*100%  or int(split) " +
                            "point for initialization"))
    parser.add_option("--params",
                      help=("comma-separated list of alpha, beta, gamma. " +
                            "default is to estimate these from ALL the data"))
    parser.add_option("--demo", action="store_true",
                      help="demonstrate with some air passenger data")
    (options, args) = parser.parse_args()

    if options.demo:
        args = [os.path.join(os.path.dirname(seasonal.__file__),
                             "data/airPassengers.csv")]
        if options.split is None:
            options.split = 0.20

    if not args:
        parser.print_help()
        exit(-1)

    if not plt:
        stderr.write(
            "Error: matplotlib must be installed\n")
        exit(-1)

    if options.params is not None:
        try:
            params = [float(p) for p in options.params.split(',')]
            options.params = HWParams(*params)
        except Exception:
            stderr.write("\nError: --params wants alpha,beta,gamma\n")
            parser.print_help()
            exit(-1)

    for csvpath in args:
        index, data, column = read_csv(csvpath, column=options.column)
        fcast, smoothed = hw(data, options.split, params=options.params)
        plt.figure(1)
        plt.subplot(211)
        plt.title("Holt Winters for "+os.path.basename(csvpath))
        plt.plot(index, data, label=column)
        plt.plot(index, fcast, label="forecast")
        plt.plot(index, smoothed, label="smoothed")
        leg = plt.legend(loc='upper left')
        leg.get_frame().set_alpha(0.5)
        plt.subplot(212)
        plt.title("Forecast Error")
        plt.plot(index, fcast - data)
        plt.show()

if __name__ == "__main__":
    main()
