import multiprocessing as mp
import os
import pytest

import tuneconfig
from tuneconfig.experiment import Experiment


def exec_func(config):
    logdir = config["logdir"]
    run_id = logdir.split("/")[-1]
    del config["logdir"]
    os.makedirs(logdir)
    return (mp.current_process().name, config, logdir, run_id)


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


def test_run(config_iterator):
    logdir = "/tmp/tuneconfig/test_experiment_run"
    num_samples = num_workers = 10
    experiment = Experiment(config_iterator, logdir)
    experiment.start()
    results = experiment.run(exec_func, num_samples, num_workers)
    assert len(results) == len(config_iterator)
    for trial_id, trial_results in results.items():
        assert len(trial_results) == num_samples
        for pname, config, run_dir, run_id in trial_results:
            assert run_dir not in config
            assert os.path.exists(run_dir)
