import os
import re

import matplotlib.pyplot as plt

from tuneconfig.grid import TrialGrid


plt.style.use("seaborn-darkgrid")


class ExperimentPlotter:
    def __init__(self, analysis, *analyses):
        self.analyses = [analysis, *analyses]
        self.grid = TrialGrid(*self.analyses)

    def plot(self, targets, x_axis=None, y_axis=None, anchors=None):
        trial_grid = self.grid.select(anchors).build(targets, x_axis, y_axis)

        nrows, ncols = self.grid.shape
        fig, axes = plt.subplots(nrows, ncols, squeeze=False)
        fig.suptitle(", ".join(anchors))

        for pos, ids, df in self.grid.traverse():
            j, i, y_value, x_value = pos
            analysis_id, trial_id, metric = ids
            ax = axes[j][i]
            self._plot(ax, df, analysis_id, trial_id, metric)

        return fig

    def _plot(self, ax, df, analysis_id, trial_id, metric):
        mean, std = df["mean"], df["std"]
        lower = mean - std
        upper = mean + std

        xs = range(len(mean))
        label = "/".join(filter(None, [analysis_id, trial_id]))
        label = f"{label}::{metric}"

        ax.plot(xs, mean, label=label)
        ax.fill_between(xs, lower, upper, alpha=0.25)
        ax.grid()
        ax.legend()
