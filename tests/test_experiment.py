import multiprocessing as mp
import os
import pytest
import random

import pandas as pd

import tuneconfig
from tuneconfig.experiment import Experiment

import os, sys
sys.path.insert(0, os.path.abspath("tests"))

import conftest


def test_run(experiment):
    num_samples = num_workers = 5
    results = experiment.run(conftest.exec_func, num_samples, num_workers)
    assert len(results) == len(experiment.config_iterator)
    for trial_id, trial_results in results.items():
        assert len(trial_results) == num_samples
        for pname, config, run_dir, run_id in trial_results:
            assert run_dir not in config
            assert os.path.exists(run_dir)


def test_report_mean_std(experiment):
    results = experiment.report_mean_std("data")
    cfg_it = experiment.config_iterator
    assert len(results) == len(cfg_it)
    all_trial_ids = set(cfg_it._trial_id(cfg) for cfg in cfg_it)
    for trial_id, (mean, std) in results.items():
        assert trial_id in all_trial_ids
        assert len(mean) == len(std)
