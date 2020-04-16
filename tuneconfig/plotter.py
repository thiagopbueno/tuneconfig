import os
import re

import matplotlib.pyplot as plt

from tuneconfig.grid import TrialGrid


plt.style.use("seaborn-darkgrid")


class ExperimentPlotter:
    """ExperimentPlotter manages plotting for multiple experiment analyses.

    Args:
        analysis (ExperimentAnalysis): (required) analysis object.
        analyses (List(ExperimentAnalysis): (optional) list of analysis objects.
    """

    def __init__(self, analysis, *analyses, **kwargs):
        self.analyses = [analysis, *analyses]
        self.grid = TrialGrid(*self.analyses)
        self.kwargs = kwargs

    def plot(self, targets, x_axis=None, y_axis=None, anchors=None):
        trial_grid = self.grid.select(anchors).build(targets, x_axis, y_axis)

        nrows, ncols = self.grid.shape
        fig, axes = plt.subplots(
            nrows, ncols, squeeze=False, figsize=self.kwargs.get("figsize")
        )
        fig.suptitle(", ".join(anchors), fontweight="bold")

        for pos, ids, df in self.grid.traverse():
            j, i, y_value, x_value, commonconfig = pos
            analysis_id, trial_id, metric = ids
            ax = axes[j][i]

            title = set(commonconfig) - set(anchors) - set([x_value, y_value])
            ax.set_title(", ".join(sorted(title)), fontweight="bold")
            if j == nrows - 1:
                ax.set_xlabel(x_value, fontweight="bold")
            if i == 0:
                ax.set_ylabel(y_value, fontweight="bold")

            self._plot(ax, df, analysis_id, trial_id, metric)

        return fig

    def _plot(self, ax, df, analysis_id, trial_id, metric):
        if self.kwargs["plot_type"] == "line":
            self._plot_line(ax, df, analysis_id, trial_id, metric)

    def _plot_line(self, ax, df, analysis_id, trial_id, metric):
        mean, std = df["mean"], df["std"]
        lower = mean - std
        upper = mean + std

        xs = range(len(mean))
        label = "/".join(filter(None, [analysis_id, trial_id]))
        label = re.sub(r"/{2,}", "/", label)
        label = f"{label}::{metric}"

        ax.plot(xs, mean, label=label)
        ax.fill_between(xs, lower, upper, alpha=0.25)
        ax.grid()
        ax.legend()
