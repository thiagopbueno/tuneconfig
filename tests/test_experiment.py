import multiprocessing as mp
import os
import pytest
import random

import pandas as pd

import tuneconfig
from tuneconfig.experiment import Experiment


def exec_func(config):
    logdir = config["logdir"]
    run_id = logdir.split("/")[-1]
    del config["logdir"]
    os.makedirs(logdir)

    df = pd.DataFrame({
        "foo": pd.Series([random.gauss(10.0, 1.0) for _ in range(10)]),
        "baz": pd.Series([random.gauss(20.0, 2.0) for _ in range(10)]),
        "bar": pd.Series([random.gauss(30.0, 3.0) for _ in range(10)]),
    })
    filepath = os.path.join(logdir, "data.csv")
    df.to_csv(filepath, index=False)

    return (mp.current_process().pid, config, logdir, run_id)


@pytest.fixture(scope="module")
def config_iterator():
    return tuneconfig.TuneConfig({
        "batch_size": tuneconfig.grid_search([32, 64, 128]),
        "horizon": 40,
        "learning_rate": tuneconfig.grid_search([0.01, 0.1]),
        "epochs": 1000,
        "optimizer": tuneconfig.grid_search(["Adam", "RMSProp", "GradientDescent"]),
        "num_samples": 10
    })


@pytest.fixture(scope="module")
def experiment(config_iterator):
    logdir = "/tmp/tuneconfig/test_experiment_run"
    experiment = Experiment(config_iterator, logdir)
    experiment.start()
    return experiment


def test_run(experiment):
    num_samples = num_workers = 20
    results = experiment.run(exec_func, num_samples, num_workers)
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
