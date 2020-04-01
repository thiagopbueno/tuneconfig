from collections import defaultdict
import json
import os

import pandas as pd

from tuneconfig.experiment import Experiment


class ExperimentAnalysis:

    def __init__(self, logdir):
        self.logdir = logdir

        self._trials = {}
        self._params = defaultdict(lambda: set())
        self._results = defaultdict(lambda: set())

    @property
    def params(self):
        return {key: sorted(values) for key, values in self._params.items()}

    @property
    def results(self):
        return sorted(self._results.keys())

    @property
    def metrics(self):
        return {key: sorted(values) for key, values in self._results.items()}

    @property
    def size(self):
        n_trials = len(self._trials)
        total_runs = sum(len(values["runs"]) for values in self._trials.values())
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

    def describe(self):
        pass

    def setup(self):
        for dirname, subdirs, filenames in os.walk(self.logdir):
            if "config.json" in filenames:

                # config
                with open(os.path.join(dirname, "config.json"), "r") as file:
                    config = json.load(file)
                    for key, value in config.items():
                        self._params[key].add(value)

                # runs
                runs = defaultdict(lambda: {})
                for run_dir in filter(Experiment.is_run_dir, subdirs):
                    for path in os.listdir(os.path.join(dirname, run_dir)):
                        basename, extension = os.path.splitext(path)
                        if extension == ".csv":
                            filepath = os.path.join(dirname, run_dir, path)
                            df = pd.read_csv(filepath)
                            self._results[basename].update(set(df.columns))
                            runs[run_dir][basename] = df

                self._trials[dirname] = {
                    "config": config,
                    "runs": runs
                }

    def report_stats(self, metric):
        results = {}

        for trial_id, trial in self._trials.items():
            runs = trial["runs"]

            data = [
                metrics[metric] for metrics in runs.values()
                if metric in metrics
            ]

            if data:
                data = pd.concat(data)
                results[trial_id] = data.groupby(data.index, sort=False).agg([
                    'mean', 'std', 'min', 'max'
                ])

        return results

    def __str__(self):
        return f"ExperimentAnalysis(logdir='{self.logdir}')"

    def __len__(self):
        return len(self._trials)
