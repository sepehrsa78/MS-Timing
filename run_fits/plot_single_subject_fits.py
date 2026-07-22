#!/usr/bin/env python
"""Generate one model-over-data plot per analysed subject.

For every subject this draws the per-interval mean +/- SD of the reproduced time
(the ``cdfMu``/``cdfSig`` markers) together with the fitted Bayesian-observer
model simulation and the subject's regression line, saved to
``results/single_subject_fits/sub_<group>_<ID>.png``.

Reads the fitted parameters and per-interval statistics from
``data/fig_subject_level.csv`` and ``data/fig_subject_interval.csv`` (run
``fit_all_subjects.py`` first).  Also writes ``data/single_subject_r2.csv`` with
the per-subject goodness of fit (R^2 between the data means and the model means).

Usage:
    python run_fits/plot_single_subject_fits.py
"""

import sys
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # headless: many figures, no display
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import r2_score

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from mstiming import config, data_io, fitting, plotting


def main():
    for pth in (config.FIG_SUBJECT_LEVEL_CSV, config.FIG_SUBJECT_INTERVAL_CSV):
        if not pth.exists():
            raise FileNotFoundError(
                f"Missing {pth.name} -- run: python run_fits/fit_all_subjects.py")

    plotting.setup_style()
    trials = data_io.load_trials()
    level = pd.read_csv(config.FIG_SUBJECT_LEVEL_CSV)
    interval = pd.read_csv(config.FIG_SUBJECT_INTERVAL_CSV)
    config.SINGLE_SUBJECT_FIG_DIR.mkdir(parents=True, exist_ok=True)

    r2_rows = []
    n = len(level)
    t0 = time.time()
    for k, row in enumerate(level.itertuples(index=False), 1):
        blk = interval[interval.ID == row.ID].sort_values("interval")
        ints = blk["interval"].to_numpy(float)
        mu, sd = blk["cdfMu"].to_numpy(float), blk["cdfSig"].to_numpy(float)
        params = {"w_m": row.timeWm_BLS_Mod, "w_r": row.timeWp_BLS_Mod, "alpha": row.timeAlpha_BLS}
        # Simulate from the same IQR-filtered trials the fit used, so the model
        # prior bounds match the fit; align the result back to the plotted intervals.
        tt = data_io.subject_trials(trials, row.ID)
        sim_ints, sim_mu_all, sim_sd_all = fitting.simulate(tt, params, seed=config.SIM_SEED)
        mu_by_int = dict(zip(sim_ints, sim_mu_all))
        sd_by_int = dict(zip(sim_ints, sim_sd_all))
        sim_mu = np.array([mu_by_int.get(i, np.nan) for i in ints])
        sim_sd = np.array([sd_by_int.get(i, np.nan) for i in ints])
        finite = np.isfinite(mu) & np.isfinite(sim_mu)
        r2 = r2_score(mu[finite], sim_mu[finite])
        r2_rows.append({"ID": row.ID, "Group": row.Group, "r2": r2})

        fig, ax = plt.subplots(figsize=(4.5, 4.5))
        plotting.model_over_data(ax, row.Group, ints, mu, sd, sim_mu, sim_sd,
                                 row.cdfReg_slope, row.cdfReg_int)
        ax.set_title(f"{row.Group}  ID {row.ID}\n"
                     rf"$w_m$={row.timeWm_BLS_Mod:.2f}  $w_r$={row.timeWp_BLS_Mod:.2f}  "
                     rf"$\alpha$={row.timeAlpha_BLS:.2f}  $R^2$={r2:.2f}", fontsize=9)
        fig.tight_layout()
        fig.savefig(config.SINGLE_SUBJECT_FIG_DIR / f"sub_{row.Group}_{row.ID}.png",
                    dpi=150, bbox_inches="tight")
        plt.close(fig)
        if k % 25 == 0 or k == n:
            print(f"  {k:3d}/{n}  ({time.time() - t0:.0f}s)", flush=True)

    r2_df = pd.DataFrame(r2_rows)
    r2_df.to_csv(config.SINGLE_SUBJECT_R2_CSV, index=False)
    print(f"\nSaved {n} plots to {config.SINGLE_SUBJECT_FIG_DIR}")
    print("median R^2 by group:", r2_df.groupby("Group")["r2"].median().round(3).to_dict())


if __name__ == "__main__":
    main()
