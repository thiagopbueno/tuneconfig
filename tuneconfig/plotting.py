from collections import defaultdict
import json

import matplotlib.pyplot as plt

plt.style.use("seaborn-darkgrid")


class ExperimentPlotter:
    def __init__(self, analysis):
        self.analysis = analysis

    def plot(
        self,
        targets,
        anchors=None,
        x_axis=None,
        y_axis=None,
        filename=None,
        show_fig=False,
        **kwargs,
    ):
        if isinstance(self.analysis, list):
            kwargs["analysis_total_num_"] = len(self.analysis)
            for i, exp_analysis in enumerate(self.analysis):
                kwargs["analysis_num_"] = i
                self._plot(exp_analysis, targets, anchors, x_axis, y_axis, **kwargs)
        else:
            self._plot(self.analysis, targets, anchors, x_axis, y_axis, **kwargs)
        # save figure
        if filename:
            self._fig.savefig(filename, format="pdf")

        # show figure
        if show_fig:
            plt.show()

    def _plot(
        self, analysis, targets, anchors=None, x_axis=None, y_axis=None, **kwargs,
    ):
        # filter trials by anchors
        trials = analysis.get(anchors)

        # separate trials in grid
        trial_grid = defaultdict(lambda: defaultdict(list))
        xs, ys = set(), set()
        for name, trial in trials.items():
            # get avg-std stats for each required metric

            # find required result and metrics
            metrics = []
            for target in targets:
                transform = None
                if "/" in target:
                    transform, target = target.split("/")
                result, metric = target.split(":")
                trial_stats = trial.stats(result, transform)
                if transform:
                    target = f"{transform}({target})"

                trial_stats_result = trial_stats[result]
                if metric in trial_stats_result.columns:
                    metrics.append((target, trial_stats_result[metric]))
                else:
                    metrics.append((target, trial_stats_result.loc[metric]))

            x = trial.config.get(x_axis)
            y = trial.config.get(y_axis)
            trial_grid[x][y].append((trial, metrics))
            if x:
                xs.add(x)
            if y:
                ys.add(y)

        # define number of cells for plots
        nrows, ncols = len(ys), len(xs)
        if nrows == ncols == 0:
            ncols = len(targets)
            nrows = 0
        else:
            ncols = ncols if ncols > 0 else len(targets)
            nrows = nrows if nrows > 0 else len(targets)

        # create figure and subplots
        if hasattr(self, "_fig") and hasattr(self, "_axes"):
            fig, axes = self._fig, self._axes
        else:
            figsize = kwargs.get("figsize", (7, 5))
            fig, axes = plt.subplots(
                nrows, ncols, sharex=True, sharey=False, figsize=figsize
            )
            self._fig, self._axes = fig, axes

        plot_type = kwargs["plot_type"]
        plot_fn = getattr(self, f"_plot_{plot_type}")

        # iterate over axes and plot each metric
        kwargs["analysis_name_"] = analysis.name

        for j, x in enumerate(trial_grid):
            for i, y in enumerate(trial_grid[x]):
                trials = trial_grid[x][y]
                metrics = trials[0][1]

                if x_axis and not y_axis:
                    for k, metric in enumerate(metrics):
                        kwargs["axis_"] = (k, j, len(metrics), len(trial_grid))
                        plot_fn(axes[k][j], x, y, x_axis, y_axis, metric, **kwargs)
                elif not x_axis and y_axis:
                    for k, metric in enumerate(metrics):
                        kwargs["axis_"] = (i, k, len(trial_grid[x]), len(metrics))
                        plot_fn(axes[i][k], x, y, x_axis, y_axis, metric, **kwargs)
                elif not x_axis and not y_axis:
                    for k, metric in enumerate(metrics):
                        kwargs["axis_"] = (0, k, 1, len(metrics))
                        plot_fn(axes[k], x, y, x_axis, y_axis, metric, **kwargs)
                else:
                    kwargs["axis_"] = (i, j, len(trial_grid[x]), len(trial_grid))
                    plot_fn(axes[i][j], x, y, x_axis, y_axis, metric, **kwargs)

    def _plot_line(self, ax, x, y, x_axis, y_axis, metric, **kwargs):
        label, df = metric
        mean, std = df["mean"], df["std"]
        lower = mean - std
        upper = mean + std
        xs = range(len(mean))

        if kwargs["analysis_name_"]:
            label = f"{label} ({kwargs['analysis_name_']})"

        ax.plot(xs, mean, label=label)
        ax.fill_between(xs, lower, upper, alpha=0.3)

        title = f"{x_axis}={x}" if x_axis else ""
        title += ", " if x_axis and y_axis else ""
        title += f"{y_axis}={y}" if y_axis else ""
        ax.set_title(title, fontweight="bold")

        i, j, max_i, _ = kwargs["axis_"]
        if i == max_i - 1:
            ax.set_xlabel(kwargs.get("target_x_axis_label"))
        if j == 0:
            ax.set_ylabel(kwargs.get("target_y_axis_label"))

        ax.grid()
        ax.legend()

    def _plot_bar(self, ax, x, y, x_axis, y_axis, metric, **kwargs):
        label, df = metric
        mean, std = df["mean"], df["std"]

        if kwargs["analysis_name_"]:
            label = f"{label} ({kwargs['analysis_name_']})"

        width = 2.0
        i = kwargs.get("analysis_num_", 0)
        n = kwargs.get("analysis_total_num_", 1)
        xs = [i / n * width]

        ax.bar(xs, [mean], width=0.8 * width / n, label=label)
        ax.set_xticks(xs)
        ax.set_xticklabels([])
        if n == 1:
            ax.set_xlim(-width, width)

        title = f"{x_axis}={x}" if x_axis else ""
        title += ", " if x_axis and y_axis else ""
        title += f"{y_axis}={y}" if y_axis else ""
        ax.set_title(title, fontweight="bold")

        i, j, max_i, _ = kwargs["axis_"]
        if i == max_i - 1:
            ax.set_xlabel(kwargs.get("target_x_axis_label"))
        if j == 0:
            ax.set_ylabel(kwargs.get("target_y_axis_label"))

        ax.grid()
        ax.legend()

    def plot_chart_from_spec(self, filepath, **kwargs):
        with open(filepath, "r") as file:
            config_dict = json.load(file)
            config_dict.update(kwargs)

        self.plot(**config_dict)
