from collections import defaultdict
import os
import re

from tuneconfig.analysis import ExperimentAnalysis


class TrialGridCell:
    def __init__(self, x, y, plots):
        self.x = x
        self.y = y

        self.plots = plots
        self.analyses = set()
        self.trials = set()
        self.metrics = set()

        self._idx = {}
        self._build_idx()

    def _build_idx(self):
        prefix = os.path.commonpath([x[0] for x in self.plots])

        commonconfig = set(filter(None, self.plots[0][1].split("/")))
        for _, trial_name, _, _ in self.plots[1:]:
            config = set(trial_name.split("/"))
            commonconfig &= config
        commonconfig = sorted(commonconfig)

        idx = 0
        for analysis_logdir, trial_name, trial, metrics in self.plots:
            analysis_id = analysis_logdir.replace(prefix, "")[1:]
            self.analyses.add(analysis_id)

            trial_name = set(trial_name.split("/"))
            xy_values = set([self.x, self.y])
            trial_id = trial_name - set(commonconfig) - xy_values
            trial_id = "/".join(sorted(trial_id))

            self.trials.add(trial_id)

            for metric in metrics:
                self.metrics.add(metric)
                self._idx[(analysis_id, trial_id, metric)] = idx
                idx += 1

        self.analyses = sorted(self.analyses)
        self.trials = sorted(self.trials)
        self.metric = sorted(self.metrics)

    def __len__(self):
        return len(self.plots) * len(self.metrics)

    def index(self, analysis_id, trial_id, metric):
        return self._idx[(analysis_id, trial_id, metric)]


class TrialGrid:
    def __init__(self, analysis, *analyses):
        self.analyses = [analysis, *analyses]

        self._cell_idx = {}

    def select(self, anchors):
        self._trials = {
            analysis.logdir: analysis.get(anchors) for analysis in self.analyses
        }
        return self

    def build(self, targets, x_axis=None, y_axis=None):
        self._grid = defaultdict(lambda: defaultdict(list))

        for analysis_id, trials in self._trials.items():
            for name, trial in trials.items():
                name = name.replace(analysis_id, "")

                metrics = {
                    target: ExperimentAnalysis.get_target_stats(target, trial)
                    for target in targets
                }

                x = f"{x_axis}={trial.config.get(x_axis)}" if x_axis else None
                y = f"{y_axis}={trial.config.get(y_axis)}" if y_axis else None
                self._grid[y][x].append((analysis_id, name, trial, metrics))

        self._build_cell_index()

        return self._grid

    def _build_cell_index(self):
        for j, y in enumerate(self._grid):
            for i, x in enumerate(self._grid[y]):
                plots = self._grid[y][x]
                self._cell_idx[(y, x)] = TrialGridCell(x, y, plots)

    def traverse(self):
        for j, y_value in enumerate(self._grid):
            for i, x_value in enumerate(self._grid[y_value]):
                plots = self._grid[y_value][x_value]
                prefix = os.path.commonpath([x[0] for x in plots])

                commonconfig = set(filter(None, plots[0][1].split("/")))
                for _, trial_name, _, _ in plots[1:]:
                    config = set(trial_name.split("/"))
                    commonconfig &= config
                commonconfig = sorted(commonconfig)

                for analysis_logdir, trial_name, trial, metrics in plots:
                    analysis_id = analysis_logdir.replace(prefix, "")[1:]

                    trial_name = set(trial_name.split("/"))
                    xy_values = set([x_value, y_value])
                    trial_id = trial_name - set(commonconfig) - xy_values
                    trial_id = "/".join(sorted(trial_id))

                    for metric, df in metrics.items():
                        yield (
                            (j, i, y_value, x_value, commonconfig),
                            (analysis_id, trial_id, metric),
                            df,
                        )

    def get(self, x, y):
        return self._cell_idx[(y, x)]

    @property
    def shape(self):
        y_values = self._grid.keys()

        x_values = set()
        for values in self._grid.values():
            x_values.update(set(values.keys()))

        return (len(y_values), len(x_values))
