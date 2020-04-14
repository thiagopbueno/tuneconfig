from collections import defaultdict

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
                metrics = {
                    target: ExperimentAnalysis.get_target_stats(target, trial)
                    for target in targets
                }

                x = f"{x_axis}={trial.config.get(x_axis)}" if x_axis else None
                y = f"{y_axis}={trial.config.get(y_axis)}" if y_axis else None
                self._grid[y][x].append((analysis_id, name, trial, metrics))

        return self._grid

    @property
    def shape(self):
        y_values = self._grid.keys()

        x_values = set()
        for values in self._grid.values():
            x_values.update(set(values.keys()))

        return (len(y_values), len(x_values))
