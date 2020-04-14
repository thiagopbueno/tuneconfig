from collections import defaultdict
import os
import re

from tuneconfig.analysis import ExperimentAnalysis


class TrialGrid:
    def __init__(self, analysis, *analyses):
        self.analyses = [analysis, *analyses]

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

        return self._grid

    def traverse(self):
        for j, y_value in enumerate(self._grid):
            for i , x_value in enumerate(self._grid[y_value]):
                plots = self._grid[y_value][x_value]
                prefix = os.path.commonpath([x[0] for x in plots])

                commonconfig = set(plots[0][1].split("/"))
                for _, trial_name, _, _ in plots[1:]:
                    config = set(trial_name.split("/"))
                    commonconfig &= config

                params_values = [x_value, y_value]
                params_values.extend(list(commonconfig))
                params_values = sorted(filter(None, params_values))

                for analysis_logdir, trial_name, trial, metrics in plots:
                    analysis_id = analysis_logdir.replace(prefix, "")[1:]

                    for s in params_values:
                        trial_name = trial_name.replace(s, "")
                    trial_id = re.sub(r"/+", "", trial_name)

                    for metric, df in metrics.items():
                        yield (
                            (j, i, y_value, x_value),
                            (analysis_id, trial_id, metric),
                            df
                        )

    @property
    def shape(self):
        y_values = self._grid.keys()

        x_values = set()
        for values in self._grid.values():
            x_values.update(set(values.keys()))

        return (len(y_values), len(x_values))
