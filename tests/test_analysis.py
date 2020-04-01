import pytest

from tuneconfig.analysis import ExperimentAnalysis

import os, sys
sys.path.insert(0, os.path.abspath("tests"))

import conftest


@pytest.fixture(scope="module")
def analysis(experiment):
    num_samples = num_workers = 10
    _ = experiment.run(conftest.exec_func, num_samples, num_workers)
    analysis = ExperimentAnalysis(experiment.logdir)
    analysis.setup()
    return analysis


def test_setup(analysis):
    trials = analysis._trials
    assert isinstance(trials, dict)
    assert all("config" in trial for trial in trials.values())
    assert all("runs" in trial for trial in trials.values())


def test_params(analysis):
    pass


def test_metrics(analysis):
    pass


def test_info(analysis):
    analysis.info()


def test_report_stats(analysis):
    results = analysis.report_stats("data")
    for trial_id, stats in results.items():
        assert trial_id in analysis._trials
