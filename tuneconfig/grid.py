from collections import defaultdict
import os
import re

from tuneconfig.analysis import ExperimentAnalysis


def _get_trial_id(commonconfig, x, y, trial_name):
    param_values = set(commonconfig) | set([x, y])
    param_values = filter(None, param_values)
    trial_id = trial_name
    for param_value in param_values:
        trial_id = trial_id.replace(param_value, "")
    trial_id = re.sub(r"/{2,}", "/", trial_id)
    if trial_id.startswith("/"):
        trial_id = trial_id[1:]
    if trial_id.endswith("/"):
        trial_id = trial_id[:-1]
    return trial_id


def _get_commonconfig(plots):
    commonconfig = set(filter(None, plots[0][1].split("/")))
    for _, trial_name, _, _ in plots[1:]:
        commonconfig &= set(trial_name.split("/"))
    return sorted(commonconfig)


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
        commonconfig = _get_commonconfig(self.plots)

        idx = 0
        for analysis_logdir, trial_name, trial, metrics in self.plots:
            analysis_id = analysis_logdir.replace(prefix, "")[1:]
            self.analyses.add(analysis_id)

            trial_id = _get_trial_id(commonconfig, self.x, self.y, trial_name)
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
            analysis.logdir: analysis.get(anchors)
            for analysis in self.analyses
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
        for j, y in enumerate(self._grid):
            for i, x in enumerate(self._grid[y]):
                plots = self._grid[y][x]

                prefix = os.path.commonpath([x[0] for x in plots])
                commonconfig = _get_commonconfig(plots)

                for analysis_logdir, trial_name, trial, metrics in plots:
                    analysis_id = analysis_logdir.replace(prefix, "")[1:]
                    trial_id = _get_trial_id(commonconfig, x, y, trial_name)

                    for metric, df in metrics.items():
                        yield (
                            (j, i, y, x, commonconfig),
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
