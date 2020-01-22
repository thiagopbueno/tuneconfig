import json
import os

import pytest

import tuneconfig


@pytest.fixture(scope="module")
def pconfig():
    def format_func(param):
        fmt = {
            "batch_size": "batch",
            "horizon": "hr",
            "learning_rate": "lr",
            "optimizer": "opt"
        }
        return fmt.get(param, param)

    return tuneconfig.TuneConfig({
        "batch_size": tuneconfig.grid_search([32, 64, 128]),
        "horizon": 40,
        "learning_rate": tuneconfig.grid_search([0.01, 0.1]),
        "epochs": 1000,
        "optimizer": tuneconfig.grid_search(["Adam", "RMSProp", "GradientDescent"])
        },
        format_func=format_func
    )


def test_grid_search():
    values = tuneconfig.grid_search([0.001, 0.01, 0.1])
    assert isinstance(values, tuneconfig.ParamsIterator)
    assert list(values) == values._lst


def test_tune_config_iterator(pconfig):
    for i, config in enumerate(pconfig):
        assert isinstance(config, dict)
        assert config == pconfig[i]

        for param, value in config.items():
            if param in pconfig._base_dict:
                assert value == pconfig._base_dict[param]
                assert param not in pconfig._params
            else:
                j = pconfig._params.index(param)
                assert value == pconfig._value_instantiations[i][j]
                assert param not in pconfig._base_dict


def test_tune_config_len(pconfig):
    assert len(pconfig) == 18


def test_tune_config_get_item(pconfig):
    for index, config in enumerate(pconfig):
        assert pconfig[index] == config


def test_config_name(pconfig):
    for config in pconfig:
        name = pconfig.name(config)
        assignments = name.split("/")
        assert len(assignments) == len(pconfig._params)
        for assignment in assignments:
            param, value = assignment.split("=")
            assert str(config[param]) == value
            assert param not in pconfig._base_dict


def test_config_full_name(pconfig):
    for config in pconfig:
        name = pconfig.full_name(config)
        assignments = name.split("/")
        assert len(assignments) == len(config)
        for assignment in assignments:
            param, value = assignment.split("=")
            assert str(config[param]) == value


def test_tune_config_dump(pconfig):
    tmp = "/tmp/tuneconfig"

    filepaths = pconfig.dump(tmp, fullname=True)
    assert len(filepaths) == len(pconfig)

    for idx, config in enumerate(pconfig):

        filepath = os.path.join(tmp, pconfig.full_name(config), "config.json")
        assert filepaths[idx] == filepath
        assert os.path.exists(filepath)
        assert os.path.isfile(filepath)

        with open(filepath, "r") as file:
            assert config == json.load(file)

    filepaths = pconfig.dump(tmp, fullname=False)
    assert len(filepaths) == len(pconfig)

    for idx, config in enumerate(pconfig):

        filepath = os.path.join(tmp, pconfig.name(config), "config.json")
        assert filepaths[idx] == filepath
        assert os.path.exists(filepath)
        assert os.path.isfile(filepath)

        with open(filepath, "r") as file:
            assert config == json.load(file)
