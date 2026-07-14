#!/usr/bin/env python
"""Fit the Bayesian observer model to every analysed subject.

Produces ``results/subject_params.csv`` with, per subject:
    ID, group_code, group, w_m, w_r, alpha, nll, slope, intercept, n_trials

The group label is taken from the cohort file (subjectIDs.csv).  
This CSV is the input consumed by the Figure 3 notebook.

Usage:
    python scripts/fit_all_subjects.py
"""

import sys
import time
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from mstiming import config, data_io, fitting


def main():
    trials = data_io.load_trials()
    cohort = data_io.load_cohort()
    config.RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    rows = []
    n = len(cohort)
    t0 = time.time()
    for k, sub in enumerate(cohort.itertuples(index=False), 1):
        # Model fit uses IQR-filtered trials (matches the published parameters);
        # the behavioural regression slope/intercept use the raw trials, which
        # reproduces the slope/intercept values reported in the paper.
        tt = data_io.subject_trials(trials, sub.ID)
        tt_raw = data_io.subject_trials(trials, sub.ID, apply_filter=False)
        fit = fitting.fit_observer(tt)
        slope, intercept = fitting.linear_metrics(tt_raw)
        rows.append({
            "ID": sub.ID,
            "group_code": sub.group_code,
            "group": sub.group,
            "w_m": fit["w_m"],
            "w_r": fit["w_r"],
            "alpha": fit["alpha"],
            "nll": fit["nll"],
            "slope": slope,
            "intercept": intercept,
            "n_trials": len(tt),
        })
        if k % 20 == 0 or k == n:
            print(f"  {k:3d}/{n}  ({time.time() - t0:.0f}s)", flush=True)

    out = pd.DataFrame(rows)
    out.to_csv(config.SUBJECT_PARAMS_CSV, index=False)
    print(f"\nWrote {config.SUBJECT_PARAMS_CSV}  ({len(out)} subjects)")
    print(out.groupby("group")[["w_m", "w_r", "alpha", "slope"]].mean().round(3))


if __name__ == "__main__":
    main()
