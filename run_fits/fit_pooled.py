#!/usr/bin/env python
"""Fit the Bayesian observer model to each group's pooled data.

Produces ``results/pooled_params.pkl``: a dict keyed by group code ('CN', 'MS')
holding {'w_m', 'w_r', 'alpha', 'nll', 'n_trials'}.  These pooled fits drive the
grey model-simulation markers in Figure 2A/B.

Usage:
    python scripts/fit_pooled.py
"""

import pickle
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from mstiming import config, data_io, fitting


def main():
    trials = data_io.load_trials()
    cohort = data_io.load_cohort()
    config.RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    pooled = {}
    for group_code in ("CN", "MS"):
        tt = data_io.group_pooled_trials(trials, cohort, group_code)
        t0 = time.time()
        fit = fitting.fit_observer(tt)
        fit["n_trials"] = len(tt)
        pooled[group_code] = fit
        print(f"{group_code}: w_m={fit['w_m']:.4f} w_r={fit['w_r']:.4f} "
              f"alpha={fit['alpha']:.4f}  (n={len(tt)}, {time.time() - t0:.0f}s)", flush=True)

    with open(config.POOLED_PARAMS_PKL, "wb") as f:
        pickle.dump(pooled, f)
    print(f"\nWrote {config.POOLED_PARAMS_PKL}")


if __name__ == "__main__":
    main()
