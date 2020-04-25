import multiprocessing as mp
import os
import pytest
import random
import shutil
import sys

import pandas as pd

import tuneconfig
from tuneconfig.experiment import Experiment, ExperimentMode

sys.path.insert(0, os.path.abspath("tests"))
import conftest


@pytest.fixture(scope="function")
def experiment(config_factory):
    logdir = "/tmp/tuneconfig_4"
    experiment = Experiment(config_factory, logdir)
    experiment.start()
    yield experiment
    shutil.rmtree(logdir)


def test_run(experiment):
    num_samples = num_workers = 5

    results = experiment.run(conftest.exec_func, num_samples, num_workers)
    assert len(results) == len(experiment.config_iterator)

    for trial_id, trial_results in results.items():
        assert len(trial_results) == num_samples

        for pname, config, run_dir, run_id in trial_results:
            assert run_dir not in config
            assert os.path.exists(run_dir)


def test_run_in_append_mode(experiment):
    num_samples = num_workers = 5
    n_experiments = 3

    for _ in range(n_experiments):
        results = experiment.run(conftest.exec_func,
                                 num_samples, num_workers,
                                 mode=ExperimentMode.APPEND)
        assert len(results) == len(experiment.config_iterator)

    for config in experiment.config_iterator:
        _, trial_dir = experiment._get_trial(config)
        runs = experiment.get_run_dirs(trial_dir)
        assert len(runs) == num_samples * n_experiments


def test_run_in_skip_mode(experiment):
    num_samples = num_workers = 5

    experiment.run(conftest.exec_func, num_samples, num_workers)
    mtimes1 = {}
    for config in experiment.config_iterator:
        _, trial_dir = experiment._get_trial(config)
        runs = experiment.get_run_dirs(trial_dir)
        mtimes1[trial_dir] = [os.stat(path).st_mtime for path in runs]

    n_experiments = 3
    for _ in range(n_experiments):
        results = experiment.run(
            conftest.exec_func, num_samples, num_workers,
            mode=ExperimentMode.SKIP)
        assert len(results) == 0

        for config in experiment.config_iterator:
            _, trial_dir = experiment._get_trial(config)
            runs = experiment.get_run_dirs(trial_dir)
            assert mtimes1[trial_dir] == [
                os.stat(path).st_mtime for path in runs]

    for config in experiment.config_iterator:
        _, trial_dir = experiment._get_trial(config)
        runs = experiment.get_run_dirs(trial_dir)
        assert len(runs) == num_samples


def test_run_in_overwrite_mode(experiment):
    num_samples = num_workers = 3

    experiment.run(conftest.exec_func, num_samples, num_workers)
    mtimes1 = {}
    for config in experiment.config_iterator:
        _, trial_dir = experiment._get_trial(config)
        runs = experiment.get_run_dirs(trial_dir)
        mtimes1[trial_dir] = [os.stat(path).st_mtime for path in runs]

    experiment.run(
        conftest.exec_func, num_samples, num_workers,
        mode=ExperimentMode.OVERWRITE)

    mtimes2 = {}
    for config in experiment.config_iterator:
        _, trial_dir = experiment._get_trial(config)
        runs = experiment.get_run_dirs(trial_dir)
        mtimes2[trial_dir] = [os.stat(path).st_mtime for path in runs]

    for config in experiment.config_iterator:
        _, trial_dir = experiment._get_trial(config)
        for mtime1, mtime2 in zip(mtimes1[trial_dir], mtimes2[trial_dir]):
            assert mtime1 != mtime2
