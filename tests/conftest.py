import os
from collections import namedtuple
import itertools
import random
import shutil

import multiprocessing as mp
import pandas as pd
import pytest

from tuneconfig import *


PlotConfig = namedtuple("PlotConfig", "targets x_axis y_axis anchors")


def exec_func(config):
    logdir = config["logdir"]
    run_id = logdir.split("/")[-1]
    del config["logdir"]
    os.makedirs(logdir)

    df = pd.DataFrame(
        {
            "foo": pd.Series([random.gauss(10.0, 1.0) for _ in range(10)]),
            "baz": pd.Series([random.gauss(20.0, 2.0) for _ in range(10)]),
            "bar": pd.Series([random.gauss(30.0, 3.0) for _ in range(10)]),
        }
    )
    filepath = os.path.join(logdir, "data.csv")
    df.to_csv(filepath, index=False)

    df = pd.DataFrame(
        {"test": pd.Series([random.randrange(-10.0, 10.0) for _ in range(10)]),}
    )
    filepath = os.path.join(logdir, "metric.csv")
    df.to_csv(filepath, index=False)

    return (mp.current_process().pid, config, logdir, run_id)


@pytest.fixture(scope="session")
def config_factory():
    def format_fn(param):
        fmt = {
            # "batch_size": "batch",
            # "horizon": "hr",
            # "learning_rate": "lr",
            # "optimizer": "opt",
            "num_samples": None
        }
        return fmt.get(param, param)

    return ConfigFactory(
        {
            "batch_size": grid_search([32, 64, 128]),
            "horizon": 40,
            "learning_rate": grid_search([0.01, 0.1]),
            "epochs": 1000,
            "optimizer": grid_search(["Adam", "RMSProp", "GradientDescent"]),
            "num_samples": 10,
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


def confplot_idfn(fixture_value):
    return "_".join(filter(None, fixture_value))


@pytest.fixture(
    scope="module",
    params=list(
        itertools.product(
            ["single_target", "multiple_targets"],
            ["single_plot", "multiple_plots"],
            ["x_axis", None],
            ["y_axis", None],
        )
    ),
    ids=confplot_idfn,
)
def confplot(request):
    target_type, plot_type, x_axis, y_axis = request.param

    if target_type == "single_target":
        targets = ["metric:test"]
    else:
        targets = ["data:foo", "data:bar"]

    anchors = ["learning_rate=0.1", "horizon=40", "epochs=1000"]

    if x_axis:
        x_axis = "optimizer"
        if plot_type == "single_plot":
            anchors.append("batch_size=32")

    if y_axis:
        y_axis = "batch_size"
        if plot_type == "single_plot":
            anchors.append("optimizer=Adam")

    return PlotConfig(targets, x_axis, y_axis, anchors)


@pytest.fixture(scope="session")
def cfg_single_target_no_axes():
    targets = ["metric:test"]
    x_axis, y_axis = None, None
    anchors = ["batch_size=32", "learning_rate=0.1", "optimizer=Adam"]
    return PlotConfig(targets, x_axis, y_axis, anchors)


@pytest.fixture(scope="session")
def cfg_multiple_targets_no_axes():
    targets = ["data:foo", "data:baz"]
    x_axis, y_axis = None, None
    anchors = ["batch_size=32", "learning_rate=0.1", "optimizer=Adam"]
    return PlotConfig(targets, x_axis, y_axis, anchors)


@pytest.fixture(scope="session")
def cfg_single_target_multiple_plots_no_axes():
    targets = ["metric:test"]
    x_axis, y_axis = None, None
    anchors = ["batch_size=32", "learning_rate=0.1"]
    return PlotConfig(targets, x_axis, y_axis, anchors)


@pytest.fixture(scope="session")
def cfg_multiple_targets_multiple_plots_no_axes():
    targets = ["data:foo", "data:baz"]
    x_axis, y_axis = None, None
    anchors = ["batch_size=32", "learning_rate=0.1"]
    return PlotConfig(targets, x_axis, y_axis, anchors)


@pytest.fixture(scope="session")
def cfg_single_target_x_axis():
    targets = ["metric:test"]
    x_axis, y_axis = "optimizer", None
    anchors = ["batch_size=32", "learning_rate=0.1"]
    return PlotConfig(targets, x_axis, y_axis, anchors)


@pytest.fixture(scope="session")
def cfg_multiple_targets_x_axis():
    targets = ["data:foo", "data:baz"]
    x_axis, y_axis = "optimizer", None
    anchors = ["batch_size=32", "learning_rate=0.1"]
    return PlotConfig(targets, x_axis, y_axis, anchors)


@pytest.fixture(scope="session")
def cfg_single_target_y_axis():
    targets = ["metric:test"]
    x_axis, y_axis = None, "batch_size"
    anchors = ["learning_rate=0.1", "optimizer=Adam"]
    return PlotConfig(targets, x_axis, y_axis, anchors)


@pytest.fixture(scope="session")
def cfg_multiple_targets_y_axis():
    targets = ["data:foo", "data:baz"]
    x_axis, y_axis = None, "batch_size"
    anchors = ["learning_rate=0.1", "optimizer=Adam"]
    return PlotConfig(targets, x_axis, y_axis, anchors)


@pytest.fixture(scope="session")
def cfg_single_target_both_axis():
    targets = ["metric:test"]
    x_axis, y_axis = "optimizer", "learning_rate"
    anchors = ["batch_size=128"]
    return PlotConfig(targets, x_axis, y_axis, anchors)


@pytest.fixture(scope="session")
def cfg_multiple_targets_both_axis():
    targets = ["data:foo", "data:baz"]
    x_axis, y_axis = "optimizer", "learning_rate"
    anchors = ["batch_size=128"]
    return PlotConfig(targets, x_axis, y_axis, anchors)
