from collections import defaultdict
import json
import os

import numpy as np
import pandas as pd

from tuneconfig.experiment import Experiment


class Trial:

    def __init__(self, logdir, config, runs):
        self.logdir = logdir
        self.config = config
        self.runs = runs

    @property
    def results(self):
        return sorted(self[0])

    @property
    def metrics(self):
        return {result: sorted(df.columns) for result, df in self[0].items()}

    def info(self):
        print(f"<{self}>")
        print(f"ConfigIndex: {len(self.config)} parameters.")
        for param, value in self.config.items():
            print(f"  - {param} = {value}")
        print(f"RunIndex: {len(self)} runs.")
        print(f"ResultIndex: {len(self.results)} result files.")
        for result, df in self[0].items():
            print(f">> File '{result}' :")
            df.info()

    def describe(self):
        for result, df in self.stats().items():
            print(f">> Stats for '{result}' :")
            print(df)
            print()

    def stats(self, result=None, transform=None):
        stats_ = defaultdict(list)

        for run, results in self.runs.items():
            for filename, df in results.items():
                if result and filename != result:
                    continue
                df = self._transform_metric(df, transform)
                stats_[filename].append(df)

        for filename, data in stats_.items():
            data = pd.concat(data)
            stats_[filename] = data.groupby(data.index, sort=False).agg(
                ["min", "max", "mean", "std"]
            )

        return stats_

    @staticmethod
    def _transform_metric(df, transform):
        if not transform:
            return df
        if not hasattr(df, transform):
            return ValueError(f"Invalid transform function '{transform}'.")
        rslt = getattr(df, transform)()
        if np.isscalar(rslt):
            rslt = pd.Series(rslt)
        return rslt

    @classmethod
    def from_directory(cls, dirname):
        # config
        with open(os.path.join(dirname, "config.json"), "r") as file:
            config = json.load(file)

        # runs
        runs = defaultdict(dict)
        for run_dir in Experiment.get_run_dirs(dirname):
            for path in os.listdir(run_dir):
                basename, extension = os.path.splitext(path)
                if extension == ".csv":
                    filepath = os.path.join(run_dir, path)
                    df = pd.read_csv(filepath)
                    runs[run_dir][basename] = df

        return Trial(dirname, config, runs)

    def __str__(self):
        return f"Trial(logdir={self.logdir})"

    def __len__(self):
        return len(self.runs)

    def __getitem__(self, i):
        return list(self.runs.items())[i][1]
