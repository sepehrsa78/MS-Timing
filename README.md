# Over-Reliance on Prior Expectations in Relapsing-Remitting MS — modelling & figures
@Written by Sepehr Sima

Code and data for the Bayesian-observer modelling of the time-reproduction
task and for the paper figures that depend on the model fits.

## What this project does

A modified three-stage Bayesian observer model is fit (maximum likelihood) to
each participant's time-reproduction data. The model partitions a trial into:

| stage | parameter | meaning |
|-------|-----------|---------|
| measurement  | `w_m`   | sensory measurement (Weber) noise |
| estimation   | `alpha` | multiplicative gain (systematic over/under-estimation) |
| reproduction | `w_r`   | motor (Weber) noise |

The code fits every subject and each group's pooled data, then reproduces the
figure panels that use those fits.

## Layout

```
publication/
├── mstiming/                 # all library code lives in this one folder
│   ├── bayesian_observer.py  # the three-stage Bayesian observer model
│   ├── config.py             # paths, hyper-parameters, colours
│   ├── data_io.py            # load trials + cohort, IQR filter
│   ├── fitting.py            # fit_observer, multistart_fit, linear_metrics, simulate
│   ├── plotting.py           # figure helpers (beeswarm, model-over-data, bars)
│   └── stats.py              # normality-aware group comparison, Cohen's d, FDR
├── run_fits/                 # runnable pipeline scripts
│   ├── fit_pooled.py             # -> results/pooled_params.pkl
│   ├── fit_all_subjects.py       # -> results/subject_params.csv
│   └── plot_single_subject_fits.py  # -> results/single_subject_fits/*.png
├── notebooks/                # the paper-figure notebooks
│   ├── Figure2.ipynb
│   └── Figure3.ipynb
├── data/                     # RSG_AllData_V0.csv, subjectIDs.csv
└── results/                  # generated parameter tables, pickles, figures/,
                              # single_subject_fits/
```

## Data

* **`data/RSG_AllData_V0.csv`** — trial-level data (no group column). Columns
  used: `ID`, `timeInterval` (presented interval `t_s`, sec), `RT` (reproduced
  interval `t_r`, sec).
* **`data/subjectIDs.csv`** — the analysed cohort **and** the group assignment
  (140 controls + 79 MS = 219 subjects, after the paper's reliability
  exclusion). This is the single source of group labels.

> **Group labels.** Group membership comes from `subjectIDs.csv`;

## Setup

```bash
pip install -r requirements.txt
```

## Reproduce

1. **Fit the model** (scripts in `run_fits/`, all write to `results/`):

   ```bash
   python run_fits/fit_pooled.py               # pooled per-group fits  (~2 min)
   python run_fits/fit_all_subjects.py         # per-subject fits       (~10-12 min)
   python run_fits/plot_single_subject_fits.py # one plot per subject   (~1-2 min)
   ```

   `fit_all_subjects.py` produces `results/subject_params.csv` with
   `ID, group, w_m, w_r, alpha, nll, slope, intercept, n_trials`.
   `plot_single_subject_fits.py` saves one model-over-data plot per subject to
   `results/single_subject_fits/` (plus `single_subject_r2.csv`).

2. **Make the figures** — run the notebooks in `notebooks/` (each is
   self-contained and saves PDF + PNG into `results/figures/`):

   | notebook | reproduces |
   |----------|------------|
   | `Figure2.ipynb` | Fig 2A/B (data + pooled model simulation), 2C/D (slope, intercept) |
   | `Figure3.ipynb`  | Fig 3A/B/C (`w_m`, `w_r`, `alpha` by group) |

   Run headless with, e.g.:

   ```bash
   jupyter nbconvert --to notebook --execute --inplace notebooks/Figure3.ipynb
   ```

## Notes on reproducibility

* Fitting uses SciPy's Nelder-Mead with default tolerances; per-subject fits
  reproduce the original stored parameters exactly, and the pooled fits
  reproduce the stored `pop/*.pkl` values.
* Group statistics follow the paper: Shapiro-Wilk normality test → t-test if
  both groups are normal, otherwise Mann-Whitney U; multiple comparisons are
  FDR-corrected. With this cohort the Figure 3 comparisons reproduce the
  reported values (`w_m` p = 0.008, `w_r` p ≈ 0.68, `alpha` p ≈ 0.80).
* The Figure 2 model simulation is stochastic; a fixed seed (`config.SIM_SEED`)
  makes it reproducible.
