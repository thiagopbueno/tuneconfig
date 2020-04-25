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
        for result, df in self.get_all_stats().items():
            print(f">> Stats for '{result}' :")
            print(df)
            print()

    def get_all_data(self, transform=None):
        return {
            result: self.get_data(result, transform)
            for result in self.results
        }

    def get_data(self, result, transform=None):
        data = []
        for results in self.runs.values():
            df = results[result]
            values = self._transform_metric(df, transform)
            data.append(values)
        return data

    def get_all_stats(self, transform=None):
        stats = defaultdict(pd.DataFrame)
        for results in self.runs.values():
            for result in results:
                result_stats = self.get_stats(result, transform)
                stats[result] = stats[result].append(
                    result_stats, ignore_index=True)
        return stats

    def get_stats(self, result, transform=None):
        data = self.get_data(result, transform)
        df = pd.concat(data)
        df = df.groupby(df.index, sort=False)
        return df.agg(["min", "max", "mean", "std"])

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
