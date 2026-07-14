"""Fit the Bayesian observer model and compute the derived behavioural metrics.

Everything downstream (the figure notebooks) consumes the outputs of these
functions, so the modelling logic lives in exactly one place.
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.optimize import minimize

from . import config
from .bayesian_observer import BayesianObserver


def _observer(trials):
    tS = trials["timeInterval"].to_numpy(float)
    tP = trials["RT"].to_numpy(float)
    return BayesianObserver(tS, tP, tS.min(), tS.max(),
                            config.INTEG_STEPS, config.INTEG_RANGE, config.FIT_TYPE)


def fit_observer(trials, init_values=None, method=None, bounds=None):
    """Maximum-likelihood fit of (w_m, w_r, alpha) to a set of trials.

    Returns a dict with the fitted parameters, the negative log-likelihood at
    the optimum and optimiser diagnostics.
    """
    init_values = np.asarray(config.INIT_VALUES if init_values is None else init_values, float)
    model = _observer(trials)

    def objective(x):
        # A non-finite negative log-likelihood (from a degenerate start) would
        # stall Nelder-Mead at the start point; replace it with a large finite
        # penalty so the optimiser always moves toward the valid region.
        val = model.BayesianModel(x)
        return val if np.isfinite(val) else 1e12

    res = minimize(objective, init_values,
                   bounds=bounds or config.BOUNDS,
                   method=method or config.OPT_METHOD,
                   options={"disp": False})
    return {
        "w_m": res.x[0],
        "w_r": res.x[1],
        "alpha": res.x[2],
        "nll": float(res.fun),
        "success": bool(res.success),
        "n_iter": int(res.get("nit", -1)),
        "n_fev": int(res.get("nfev", -1)),
    }


def multistart_fit(trials, inits):
    """Fit the same trials from several initial values (robustness check).

    ``inits`` is an iterable of [w_m, w_r, alpha] start points.  Returns a
    DataFrame with one row per start.
    """
    rows = []
    for i, x0 in enumerate(inits):
        out = fit_observer(trials, init_values=x0)
        out["start_idx"] = i
        out["init_w_m"], out["init_w_r"], out["init_alpha"] = map(float, x0)
        rows.append(out)
    return pd.DataFrame(rows)


def linear_metrics(trials):
    """Per-subject OLS regression of reproduced (RT) on presented interval.

    Returns (slope, intercept).  Slope < 1 indicates central-tendency bias;
    the reliability exclusion in the paper drops subjects with slope <= 0.
    """
    X = sm.add_constant(trials["timeInterval"].to_numpy(float))
    y = trials["RT"].to_numpy(float)
    b = sm.OLS(y, X).fit().params
    return float(b[1]), float(b[0])


def simulate(trials, params, sim_num=None, seed=None):
    """Forward-simulate reproductions and summarise per interval.

    Returns (intervals, mean, std) where ``std`` is the SD across simulated
    reproductions at each interval (the grey model markers in Fig. 2).

    All trials sharing an interval are identical inputs to the model, so the
    simulation runs on the *unique* intervals with ``sim_num`` repeats each --
    the per-interval mean/SD is a property of the model and converges with
    ``sim_num`` (this avoids a needless multi-GB array on pooled data).
    """
    if seed is not None:
        np.random.seed(seed)
    sim_num = sim_num or config.SIM_NUM
    intervals = np.unique(trials["timeInterval"].to_numpy(float))
    model = BayesianObserver(intervals, intervals, intervals.min(), intervals.max(),
                             config.INTEG_STEPS, config.INTEG_RANGE, config.FIT_TYPE)
    sS, sP = model.BayesSimulation([params["w_m"], params["w_r"], params["alpha"]], sim_num)
    mean = np.array([sP[sS == v].mean() for v in intervals])
    std = np.array([sP[sS == v].std() for v in intervals])
    return intervals, mean, std
