"""Loading and cleaning of the time-reproduction data.

The analysed cohort and the group assignment are defined solely by
``subjectIDs.csv`` (140 controls + 79 MS = 219 subjects after the reliability
exclusion reported in the paper).  The trial-level file contains no group
column, so group membership is always obtained by joining on subject ``ID``.
"""

import numpy as np
import pandas as pd

from . import config


def load_trials(path=None):
    """Return the raw trial-level table (all subjects, unfiltered)."""
    path = path or config.TRIALS_CSV
    return pd.read_csv(path)


def load_cohort(path=None):
    """Return the analysed cohort as a DataFrame with columns ``ID``, ``group``.

    ``group`` uses display labels ('Control', 'MS'); ``group_code`` keeps the raw
    label ('CN', 'MS').  ``Age`` (years) is carried through when present -- it is
    needed for the age-subgroup analysis in Figure 4.
    """
    path = path or config.COHORT_CSV
    cohort = pd.read_csv(path).rename(columns={"SubjectID": "ID", "Group": "group_code"})
    cohort["group"] = cohort["group_code"].map(config.GROUP_LABEL)
    cols = ["ID", "group_code", "group"] + (["Age"] if "Age" in cohort.columns else [])
    return cohort[cols]


def iqr_filter(df, col="RT", k=1.5):
    """Drop rows whose ``col`` value falls outside the 1.5*IQR whiskers."""
    q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
    iqr = q3 - q1
    lo, hi = q1 - k * iqr, q3 + k * iqr
    return df[(df[col] >= lo) & (df[col] <= hi)]


def subject_trials(trials, subject_id, apply_filter=True):
    """IQR-filtered trials for a single subject."""
    tt = trials[trials["ID"] == subject_id]
    return iqr_filter(tt) if apply_filter else tt


def group_pooled_trials(trials, cohort, group_code, apply_filter=True):
    """IQR-filtered trials pooled across all analysed subjects of one group.

    ``group_code`` is the raw label ('CN' or 'MS'); membership comes from the
    cohort file (the trial file has no group column).
    """
    ids = cohort.loc[cohort["group_code"] == group_code, "ID"]
    tt = trials[trials["ID"].isin(ids)]
    return iqr_filter(tt) if apply_filter else tt


def merge_params_with_cohort(params, cohort):
    """Attach the authoritative group label to a per-subject parameter table.

    The parameter table is keyed by ``ID``; the group label always comes from
    the cohort file.  Any pre-existing ``group`` column in ``params`` is dropped.
    """
    params = params.drop(columns=[c for c in ("group", "group_code") if c in params.columns])
    return params.merge(cohort, on="ID", how="inner")
