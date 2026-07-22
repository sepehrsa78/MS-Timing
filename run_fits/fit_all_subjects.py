#!/usr/bin/env python
"""Fit the Bayesian observer model to every analysed subject.

Writes the two per-subject source-data tables consumed by the figure notebooks:

* ``data/fig_subject_level.csv`` -- one row per subject:
      ID, Group, Age, cdfReg_slope, cdfReg_int,
      timeWm_BLS_Mod, timeWp_BLS_Mod, timeAlpha_BLS
  where ``timeWm_BLS_Mod``/``timeWp_BLS_Mod``/``timeAlpha_BLS`` are the fitted
  (w_m, w_r, alpha) and ``cdfReg_slope``/``cdfReg_int`` are the regression of the
  per-interval mean reproduction on the intervals.

* ``data/fig_subject_interval.csv`` -- one row per subject x interval:
      ID, Group, interval, cdfMu, cdfSig
  the per-interval mean and SD of the reproduced time.

The model fit uses IQR-filtered trials (matches the published parameters); the
behavioural per-interval means/SD and the regression use the raw trials.  Group
and Age come from the cohort file (subjectIDs.csv).

Usage:
    python run_fits/fit_all_subjects.py
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
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)

    level_rows, interval_rows = [], []
    n = len(cohort)
    t0 = time.time()
    for k, sub in enumerate(cohort.itertuples(index=False), 1):
        tt = data_io.subject_trials(trials, sub.ID)                       # IQR-filtered
        tt_raw = data_io.subject_trials(trials, sub.ID, apply_filter=False)
        fit = fitting.fit_observer(tt)
        ints, mu, sd = fitting.per_interval_stats(tt_raw)
        slope, intercept = fitting.interval_regression(ints, mu)

        level_rows.append({
            "ID": sub.ID,
            "Group": sub.group,
            "Age": sub.Age,
            "cdfReg_slope": slope,
            "cdfReg_int": intercept,
            "timeWm_BLS_Mod": fit["w_m"],
            "timeWp_BLS_Mod": fit["w_r"],
            "timeAlpha_BLS": fit["alpha"],
        })
        for itv, m, s in zip(ints, mu, sd):
            interval_rows.append({"ID": sub.ID, "Group": sub.group,
                                  "interval": itv, "cdfMu": m, "cdfSig": s})
        if k % 20 == 0 or k == n:
            print(f"  {k:3d}/{n}  ({time.time() - t0:.0f}s)", flush=True)

    level = pd.DataFrame(level_rows)
    interval = pd.DataFrame(interval_rows)
    level.to_csv(config.FIG_SUBJECT_LEVEL_CSV, index=False)
    interval.to_csv(config.FIG_SUBJECT_INTERVAL_CSV, index=False)
    print(f"\nWrote {config.FIG_SUBJECT_LEVEL_CSV.name}  ({len(level)} subjects)")
    print(f"Wrote {config.FIG_SUBJECT_INTERVAL_CSV.name}  ({len(interval)} rows)")
    print(level.groupby("Group")[["timeWm_BLS_Mod", "timeWp_BLS_Mod",
                                  "timeAlpha_BLS", "cdfReg_slope"]].mean().round(3))


if __name__ == "__main__":
    main()
