"""Project-wide configuration: paths, model hyper-parameters, plotting style."""

from pathlib import Path

# --- paths ------------------------------------------------------------------
PKG_ROOT = Path(__file__).resolve().parent.parent      
DATA_DIR = PKG_ROOT / "data"
RESULTS_DIR = PKG_ROOT / "results"
FIG_DIR = RESULTS_DIR / "figures"
SINGLE_SUBJECT_FIG_DIR = RESULTS_DIR / "single_subject_fits"   # one plot per subject

# All CSVs live in data/ -- both the raw inputs and the model-fit "source-data"
# tables that the fitting scripts write and the figure notebooks read.
TRIALS_CSV = DATA_DIR / "RSG_AllData_V0.csv"            # raw trial-level data
COHORT_CSV = DATA_DIR / "subjectIDs.csv"               # analysed cohort + group

# Model-fit source-data tables (one row per subject, per subject x interval, and
# per interval respectively), consumed by the figure notebooks.
FIG_SUBJECT_LEVEL_CSV = DATA_DIR / "fig_subject_level.csv"        # fit_all_subjects.py
FIG_SUBJECT_INTERVAL_CSV = DATA_DIR / "fig_subject_interval.csv"  # fit_all_subjects.py
FIG_MODEL_SIM_CSV = DATA_DIR / "fig_model_sim.csv"               # fit_pooled.py
SINGLE_SUBJECT_R2_CSV = DATA_DIR / "single_subject_r2.csv"       # plot_single_subject_fits.py

POOLED_PARAMS_PKL = RESULTS_DIR / "pooled_params.pkl"            # fit_pooled.py (pooled fit store)

# --- experiment -------------------------------------------------------------
INTERVALS = [0.4, 0.5, 0.7, 1.1, 1.9]   # sample intervals t_s (seconds)

# --- model / fitting hyper-parameters --------------------------------------
FIT_TYPE = "BLS"
INTEG_STEPS = 1000
INTEG_RANGE = [0.001, 10.0]
INIT_VALUES = [0.3, 0.3, 0.8]           # [w_m, w_r, alpha] default start
# Optimisation bounds: (w_m, w_r, alpha) all strictly positive.
BOUNDS = ((1e-4, None), (1e-4, None), (1e-9, None))
OPT_METHOD = "Nelder-Mead"
SIM_NUM = 20000                         # simulated repeats per unique interval

# Reproducible RNG seed for the forward simulation used in Figure 2.
SIM_SEED = 0
# Seed for the per-subject bootstrap of the group regression line in Figure 2.
BOOTSTRAP_SEED = 0
BOOTSTRAP_N = 1000                      # bootstrap resamples for the Fig 2 regression

# --- group labels & colours -------------------------------------------------
# The raw data / cohort file label groups 'CN' and 'MS'; the paper displays
# them as 'Control' and 'MS'.
GROUP_LABEL = {"CN": "Control", "MS": "MS"}

# Green (control) / orange (MS) scheme matching the published figures.
COLORS = {
    "Control": {"dot": "#a8ddb5", "bar": "#3cb371", "line": "#3cb371"},
    "MS": {"dot": "#fdc888", "bar": "#f58518", "line": "#f58518"},
}
# Flat per-group colours used by the box+swarm publication panels (Fig 2-4).
PUB_COLORS = {"Control": "mediumseagreen", "MS": "darkorange"}
# Shades used for the four age subgroups in Figure 4.
AGE_COLORS = {
    "Young Control": "#d6efdf",
    "Old Control": "#3cb371",
    "Young MS": "#fde3c4",
    "Old MS": "#f58518",
}
MODEL_SIM_COLOR = "#b0b0b0"             # grey model-simulation markers in Fig 2
