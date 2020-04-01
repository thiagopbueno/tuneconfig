import pytest

from tuneconfig.trial import Trial


def test_setup(analysis):
    trials = analysis._trials
    assert isinstance(trials, dict)
    assert all(isinstance(trial, Trial) for trial in trials.values())
    assert all(hasattr(trial, "config") for trial in trials.values())
    assert all(hasattr(trial, "runs") for trial in trials.values())


def test_params(analysis):
    print(analysis.params)


def test_metrics(analysis):
    print(analysis.metrics)


def test_info(analysis):
    analysis.info()
