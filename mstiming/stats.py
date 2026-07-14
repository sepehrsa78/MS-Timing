"""Statistical comparisons used in the figures.
"""

import numpy as np
from scipy import stats as st


def describe(x):
    x = np.asarray(x, float)
    return {"n": int(x.size), "mean": float(np.mean(x)), "sd": float(np.std(x, ddof=1))}


def compare_two_groups(a, b, alpha=0.05):
    """Compare samples ``a`` and ``b`` following the paper's decision rule.

    Returns a dict with the chosen test, its statistic and p-value, and the
    descriptive stats of each sample.  For Mann-Whitney the U statistic is
    reported for the (a, b) ordering.
    """
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    normal = (st.shapiro(a).pvalue > alpha) and (st.shapiro(b).pvalue > alpha)
    if normal:
        stat, p = st.ttest_ind(a, b)
        test = "t-test"
    else:
        stat, p = st.mannwhitneyu(a, b, alternative="two-sided")
        test = "Mann-Whitney U"
    return {"test": test, "stat": float(stat), "p": float(p),
            "a": describe(a), "b": describe(b), "normal": bool(normal)}


def cohens_d(a, b):
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    na, nb = a.size, b.size
    sp = np.sqrt(((na - 1) * a.var(ddof=1) + (nb - 1) * b.var(ddof=1)) / (na + nb - 2))
    return float((a.mean() - b.mean()) / sp)


def fdr(pvals):
    """Benjamini-Hochberg FDR correction; returns adjusted p-values."""
    p = np.asarray(pvals, float)
    order = np.argsort(p)
    ranked = p[order] * len(p) / (np.arange(len(p)) + 1)
    ranked = np.minimum.accumulate(ranked[::-1])[::-1]
    out = np.empty_like(ranked)
    out[order] = np.clip(ranked, 0, 1)
    return out
