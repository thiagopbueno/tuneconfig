import json
import os

import pytest

import tuneconfig


@pytest.fixture(scope="module")
def config():
    return tuneconfig.TuneConfig({
        "batch_size": tuneconfig.grid_search([32, 64, 128]),
        "horizon": 40,
        "learning_rate": tuneconfig.grid_search([0.01, 0.1]),
        "epochs": 1000,
        "optimizer": tuneconfig.grid_search(["Adam", "RMSProp", "GradientDescent"])
    })


def test_grid_search():
    values = tuneconfig.grid_search([0.001, 0.01, 0.1])
    assert isinstance(values, tuneconfig.ParamsIterator)
    assert list(values) == values._lst


def test_tune_config_iterator(config):
    for params_config in config:
        assert isinstance(params_config, dict)
        assert len(params_config) == len(config._config_dict)


def test_tune_config_dump(config):
    tmp = "/tmp/tuneconfig"

    config.dump(tmp, subfolders=True)
    for index, params_config in enumerate(config):
        dirpath = os.path.join(tmp, str(index))
        filepath = os.path.join(dirpath, "config.json")
        assert os.path.exists(dirpath)
        assert os.path.exists(filepath)
        assert os.path.isfile(filepath)

        with open(filepath, "r") as file:
            assert params_config == json.load(file)

    config.dump(tmp, subfolders=False)
    for index, params_config in enumerate(config):
        dirpath = tmp
        filepath = os.path.join(dirpath, f"config{index}.json")
        assert os.path.exists(dirpath)
        assert os.path.exists(filepath)
        assert os.path.isfile(filepath)

        with open(filepath, "r") as file:
            assert params_config == json.load(file)

