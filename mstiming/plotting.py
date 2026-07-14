"""Figure helpers shared by the per-figure notebooks.
"""

import warnings

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from . import config


def setup_style():
    sns.set_theme(style="ticks")
    plt.rcParams.update({
        "axes.linewidth": 2,
        "xtick.major.width": 2,
        "ytick.major.width": 2,
        "font.size": 12,
        "svg.fonttype": "none",
    })


def _pval_stars(p):
    return "***" if p < 1e-3 else "**" if p < 1e-2 else "*" if p < 5e-2 else "ns"


def sig_bracket(ax, x1, x2, y, text, lw=1.5, tick=None):
    """Draw a significance bracket from x1 to x2 at height y with a label."""
    tick = (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.02 if tick is None else tick
    ax.plot([x1, x1, x2, x2], [y, y + tick, y + tick, y], lw=lw, c="black")
    ax.text((x1 + x2) / 2, y + tick, text, ha="center", va="bottom")


def beeswarm_mean(ax, df, value, group_col="group", order=("Control", "MS"),
                  ylabel="", ylim=None, yticks=None, pval=None, dot_size=4.5):
    """Beeswarm of ``value`` per group with a horizontal mean bar per group.

    Uses a true swarm layout (points nudged sideways to avoid overlap, forming
    the branch-like structure of the published figures).  A single significance
    bracket with the p-value is drawn if ``pval`` is given.
    """
    order = list(order)
    palette = {g: config.COLORS[g]["dot"] for g in order}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # swarm overlap notice with many points
        sns.swarmplot(data=df, x=group_col, y=value, order=order, hue=group_col,
                      palette=palette, size=dot_size, alpha=0.9, edgecolor="none",
                      legend=False, ax=ax)
    for i, g in enumerate(order):
        m = df.loc[df[group_col] == g, value].mean()
        ax.plot([i - 0.34, i + 0.34], [m, m], lw=7, solid_capstyle="butt",
                color=config.COLORS[g]["bar"], zorder=5)
    ax.set_xlabel("")
    ax.set_ylabel(ylabel)
    if ylim is None:
        # leave head-room for the bracket when the axis is auto-scaled
        ylim = (df[value].min() * 0.9, df[value].max() * 1.18)
    ax.set_ylim(ylim)
    if yticks is not None:
        ax.set_yticks(yticks)
    if pval is not None:
        y0, y1 = ax.get_ylim()
        txt = f"p = {pval:.3f}" + ("*" if pval < 0.05 else "")
        sig_bracket(ax, 0, 1, y1 - (y1 - y0) * 0.10, txt, tick=(y1 - y0) * 0.02)
    sns.despine(ax=ax)
    return ax


def model_over_data(ax, group, intervals, mu_data, sd_data, mu_model, sd_model,
                    slope, intercept, xylim=(0.3, 2.0), ticks=(0.4, 0.7, 1.1, 1.9)):
    """Fig 2A/B: reproduced vs presented interval, data + grey model simulation.

    ``slope``/``intercept`` draw the group's mean regression line; the dashed
    diagonal is the identity line (perfect reproduction).
    """
    col = config.COLORS[group]["line"]
    lo, hi = xylim
    xs = np.array([lo, hi])
    ax.plot(xs, xs, ls="--", color="0.4", lw=1.5, zorder=1)              # identity
    ax.plot(xs, slope * xs + intercept, color=col, lw=2.5, zorder=2,     # regression
            label=f"{'CN' if group=='Control' else 'MS'}: {slope:.2f} X + {intercept:.2f}")
    ax.errorbar(intervals, mu_model, yerr=sd_model, fmt="o", ms=7, color=config.MODEL_SIM_COLOR,
                elinewidth=2, capsize=0, zorder=3, label="Model simulation")
    ax.errorbar(intervals, mu_data, yerr=sd_data, fmt="o", ms=8, color=col,
                elinewidth=2, capsize=0, markeredgecolor="white", zorder=4)
    ax.set_xlim(xylim)
    ax.set_ylim(xylim)
    ax.set_xticks(list(ticks))
    ax.set_yticks(list(ticks))
    ax.set_xlabel("Intervals (sec)")
    ax.set_ylabel("Reproduction (sec)")
    ax.legend(loc="upper left", frameon=False, fontsize=9)
    sns.despine(ax=ax)
    return ax


def group_bars(ax, df, value, order, colors, ylabel="", ylim=None, yticks=None,
               brackets=None):
    """Fig 4: mean +/- SEM bars for age subgroups with optional sig brackets.

    ``brackets`` is a list of (i, j, text) tuples referencing bar positions.
    """
    means = [df.loc[df["subgroup"] == g, value].mean() for g in order]
    sems = [df.loc[df["subgroup"] == g, value].sem() for g in order]
    x = np.arange(len(order))
    ax.bar(x, means, yerr=sems, color=[colors[g] for g in order],
           edgecolor="black", linewidth=1.5, capsize=4, width=0.7)
    ax.set_xticks(x)
    ax.set_xticklabels([g.replace(" ", "\n") for g in order])
    ax.set_ylabel(ylabel)
    if ylim is not None:
        ax.set_ylim(ylim)
    if yticks is not None:
        ax.set_yticks(yticks)
    if brackets:
        top = max(m + s for m, s in zip(means, sems))
        step = top * 0.12
        for k, (i, j, text) in enumerate(brackets):
            sig_bracket(ax, i, j, top + step * (k + 1), text)
        ax.set_ylim(top=top + step * (len(brackets) + 1.5))
    sns.despine(ax=ax)
    return ax
