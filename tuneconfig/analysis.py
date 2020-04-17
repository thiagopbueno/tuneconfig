from collections import defaultdict
import json
import os

import pandas as pd

from tuneconfig.experiment import Experiment
from tuneconfig.trial import Trial


class ExperimentAnalysis:
    """ExperimentAnalysis

    """

    RESULT_METRIC_SEPARATOR = ":"
    TRANSFORM_TARGET_SEPARATOR = "/"

    @classmethod
    def split_target(cls, target):
        transform = None
        if cls.TRANSFORM_TARGET_SEPARATOR in target:
            transform, target = target.split(cls.TRANSFORM_TARGET_SEPARATOR)
        result, metric = target.split(cls.RESULT_METRIC_SEPARATOR)
        return result, metric, transform

    @classmethod
    def get_target_stats(cls, target, trial):
        result, metric, transform = cls.split_target(target)

        data = []
        for results in trial.runs.values():
            df = results[result][metric]
            rslt = Trial._transform_metric(df, transform)
            data.append(rslt)

        data = pd.concat(data)
        data = data.groupby(data.index, sort=False).agg(
            ["min", "max", "mean", "std"]
        )

        return data

    def __init__(self, logdir, name=None):
        self.logdir = logdir
        self.name = name

        self._trials = {}
        self._params = defaultdict(set)

    @property
    def params(self):
        return {key: sorted(values) for key, values in self._params.items()}

    @property
    def results(self):
        return sorted(self[0][0])

    @property
    def metrics(self):
        return self[0].metrics

    @property
    def size(self):
        n_trials = len(self)
        total_runs = sum(len(trial) for trial in self._trials.values())
        n_runs_per_trial = total_runs / n_trials
        return (n_trials, n_runs_per_trial)

    def info(self):
        n_trials, runs_per_trial = self.size
        print(f"<{self}>")
        print(f"TrialIndex: {n_trials} trials, {runs_per_trial} runs per trial.")
        print(f"ParamIndex: {len(self.params)} parameters.")
        for param, values in self.params.items():
            print(f"  - {param} = [{', '.join(list(map(str, values)))}]")
        print(f"ResultIndex: {len(self.results)} result files.")
        for result, metrics in self.metrics.items():
            print(f"  - {result}({', '.join(metrics)})")

    def setup(self):
        for dirname, subdirs, filenames in os.walk(self.logdir):
            if Experiment.is_trial_dir(dirname):
                trial = Trial.from_directory(dirname)
                self._trials[dirname] = trial

                for key, value in trial.config.items():
                    self._params[key].add(value)

    def get(self, params_values):
        trials = {}
        for name, trial in self._trials.items():
            if all(pv in name for pv in params_values):
                trials[name] = trial
        return trials

    def __str__(self):
        return f"ExperimentAnalysis(logdir='{self.logdir}', name='{self.name}')"

    def __len__(self):
        return len(self._trials)

    def __getitem__(self, i):
        return list(self._trials.items())[i][1]
