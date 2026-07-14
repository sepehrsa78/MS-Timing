"""Bayesian observer model for the time-reproduction task.

The model partitions a single time-reproduction trial into three stages, each
governed by one parameter (Pourmohammadi et al.; Jazayeri & Shadlen, 2010):

    1. Measurement   t_s -> t_m   noisy measurement, scalar noise  w_m
       p(t_m | t_s) = N(t_m ; t_s, (w_m * t_s)^2)

    2. Estimation    t_m -> t_e   Bayes-least-squares (BLS) estimate scaled by a
       multiplicative gain factor ``alpha``:
       t_e = alpha * INT t_s * p(t_m|t_s) dt_s  /  INT p(t_m|t_s) dt_s

    3. Reproduction  t_e -> t_r   noisy motor response, scalar noise  w_r
       p(t_r | t_e) = N(t_r ; t_e, (w_r * t_e)^2)

The full likelihood of a reproduced time given a sample interval marginalises
over the latent measurement t_m:

    p(t_r | t_s, w_m, w_r, alpha) = INT p(t_r | f_BLS(t_m), w_r) p(t_m | t_s, w_m) dt_m

Parameters are fit per subject (or on pooled data) by maximum likelihood.

Notes
-----
* ``fitType`` selects the estimator used in stage 2: ``'BLS'`` (used in the
  paper), ``'MLE'`` or ``'MAP'``.
* In the paper the three parameters are (w_m, w_r, alpha).  Internally the
  second parameter is called ``w_p`` (production noise) for historical reasons;
  it is identical to the paper's w_r.
"""

import numpy as np
from scipy.stats import norm


class BayesianObserver:
    """Three-stage Bayesian observer for interval timing.

    Parameters
    ----------
    xSvec : array-like
        Sample intervals (t_s) for every trial.
    xPvec : array-like
        Reproduced intervals (t_r) for every trial.
    minR, maxR : float
        Bounds of the prior over intervals (min/max presented interval).
    nSteps : int
        Number of quadrature points for the numerical integrals.
    integRange : (float, float)
        Integration range for the latent measurement t_m.
    fitType : {'BLS', 'MLE', 'MAP'}
        Estimator used in the estimation stage.
    """

    def __init__(self, xSvec, xPvec, minR, maxR, nSteps, integRange, fitType):
        self.xSvec = np.asarray(xSvec, dtype=float)
        self.xPvec = np.asarray(xPvec, dtype=float)
        self.minR = minR
        self.maxR = maxR
        self.nSteps = nSteps
        self.integRange = integRange
        self.fitType = fitType

    # --- elementary distributions -------------------------------------------
    def gaussDist(self, x, mu, sigma):
        return norm.pdf(x, mu, sigma)

    def margGaussDist(self, x, mu, sigma):
        return mu * self.gaussDist(x, mu, sigma)

    # --- stage-2 estimators --------------------------------------------------
    def fBLS(self, x_m, w_m, factor):
        """Bayes-least-squares estimate (posterior mean) times the gain factor.

        Where the normalisation integral underflows to exactly zero (measurements
        far outside the prior for small ``w_m``), the estimate is defined as 0
        rather than 0/0 = NaN, keeping the likelihood finite for any parameters.
        """
        d_ts = np.linspace(self.minR, self.maxR, self.nSteps)
        num = np.trapz(self.margGaussDist(x_m[:, np.newaxis], d_ts, w_m * d_ts), d_ts, axis=1)
        denom = np.trapz(self.gaussDist(x_m[:, np.newaxis], d_ts, w_m * d_ts), d_ts, axis=1)
        ratio = np.divide(num, denom, out=np.zeros_like(num), where=denom > 0)
        return factor * ratio

    def fMAP(self, x_m, w_m, factor):
        es = x_m * ((-1 + np.sqrt(1 + 4 * (w_m ** 2))) / (2 * (w_m ** 2)))
        es[es <= self.minR] = self.minR
        es[es >= self.maxR] = self.maxR
        return factor * es

    def fMLE(self, x_m, w_m, factor):
        es = x_m * ((-1 + np.sqrt(1 + 4 * (w_m ** 2))) / (2 * (w_m ** 2)))
        return factor * es

    def mrgGauss(self, x_m, x_s, w_m, x_p, x_e, w_p):
        return self.gaussDist(x_m, x_s, w_m * x_s) * self.gaussDist(x_p, x_e, w_p * x_e)

    # --- likelihood ----------------------------------------------------------
    def BayesianModel(self, initialValues):
        """Negative log-likelihood of the data given parameters.

        ``initialValues`` = [w_m, w_r, alpha].
        """
        d_tm = np.linspace(self.integRange[0], self.integRange[1], self.nSteps)
        # Extreme parameter values (e.g. very small w_m) make the BLS
        # normalisation integral underflow; silence the resulting warnings and
        # let the caller turn a non-finite likelihood into a finite penalty.
        with np.errstate(divide='ignore', invalid='ignore'):
            if self.fitType == 'BLS':
                est = self.fBLS(d_tm, initialValues[0], initialValues[2])
            elif self.fitType == 'MLE':
                est = self.fMLE(d_tm, initialValues[0], initialValues[2])
            else:
                est = self.fMAP(d_tm, initialValues[0], initialValues[2])
            f = self.mrgGauss(d_tm, self.xSvec[:, np.newaxis], initialValues[0],
                              self.xPvec[:, np.newaxis], est, initialValues[1])
            # Grid points where the estimate underflowed lie far outside the
            # prior and carry ~0 probability; drop any non-finite entries so the
            # integral stays finite for any parameter values.
            f = np.nan_to_num(f, nan=0.0, posinf=0.0, neginf=0.0)
            logLike = np.sum(np.log(np.trapz(f, d_tm, axis=1)))
        return -1 * logLike

    # --- forward simulation --------------------------------------------------
    def BayesSimulation(self, initialValues, simNum):
        """Simulate reproduced times under the model.

        Returns (xSvec, xPvec) where each sample interval is repeated ``simNum``
        times and ``xPvec`` holds the simulated reproductions.
        """
        xSvec = self.xSvec.repeat(simNum)
        x_m = norm.rvs(xSvec, xSvec * initialValues[0])
        if self.fitType == 'BLS':
            x_e = self.fBLS(x_m, initialValues[0], initialValues[2])
        elif self.fitType == 'MLE':
            x_e = self.fMLE(x_m, initialValues[0], initialValues[2])
            x_e[x_e < 0] = 0
        else:
            x_e = self.fMAP(x_m, initialValues[0], initialValues[2])
            x_e[x_e <= self.minR] = self.minR
            x_e[x_e >= self.maxR] = self.maxR
        xPvec = norm.rvs(x_e, x_e * initialValues[1])
        return xSvec, xPvec
