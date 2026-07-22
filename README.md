# Over-Reliance on Prior Expectations in Relapsing-Remitting MS — modelling & figures

Code and data for the Bayesian-observer modelling of the time-reproduction
task and for the paper figures (Figures 2–4) that depend on the model fits.

@Written by Sepehr Sima

## What this project does

A modified three-stage Bayesian observer model is fit (maximum likelihood) to
each participant's time-reproduction data. The model partitions a trial into:

| stage | parameter | meaning |
|-------|-----------|---------|
| measurement  | `w_m`   | sensory measurement (Weber) noise |
| estimation   | `alpha` | multiplicative gain (systematic over/under-estimation) |
| reproduction | `w_r`   | motor (Weber) noise |

The code fits every subject and each group's pooled data, writes the fits out as
plain "source-data" CSVs, then the notebooks turn those CSVs into the figure
panels.

## Layout

```
MS-Timing/
├── mstiming/                 # all library code lives in this one folder
│   ├── bayesian_observer.py  # the three-stage Bayesian observer model
│   ├── config.py             # paths, hyper-parameters, colours
│   ├── data_io.py            # load trials + cohort, IQR filter
│   ├── fitting.py            # fit_observer, per_interval_stats, interval_regression, simulate
│   ├── plotting.py           # figure helpers (publication style, box+swarm, sig bars, model-over-data)
│   └── stats.py              # normality-aware group comparison, FDR post-hoc, Cohen's d
├── run_fits/                 # runnable pipeline scripts
│   ├── fit_pooled.py             # -> data/fig_model_sim.csv, results/pooled_params.pkl
│   ├── fit_all_subjects.py       # -> data/fig_subject_level.csv, data/fig_subject_interval.csv
│   └── plot_single_subject_fits.py  # -> results/single_subject_fits/*.png, data/single_subject_r2.csv
├── notebooks/                # the paper-figure notebooks (read data/*.csv)
│   ├── Figure2.ipynb
│   ├── Figure3.ipynb
│   └── Figure4.ipynb
├── data/                     # ALL csvs: raw inputs + model-fit source-data tables
└── results/                  # non-csv artifacts: figures/, single_subject_fits/, pooled_params.pkl
```

## Data

* **`data/RSG_AllData_V0.csv`** — trial-level data (no group column). Columns
  used: `ID`, `timeInterval` (presented interval `t_s`, sec), `RT` (reproduced
  interval `t_r`, sec).
* **`data/subjectIDs.csv`** — the analysed cohort, group assignment **and age**
  (140 controls + 79 MS = 219 subjects, after the paper's reliability
  exclusion). Columns: `Group` ('CN'/'MS'), `SubjectID`, `Age` (years). This is
  the single source of group labels and ages.

> **Group labels.** Group membership comes from `subjectIDs.csv`; the trial file
> has no group column, so labels are always obtained by joining on subject `ID`.

## Source-data tables (written to `data/` by the fitting scripts, read by the notebooks)

| file | one row per | columns |
|------|-------------|---------|
| `data/fig_subject_level.csv` | subject | `ID`, `Group`, `Age`, `cdfReg_slope`, `cdfReg_int`, `timeWm_BLS_Mod` (=`w_m`), `timeWp_BLS_Mod` (=`w_r`), `timeAlpha_BLS` (=`alpha`) |
| `data/fig_subject_interval.csv` | subject × interval | `ID`, `Group`, `interval`, `cdfMu` (mean reproduction), `cdfSig` (SD, `ddof=0`) |
| `data/fig_model_sim.csv` | interval | `interval`, `CN_mean`, `CN_std`, `MS_mean`, `MS_std` (pooled-fit forward simulation) |
| `data/single_subject_r2.csv` | subject | `ID`, `Group`, `r2` (per-subject goodness of fit) |

`cdfMu`/`cdfSig` are the per-interval mean and SD of the raw reproduced times;
`cdfReg_slope`/`cdfReg_int` are the regression of those five per-interval means
on the intervals (each interval weighted equally). The model fit itself uses the
IQR-filtered trials.

## Setup

```bash
pip install -r requirements.txt
```

## Reproduce

1. **Fit the model** (scripts in `run_fits/`; the CSV outputs go to `data/`):

   ```bash
   python run_fits/fit_pooled.py               # pooled per-group fits  (~2 min)
   python run_fits/fit_all_subjects.py         # per-subject fits       (~10-12 min)
   python run_fits/plot_single_subject_fits.py # one plot per subject   (~1-2 min)
   ```

   `fit_pooled.py` writes `data/fig_model_sim.csv` (model-simulation markers) and
   `results/pooled_params.pkl`. `fit_all_subjects.py` writes the two per-subject
   tables `data/fig_subject_level.csv` and `data/fig_subject_interval.csv`.
   `plot_single_subject_fits.py` saves one model-over-data plot per subject to
   `results/single_subject_fits/` plus `data/single_subject_r2.csv`.

2. **Make the figures** — run the notebooks in `notebooks/` (each is
   self-contained and saves PDF + PNG into `results/figures/`):

   | notebook | reproduces |
   |----------|------------|
   | `Figure2.ipynb` | Fig 2A/B (data + pooled model simulation), 2C/D (slope, intercept) |
   | `Figure3.ipynb` | Fig 3A/B/C (`w_m`, `w_r`, `alpha` by group) |
   | `Figure4.ipynb` | Fig 4A/B (slope, `w_m`) across young/old Control & MS subgroups |

   Run headless with, e.g.:

   ```bash
   jupyter nbconvert --to notebook --execute --inplace notebooks/Figure4.ipynb
   ```

## Notes on reproducibility

* Fitting uses SciPy's Nelder-Mead with default tolerances; per-subject and
  pooled fits reproduce the previously reported parameters to within the
  optimiser tolerance (differences ~1e-4), and the derived `cdf*` behavioural
  columns reproduce to machine precision.
* Group statistics follow the paper: Shapiro-Wilk normality test → Welch's
  t-test if both groups are normal, otherwise Mann-Whitney U. The Figure 4
  age-subgroup comparisons are Benjamini-Hochberg FDR-corrected across the six
  pairwise tests. With this cohort the Figure 3 comparisons reproduce the
  reported values (`w_m` p = 0.008, `w_r` p ≈ 0.69, `alpha` p ≈ 0.80); the
  Figure 2 comparisons are slope p ≈ 0.026, intercept p ≈ 0.071.
* The Figure 2 model simulation (`fig_model_sim.csv`) is stochastic; a fixed
  seed (`config.SIM_SEED`) makes it reproducible. The Figure 2 A/B regression
  line comes from a per-subject bootstrap seeded with `config.BOOTSTRAP_SEED`.
