import json
import os

import pytest

import tuneconfig


@pytest.fixture(scope="module")
def pconfig():
    def format_fn(param):
        fmt = {
            "batch_size": "batch",
            "horizon": "hr",
            "learning_rate": "lr",
            "optimizer": "opt",
            "num_samples": None
        }
        return fmt.get(param, param)

    return tuneconfig.TuneConfig({
        "batch_size": tuneconfig.grid_search([32, 64, 128]),
        "horizon": 40,
        "learning_rate": tuneconfig.grid_search([0.01, 0.1]),
        "epochs": 1000,
        "optimizer": tuneconfig.grid_search(["Adam", "RMSProp", "GradientDescent"]),
        "num_samples": 10
        },
        format_fn=format_fn,
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


def test_trial_id(pconfig):
    for config in pconfig:
        name = pconfig._trial_id(config)
        assignments = name.split("/")

        ignore_params = [p for p in config if pconfig._format_fn(p) is None]
        assert len(assignments) == len(config) - len(ignore_params)

        for assignment in assignments:
            param, value = assignment.split("=")

            for p, val in config.items():
                fmt_param = pconfig._format_fn(p)
                if fmt_param == param:
                    assert value == str(val)


def test_tune_config_dump(pconfig):
    tmp = "/tmp/tuneconfig"

    filepaths = pconfig.dump(tmp)
    assert len(filepaths) == len(pconfig)

    for idx, config in enumerate(pconfig):

        filepath = os.path.join(tmp, pconfig._trial_id(config), "config.json")
        assert filepaths[idx] == filepath
        assert os.path.exists(filepath)
        assert os.path.isfile(filepath)

        with open(filepath, "r") as file:
            assert config == json.load(file)


def test_is_config_valid(pconfig):
    ignore = {
        "batch_size": 128,
        "learning_rate": 0.1,
    }

    for config in pconfig:
        for param, value in ignore.items():
            if param not in config or config[param] != value:
                assert pconfig._is_config_valid(config, ignore)

    ignore = [
        {
            "batch_size": 128,
            "learning_rate": 0.1,
        },
        {
            "batch_size": 32,
            "optimizer": "GradientDescent",
            "learning_rate": 0.01,
        },
        {
            "horizon": 100,
            "batch_size": 64
        }
    ]

    for config in pconfig:
        for no_config in ignore:
            for param, value in no_config.items():
                if param not in config or config[param] != value:
                    assert pconfig._is_config_valid(config, no_config)


def test_tune_config_filter(pconfig):
    ignore = [
        {
            "batch_size": 128,
            "learning_rate": 0.1,
        },
        {
            "batch_size": 32,
            "optimizer": "GradientDescent",
            "learning_rate": 0.01,
        },
        {
            "horizon": 100,
            "batch_size": 64
        }
    ]

    tmp = "/tmp/tuneconfig"

    filepaths = pconfig.dump(tmp, ignore=ignore)

    num_valid_configs = 0
    for config in pconfig:

        if not pconfig._is_config_valid(config, ignore):
            filepath = os.path.join(tmp, pconfig._trial_id(config), "config.json")
            assert filepath not in filepaths
        else:
            num_valid_configs += 1

    assert len(filepaths) == num_valid_configs
