"""Statistical comparisons used in the figures.

The decision rule follows the paper: Shapiro-Wilk normality test per group, then
Welch's t-test if both groups are normal, otherwise the Mann-Whitney U test.
For the Figure 4 age-subgroup analysis the six pairwise comparisons are
Benjamini-Hochberg FDR corrected together.
"""

import numpy as np
import pandas as pd
from scipy import stats as st
from statsmodels.stats.multitest import multipletests


def describe(x):
    x = np.asarray(x, float)
    return {"n": int(x.size), "mean": float(np.mean(x)), "sd": float(np.std(x, ddof=1))}


def adaptive_test(a, b, alpha=0.05):
    """Compare samples following the paper's decision rule.

    Shapiro-Wilk per group (only when n >= 3) -> Welch's t-test if both samples
    are normal, else Mann-Whitney U.  Returns ``(p_value, test_name)``.  NaNs are
    dropped from each sample.
    """
    a = pd.Series(a).dropna()
    b = pd.Series(b).dropna()
    pa = st.shapiro(a).pvalue if len(a) >= 3 else 0.0
    pb = st.shapiro(b).pvalue if len(b) >= 3 else 0.0
    if pa > alpha and pb > alpha:
        _, p = st.ttest_ind(a, b, equal_var=False)
        test = "Welch t"
    else:
        _, p = st.mannwhitneyu(a, b, alternative="two-sided")
        test = "Mann-Whitney"
    return float(p), test


def compare_two_groups(a, b, alpha=0.05):
    """``adaptive_test`` plus each sample's descriptive statistics.

    Returns a dict with the chosen test, its p-value and the ``describe`` summary
    of each sample.
    """
    p, test = adaptive_test(a, b, alpha=alpha)
    return {"test": test, "p": p, "a": describe(a), "b": describe(b)}


def fdr_posthoc(samples, pairs, method="fdr_bh"):
    """Post-hoc pairwise comparisons with multiple-comparison correction.

    ``samples`` maps a subgroup name to its values; ``pairs`` is the list of
    (name, name) comparisons.  Each pair is tested with :func:`adaptive_test`
    and the raw p-values are corrected together (Benjamini-Hochberg by default).
    Returns a dict mapping ``"a|b"`` to the adjusted p-value.
    """
    raw = [adaptive_test(samples[a], samples[b])[0] for a, b in pairs]
    _, padj, _, _ = multipletests(raw, method=method)
    return {f"{a}|{b}": float(pv) for (a, b), pv in zip(pairs, padj)}


def cohens_d(a, b):
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    na, nb = a.size, b.size
    sp = np.sqrt(((na - 1) * a.var(ddof=1) + (nb - 1) * b.var(ddof=1)) / (na + nb - 2))
    return float((a.mean() - b.mean()) / sp)
