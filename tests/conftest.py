import os
import random
import shutil

import multiprocessing as mp
import pandas as pd
import pytest

from tuneconfig import *


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

    df = pd.DataFrame({
        "test": pd.Series([random.randrange(-10.0, 10.0) for _ in range(10)]),
    })
    filepath = os.path.join(logdir, "metric.csv")
    df.to_csv(filepath, index=False)

    return (mp.current_process().pid, config, logdir, run_id)


@pytest.fixture(scope="session")
def config_factory():
    def format_fn(param):
        fmt = {
            "batch_size": "batch",
            "horizon": "hr",
            "learning_rate": "lr",
            "optimizer": "opt",
            "num_samples": None
        }
        return fmt.get(param, param)

    return ConfigFactory({
        "batch_size": grid_search([32, 64, 128]),
        "horizon": 40,
        "learning_rate": grid_search([0.01, 0.1]),
        "epochs": 1000,
        "optimizer": grid_search(["Adam", "RMSProp", "GradientDescent"]),
        "num_samples": 10
        },
        format_fn=format_fn,
    )


@pytest.fixture(scope="session")
def experiment(config_factory):
    logdir = "/tmp/tuneconfig_1"
    experiment = Experiment(config_factory, logdir)
    experiment.start()
    yield experiment
    shutil.rmtree(logdir)


@pytest.fixture(scope="session")
def analysis(experiment):
    num_samples = num_workers = 10
    _ = experiment.run(exec_func, num_samples, num_workers)
    analysis = ExperimentAnalysis(experiment.logdir)
    analysis.setup()
    return analysis


@pytest.fixture(scope="session")
def trial(analysis):
    return analysis[0]


@pytest.fixture(scope="session")
def analysis_list(config_factory):
    basedir = "/tmp/tuneconfig_2"
    num_samples = num_workers = 3

    analyses = []
    for i in range(3):
        name = f"experiment{i}"
        logdir = os.path.join(basedir, name)
        experiment = Experiment(config_factory, logdir)
        experiment.start()
        _ = experiment.run(exec_func, num_samples, num_workers)
        exp_analysis = ExperimentAnalysis(experiment.logdir, name)
        exp_analysis.setup()
        analyses.append(exp_analysis)

    yield analyses

    for analysis in analyses:
        shutil.rmtree(analysis.logdir)
