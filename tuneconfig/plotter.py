import os
import json
import re

import matplotlib.pyplot as plt

from tuneconfig.grid import TrialGrid


plt.style.use("seaborn-darkgrid")


class ExperimentPlotter:
    """ExperimentPlotter manages plotting for multiple experiment analyses.

    Args:
        analysis (ExperimentAnalysis): (required) analysis object.
        analyses (List(ExperimentAnalysis)): (optional) list of analysis objects.
    """

    def __init__(self, analysis, *analyses, **kwargs):
        self.analyses = [analysis, *analyses]
        self.grid = TrialGrid(*self.analyses)
        self.kwargs = kwargs

    def plot(self, targets, x_axis=None, y_axis=None, anchors=None, **kwargs):
        fmt_kwargs = self.kwargs.copy()
        fmt_kwargs.update(kwargs)

        aggregate = kwargs.get("aggregate", True)
        trial_grid = self.grid.select(anchors).build(targets, x_axis, y_axis, aggregate)

        nrows, ncols = self.grid.shape
        fig, axes = plt.subplots(
            nrows, ncols,
            squeeze=False,
            figsize=fmt_kwargs.get("figsize"),
            sharex=fmt_kwargs.get("sharex", False),
            sharey=fmt_kwargs.get("sharey", False),
        )

        suptitle = None
        for pos, _, _ in self.grid.traverse():
            commonconfig = pos[-1]
            if not suptitle:
                suptitle = set(commonconfig)
            else:
                suptitle &= set(commonconfig)
        fig.suptitle(", ".join(sorted(suptitle)), fontweight="bold")

        for pos, ids, df in self.grid.traverse():
            j, i, y, x, commonconfig = pos
            analysis_id, trial_id, metric = ids
            ax = axes[j][i]

            xy_values = set()
            if x:
                xy_values.add(x[1])
            if y:
                xy_values.add(y[1])
            ax.set_title(", ".join(sorted(xy_values)), fontweight="bold")

            if j == nrows - 1:
                ax.set_xlabel(
                    fmt_kwargs.get("target_x_axis_label"), fontweight="bold")
            if i == 0:
                ax.set_ylabel(
                    fmt_kwargs.get("target_y_axis_label"), fontweight="bold")

            label, index = self._get_plot_label_idx(x, y, *ids)
            self._plot(ax, df, label, index, **fmt_kwargs)

        return fig

    def _plot(self, ax, df, label, index, **kwargs):
        plot_type = kwargs["plot_type"]
        plot_fn = getattr(self, f"_plot_{plot_type}")
        plot_fn(ax, df, label, index, **kwargs)

    def _plot_line(self, ax, df, label, index, **kwargs):
        mean, std = df["mean"], df["std"]
        lower = mean - std
        upper = mean + std

        xs = range(len(mean))
        ax.plot(xs, mean, label=label)
        ax.fill_between(xs, lower, upper, alpha=0.25)
        ax.set_xscale(kwargs.get("xscale", "linear"))
        ax.set_yscale(kwargs.get("yscale", "linear"))
        ax.grid()
        ax.legend()

    def _plot_bar(self, ax, df, label, index, **kwargs):
        mean, std = df["mean"], df["std"]
        x = index * 0.5
        width = 0.35
        ax.bar([x], mean, width, yerr=std, capsize=10, label=label, alpha=0.45)
        ax.set_xticklabels([])
        ax.legend()

    def _plot_boxplot(self, ax, data, label, index, **kwargs):
        label = label[label.find("@") + 2:]
        ax.boxplot(data, positions=[index], labels=[label],
                   showmeans=True, meanline=True, showfliers=False)
        ax.grid()

    def _get_plot_label_idx(self, x, y, analysis_id, trial_id, metric):
        label = "/".join(filter(None, [analysis_id, trial_id]))
        label = re.sub(r"/{2,}", "/", label)
        label = f"{metric} @ {label}"
        index = self.grid.get(x, y).index(analysis_id, trial_id, metric)
        return label, index

    def plot_chart_from_spec(self, config_path, show_fig=True, filename=None):
        with open(config_path, "r") as file:
            config = json.load(file)
        fig = self.plot(**config)
        if filename:
            fig.savefig(filename)
        if show_fig:
            plt.show()
