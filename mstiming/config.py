"""Project-wide configuration: paths, model hyper-parameters, plotting style."""

from pathlib import Path

# --- paths ------------------------------------------------------------------
PKG_ROOT = Path(__file__).resolve().parent.parent      
DATA_DIR = PKG_ROOT / "data"
RESULTS_DIR = PKG_ROOT / "results"
FIG_DIR = RESULTS_DIR / "figures"
SINGLE_SUBJECT_FIG_DIR = RESULTS_DIR / "single_subject_fits"   # one plot per subject

TRIALS_CSV = DATA_DIR / "RSG_AllData_V0.csv"            # raw trial-level data
COHORT_CSV = DATA_DIR / "subjectIDs.csv"               # analysed cohort + group

SUBJECT_PARAMS_CSV = RESULTS_DIR / "subject_params.csv"  # produced by fit_all_subjects.py
POOLED_PARAMS_PKL = RESULTS_DIR / "pooled_params.pkl"    # produced by fit_pooled.py

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

# --- group labels & colours -------------------------------------------------
# The raw data / cohort file label groups 'CN' and 'MS'; the paper displays
# them as 'Control' and 'MS'.
GROUP_LABEL = {"CN": "Control", "MS": "MS"}

# Green (control) / orange (MS) scheme matching the published figures.
COLORS = {
    "Control": {"dot": "#a8ddb5", "bar": "#3cb371", "line": "#3cb371"},
    "MS": {"dot": "#fdc888", "bar": "#f58518", "line": "#f58518"},
}
# Shades used for the four age subgroups in Figure 4.
AGE_COLORS = {
    "Young Control": "#d6efdf",
    "Old Control": "#3cb371",
    "Young MS": "#fde3c4",
    "Old MS": "#f58518",
}
MODEL_SIM_COLOR = "#b0b0b0"             # grey model-simulation markers in Fig 2
