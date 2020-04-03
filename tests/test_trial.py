import pandas as pd
import pytest


def test_info(trial):
    trial.info()


def test_describe(trial):
    trial.describe()


def test_stats(trial):
    stats = trial.stats()
    assert isinstance(stats, dict)
    assert len(stats) == len(trial.metrics)

    for result, data in stats.items():
        assert result in trial.results
        assert isinstance(data, pd.DataFrame)
