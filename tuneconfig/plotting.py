from collections import defaultdict

import matplotlib.pyplot as plt


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
        # filter trials by anchors
        trials = self.analysis.get(anchors)

        # separate trials in grid
        trial_grid = defaultdict(lambda: defaultdict(list))
        xs, ys = set(), set()
        for name, trial in trials.items():
            # get avg-std stats for each required metric
            trial_stats = trial.stats()

            # find required result and metrics
            metrics = []
            for target in targets:
                result, metric = target.split(":")
                metrics.append((target, trial_stats[result][metric]))

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
        figsize = kwargs.get("figsize", (7, 5))
        fig, axes = plt.subplots(
            nrows, ncols, sharex=True, sharey=True, figsize=figsize
        )

        # iterate over axes and plot each metric
        for j, x in enumerate(trial_grid):
            for i, y in enumerate(trial_grid[x]):
                trials = trial_grid[x][y]
                metrics = trials[0][1]

                if x_axis and not y_axis:
                    for k, metric in enumerate(metrics):
                        self._plot(axes[k][j], x, y, x_axis, y_axis, metric, **kwargs)
                elif not x_axis and y_axis:
                    for k, metric in enumerate(metrics):
                        self._plot(axes[i][k], x, y, x_axis, y_axis, metric, **kwargs)
                elif not x_axis and not y_axis:
                    for k, metric in enumerate(metrics):
                        self._plot(axes[k], x, y, x_axis, y_axis, metric, **kwargs)
                else:
                    print(i, j)
                    print(axes[i][j])
                    self._plot(axes[k], x, y, x_axis, y_axis, metric, **kwargs)

        # save figure
        if filename:
            fig.savefig(filename, format="pdf")

        # show figure
        if show_fig:
            plt.show()

    def _plot(self, ax, x, y, x_axis, y_axis, metric, **kwargs):
        label, df = metric
        mean, std = df["mean"], df["std"]
        lower = mean - std
        upper = mean + std
        x = range(len(mean))
        ax.plot(x, mean, label=label)
        ax.fill_between(x, lower, upper, alpha=0.3)

        title = f"{x_axis}={x}" if x_axis else ""
        title += ", " if x_axis else ""
        title += f"{y_axis}={y}" if y_axis else ""
        ax.set_title(title)
        ax.set_xlabel(kwargs.get("target_x_axis_label"))

        ax.grid()
        ax.legend()
