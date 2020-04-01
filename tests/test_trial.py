import pandas as pd
import pytest


def test_info(trial):
    trial.info()


def test_describe(trial):
    trial.describe()


def test_report_stats(trial):
    stats = trial.report_stats()
    assert isinstance(stats, dict)
    assert all(len(stats) == len(values) for values in trial.metrics.values())

    for result, data in stats.items():
        assert result in trial.results
        assert isinstance(data, pd.DataFrame)
