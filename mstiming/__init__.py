"""Reusable pieces of the MS time-reproduction analysis.

Everything lives in this one package:

    bayesian_observer : the three-stage Bayesian observer model (one class).
    config            : paths, model hyper-parameters, group colours.
    data_io           : load raw trials and the analysed cohort, apply the IQR filter.
    fitting           : fit the model per subject / on pooled data, simulate.
    plotting          : figure helpers (model-over-data, beeswarm, group bars).
    stats             : normality-aware group comparison, Cohen's d, FDR.
"""

from .bayesian_observer import BayesianObserver
from . import config, data_io, fitting, plotting, stats

__all__ = ["BayesianObserver", "config", "data_io", "fitting", "plotting", "stats"]
