"""Figure helpers shared by the per-figure notebooks and the diagnostic plots.

``publication_style`` / ``fmt_p`` / ``sig_bar`` / ``box_swarm`` back the paper
panels (Figures 2-4); ``setup_style`` / ``model_over_data`` back the per-subject
model-over-data diagnostics produced by ``run_fits/plot_single_subject_fits.py``.
"""

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from . import config


# --- publication style (Figures 2-4) ---------------------------------------
def publication_style():
    """Apply the manuscript's figure style; return the font family used.

    Uses the manuscript font (Gill Sans) when it is installed, otherwise falls
    back to matplotlib's default so the figures still render everywhere.
    """
    installed = {f.name for f in fm.fontManager.ttflist}
    font = "Gill Sans" if "Gill Sans" in installed else "DejaVu Sans"
    plt.rcParams.update({
        "font.family": font, "font.weight": "semibold",
        "axes.labelweight": "semibold", "axes.titleweight": "semibold",
    })
    sns.set_context("talk")
    sns.set_style("white", {"xtick.bottom": True, "ytick.left": True})
    return font


def fmt_p(p, adj=False):
    """Format a p-value the way the manuscript labels its significance bars."""
    lead = "p-adj" if adj else "p"
    if p < 0.05:
        if round(p, 3) < 0.001:
            return rf"{lead} $<$ 0.001$^{{*}}$"
        return rf"{lead} = {p:.3f}$^{{*}}$"
    return rf"{lead} = {p:.2f}"


def sig_bar(ax, x1, x2, y, p, adj=False, fontsize=30, lw=3, tick_frac=0.02, color="black"):
    """Draw a significance bracket from ``x1`` to ``x2`` at height ``y``.

    The bracket ticks point downward and the label is ``fmt_p(p, adj)``.
    """
    y0, y1 = ax.get_ylim()
    tick = tick_frac * (y1 - y0)
    ax.plot([x1, x1, x2, x2], [y - tick, y, y, y - tick],
            lw=lw, color=color, clip_on=False, solid_capstyle="butt")
    ax.text((x1 + x2) / 2, y, fmt_p(p, adj), ha="center", va="bottom",
            fontsize=fontsize, fontweight="semibold")


def box_swarm(ax, df, value, palette=None, group_col="Group", order=("Control", "MS"),
              size=6, alpha=0.5):
    """Unfilled box plot overlaid on a per-subject swarm, coloured by group.

    This is the panel style shared by Figure 2C/D and Figure 3A/B/C.
    """
    palette = palette or config.PUB_COLORS
    order = list(order)
    sns.swarmplot(data=df, x=group_col, y=value, order=order, hue=group_col,
                  palette=palette, size=size, alpha=alpha, legend=False, ax=ax)
    sns.boxplot(data=df, x=group_col, y=value, order=order, hue=group_col,
                palette=palette, width=0.5, linewidth=2, fliersize=0,
                legend=False, fill=False, ax=ax)
    return ax


# --- per-subject diagnostic (run_fits/plot_single_subject_fits.py) ----------
def setup_style():
    sns.set_theme(style="ticks")
    plt.rcParams.update({
        "axes.linewidth": 2,
        "xtick.major.width": 2,
        "ytick.major.width": 2,
        "font.size": 12,
        "svg.fonttype": "none",
    })


def model_over_data(ax, group, intervals, mu_data, sd_data, mu_model, sd_model,
                    slope, intercept, xylim=(0.3, 2.0), ticks=(0.4, 0.7, 1.1, 1.9)):
    """Reproduced vs presented interval: data markers + grey model simulation.

    ``slope``/``intercept`` draw the subject's regression line; the dashed
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
