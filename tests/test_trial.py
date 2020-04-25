import pandas as pd
import pytest


def test_info(trial):
    trial.info()


def test_describe(trial):
    trial.describe()


def test_get_all_data(trial):
    data = trial.get_all_data()
    assert isinstance(data, dict)
    assert len(data) == len(trial.metrics)

    for result, values in data.items():
        assert result in trial.results
        assert isinstance(values, list)
        assert len(values) == len(trial)
        for value in values:
            assert isinstance(value, pd.DataFrame)


def test_get_all_stats(trial):
    stats = trial.get_all_stats()
    assert isinstance(stats, dict)
    assert len(stats) == len(trial.metrics)

    for result, data in stats.items():
        assert result in trial.results
        assert isinstance(data, pd.DataFrame)
        assert all(col[1] in ["min", "max", "mean", "std"]
                   for col in data.columns)
