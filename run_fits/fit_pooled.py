#!/usr/bin/env python
"""Fit the Bayesian observer model to each group's pooled data.

Writes two outputs:

* ``results/pooled_params.pkl`` -- dict keyed by group code ('CN', 'MS') holding
  the pooled fit {'w_m', 'w_r', 'alpha', 'nll', 'n_trials'}.
* ``data/fig_model_sim.csv`` -- one row per interval with columns
  ``interval, CN_mean, CN_std, MS_mean, MS_std``: the mean and SD of the forward
  model simulation under each group's pooled fit (the grey model-simulation
  markers in Figure 2A/B).

Usage:
    python run_fits/fit_pooled.py
"""

import pickle
import sys
import time
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from mstiming import config, data_io, fitting


def main():
    trials = data_io.load_trials()
    cohort = data_io.load_cohort()
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)     # fig_model_sim.csv
    config.RESULTS_DIR.mkdir(parents=True, exist_ok=True)  # pooled_params.pkl

    pooled = {}
    sim_frames = []
    for group_code in ("CN", "MS"):
        tt = data_io.group_pooled_trials(trials, cohort, group_code)
        t0 = time.time()
        fit = fitting.fit_observer(tt)
        fit["n_trials"] = len(tt)
        pooled[group_code] = fit
        # Keep the intervals returned by simulate() so each mean/std stays paired
        # with its own interval label regardless of ordering or missing intervals.
        ints, mean, std = fitting.simulate(tt, fit, seed=config.SIM_SEED)
        sim_frames.append(pd.DataFrame({"interval": ints,
                                        f"{group_code}_mean": mean,
                                        f"{group_code}_std": std}))
        print(f"{group_code}: w_m={fit['w_m']:.4f} w_r={fit['w_r']:.4f} "
              f"alpha={fit['alpha']:.4f}  (n={len(tt)}, {time.time() - t0:.0f}s)", flush=True)

    sim = sim_frames[0].merge(sim_frames[1], on="interval", how="outer").sort_values("interval")
    with open(config.POOLED_PARAMS_PKL, "wb") as f:
        pickle.dump(pooled, f)
    sim.to_csv(config.FIG_MODEL_SIM_CSV, index=False)
    print(f"\nWrote {config.POOLED_PARAMS_PKL.name} and {config.FIG_MODEL_SIM_CSV.name}")


if __name__ == "__main__":
    main()
