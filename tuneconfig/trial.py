from collections import defaultdict

import pandas as pd


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
        return {key: sorted(values) for key, values in self.runs.items()}

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
        for result, df in self.report_stats().items():
            print(f">> Stats for '{result}' :")
            print(df)
            print()

    def report_stats(self):
        stats = defaultdict(lambda: [])

        for run, results in self.runs.items():
            for result, df in results.items():
                stats[result].append(df)

        for result, data in stats.items():
            data = pd.concat(data)
            stats[result] = data.groupby(data.index, sort=False).agg([
                "min", "max", "mean", "std"
            ])

        return stats

    def __str__(self):
        return f"Trial(logdir='{self.logdir}'"

    def __len__(self):
        return len(self.runs)

    def __getitem__(self, i):
        return list(self.runs.items())[i][1]
