import json
import os

import pytest

from tuneconfig.config_factory import ParamsIterator, grid_search, ConfigFactory


def test_grid_search():
    values = grid_search([0.001, 0.01, 0.1])
    assert isinstance(values, ParamsIterator)
    assert list(values) == values._lst


def test_tune_config_iterator(config_factory):
    for i, config in enumerate(config_factory):
        assert isinstance(config, dict)
        assert config == config_factory[i]

        for param, value in config.items():
            if param in config_factory._base_dict:
                assert value == config_factory._base_dict[param]
                assert param not in config_factory._params
            else:
                j = config_factory._params.index(param)
                assert value == config_factory._value_instantiations[i][j]
                assert param not in config_factory._base_dict


def test_tune_config_len(config_factory):
    assert len(config_factory) == 18


def test_tune_config_get_item(config_factory):
    for index, config in enumerate(config_factory):
        assert config_factory[index] == config


def test_trial_id(config_factory):
    for config in config_factory:
        name = config_factory._trial_id(config)
        assignments = name.split("/")

        ignore_params = [p for p in config if config_factory._format_fn(p) is None]
        assert len(assignments) == len(config) - len(ignore_params)

        for assignment in assignments:
            param, value = assignment.split("=")

            for p, val in config.items():
                fmt_param = config_factory._format_fn(p)
                if fmt_param == param:
                    assert value == str(val)


def test_tune_config_dump(config_factory):
    tmp = "/tmp/tuneconfig"

    filepaths = config_factory.dump(tmp)
    assert len(filepaths) == len(config_factory)

    for idx, config in enumerate(config_factory):

        filepath = os.path.join(tmp, config_factory._trial_id(config), "config.json")
        assert filepaths[idx] == filepath
        assert os.path.exists(filepath)
        assert os.path.isfile(filepath)

        with open(filepath, "r") as file:
            assert config == json.load(file)


def test_is_config_valid(config_factory):
    ignore = {
        "batch_size": 128,
        "learning_rate": 0.1,
    }

    for config in config_factory:
        for param, value in ignore.items():
            if param not in config or config[param] != value:
                assert config_factory._is_config_valid(config, ignore)

    ignore = [
        {"batch_size": 128, "learning_rate": 0.1,},
        {"batch_size": 32, "optimizer": "GradientDescent", "learning_rate": 0.01,},
        {"horizon": 100, "batch_size": 64},
    ]

    for config in config_factory:
        for no_config in ignore:
            for param, value in no_config.items():
                if param not in config or config[param] != value:
                    assert config_factory._is_config_valid(config, no_config)


def test_tune_config_filter(config_factory):
    ignore = [
        {"batch_size": 128, "learning_rate": 0.1,},
        {"batch_size": 32, "optimizer": "GradientDescent", "learning_rate": 0.01,},
        {"horizon": 100, "batch_size": 64},
    ]

    tmp = "/tmp/tuneconfig"

    filepaths = config_factory.dump(tmp, ignore=ignore)

    num_valid_configs = 0
    for config in config_factory:

        if not config_factory._is_config_valid(config, ignore):
            filepath = os.path.join(
                tmp, config_factory._trial_id(config), "config.json"
            )
            assert filepath not in filepaths
        else:
            num_valid_configs += 1

    assert len(filepaths) == num_valid_configs


def test_create_config_factory_from_dict():
    config_dict = {
        "batch_size": ["__grid_search__", [32, 64, 128, 1024]],
        "horizon": 40,
        "lr": ["__grid_search__", [0.005, 0.001, 0.01]],
        "optimizer": ["__grid_search__", ["GradientDescent", "RMSProp"]],
    }

    config_factory = ConfigFactory.from_dict(config_dict)

    assert isinstance(config_factory, ConfigFactory)
    assert len(config_factory) == 24
    assert config_factory.get("batch_size") == config_dict["batch_size"][-1]
    assert config_factory.get("horizon") == config_dict["horizon"]
    assert config_factory.get("lr") == config_dict["lr"][-1]
    assert config_factory.get("optimizer") == config_dict["optimizer"][-1]


def test_create_config_factory_from_json():
    config_dict = {
        "batch_size": ["__grid_search__", [32, 64, 128, 1024]],
        "horizon": 40,
        "lr": ["__grid_search__", [0.005, 0.001, 0.01]],
        "optimizer": ["__grid_search__", ["GradientDescent", "RMSProp"]],
    }

    config_json = "/tmp/tuneconfig/experiment_config.json"
    with open(config_json, "w") as file:
        json.dump(config_dict, file)

    config_factory = ConfigFactory.from_json(config_json)

    assert isinstance(config_factory, ConfigFactory)
    assert len(config_factory) == 24
    assert config_factory.get("batch_size") == config_dict["batch_size"][-1]
    assert config_factory.get("horizon") == config_dict["horizon"]
    assert config_factory.get("lr") == config_dict["lr"][-1]
    assert config_factory.get("optimizer") == config_dict["optimizer"][-1]
