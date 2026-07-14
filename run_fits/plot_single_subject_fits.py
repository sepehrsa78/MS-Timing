#!/usr/bin/env python
"""Generate one model-over-data plot per analysed subject.

For every subject in the cohort this draws the per-interval mean +/- SD of the
reproduced times together with the fitted Bayesian-observer model simulation and
the subject's regression line, and saves it to
``results/single_subject_fits/sub_<group>_<ID>.png``.

Reads the fitted parameters from ``results/subject_params.csv`` (run
``fit_all_subjects.py`` first).  Also writes ``single_subject_r2.csv`` with the
per-subject goodness of fit.

Usage:
    python run_fits/plot_single_subject_fits.py
"""

import sys
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # headless: many figures, no display
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import r2_score

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from mstiming import config, data_io, fitting, plotting


def main():
    if not config.SUBJECT_PARAMS_CSV.exists():
        raise FileNotFoundError(
            "Missing results/subject_params.csv -- run: python run_fits/fit_all_subjects.py")

    plotting.setup_style()
    trials = data_io.load_trials()
    params = pd.read_csv(config.SUBJECT_PARAMS_CSV)
    config.SINGLE_SUBJECT_FIG_DIR.mkdir(parents=True, exist_ok=True)

    r2_rows = []
    n = len(params)
    t0 = time.time()
    for k, row in enumerate(params.itertuples(index=False), 1):
        tt = data_io.subject_trials(trials, row.ID)
        mu, sd = data_io.group_means(tt)
        ints, sim_mu, sim_sd = fitting.simulate(
            tt, {"w_m": row.w_m, "w_r": row.w_r, "alpha": row.alpha}, seed=config.SIM_SEED)
        r2 = r2_score(mu.values, sim_mu)
        r2_rows.append({"ID": row.ID, "group": row.group, "r2": r2})

        fig, ax = plt.subplots(figsize=(4.5, 4.5))
        plotting.model_over_data(ax, row.group, mu.index.values, mu.values, sd.values,
                                 sim_mu, sim_sd, row.slope, row.intercept)
        ax.set_title(f"{row.group}  ID {row.ID}\n$w_m$={row.w_m:.2f}  $w_r$={row.w_r:.2f}  "
                     rf"$\alpha$={row.alpha:.2f}  $R^2$={r2:.2f}", fontsize=9)
        fig.tight_layout()
        fig.savefig(config.SINGLE_SUBJECT_FIG_DIR / f"sub_{row.group}_{row.ID}.png",
                    dpi=150, bbox_inches="tight")
        plt.close(fig)
        if k % 25 == 0 or k == n:
            print(f"  {k:3d}/{n}  ({time.time() - t0:.0f}s)", flush=True)

    r2_df = pd.DataFrame(r2_rows)
    r2_df.to_csv(config.RESULTS_DIR / "single_subject_r2.csv", index=False)
    print(f"\nSaved {n} plots to {config.SINGLE_SUBJECT_FIG_DIR}")
    print("median R^2 by group:", r2_df.groupby("group")["r2"].median().round(3).to_dict())


if __name__ == "__main__":
    main()
