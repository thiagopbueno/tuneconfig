import itertools
import json
import os


def grid_search(lst):
    return ParamsIterator(lst)


class ParamsIterator:
    def __init__(self, lst):
        self._lst = lst

    def __iter__(self):
        return iter(self._lst)


class ConfigFactory:
    def __init__(self, config_dict, format_fn=None):
        self._config_dict = config_dict
        self._format_fn = format_fn

        self._reset()

    def _reset(self):
        self._base_dict = {}
        self._params_iterators = {}

        for param, value in self._config_dict.items():
            if isinstance(value, ParamsIterator):
                self._params_iterators[param] = list(value)
            else:
                self._base_dict[param] = value

        self._params = list(self._params_iterators.keys())
        self._values = list(self._params_iterators.values())
        self._value_instantiations = list(itertools.product(*self._values))

    def get(self, param):
        if param not in self._config_dict:
            return None
        values = self._config_dict[param]
        if isinstance(values, ParamsIterator):
            return list(values)
        else:
            return values

    def set(self, param, value):
        self._config_dict[param] = value
        self._reset()

    def update(self, config_dict):
        self._config_dict.update(config_dict)
        self._reset()

    def __len__(self):
        return len(self._value_instantiations)

    def __getitem__(self, i):
        values = self._value_instantiations[i]
        return {**self._base_dict, **dict(zip(self._params, values))}

    def __iter__(self):
        self._index = 0
        return self

    def __next__(self):
        i = self._index
        self._index += 1

        if i == len(self._value_instantiations):
            raise StopIteration

        return self[i]

    def _trial_id(self, config):
        assignments = []

        for param in sorted(config):
            fmt_param = param
            if self._format_fn:
                fmt_param = self._format_fn(param)

            if fmt_param is None:
                continue

            value = config[param]
            assignments.append(f"{fmt_param}={value}")

        return "/".join(assignments)

    def dump(self, basepath, ignore=None):
        json_files_created = []

        for config in self:
            if not self._is_config_valid(config, ignore):
                continue

            dirpath = os.path.join(basepath, self._trial_id(config))

            if not os.path.exists(dirpath):
                os.makedirs(dirpath)

            filename = "config.json"
            filepath = os.path.join(dirpath, filename)

            with open(filepath, "w") as file:
                json.dump(config, file)
                json_files_created.append(filepath)

        return json_files_created

    def _is_config_valid(self, config, ignore):
        if ignore is None:
            return True

        if isinstance(ignore, dict):
            ignore = [ignore]

        valid = True
        for no_config in ignore:
            if all(config.get(key) == value for key, value in no_config.items()):
                valid = False
                break

        return valid

    @classmethod
    def from_dict(cls, config_dict, format_fn=None):
        def _get_params_iterator(value):
            valid_params_iterators = ["__grid_search__"]
            if (
                not isinstance(value, list)
                or len(value) == 0
                or value[0] not in valid_params_iterators
            ):
                return value

            if value[0] == "__grid_search__":
                assert isinstance(value[1], list)
                return grid_search(value[1])
            else:
                raise ValueError(f"Not a valid ParamsIterator: '{values}'.")

        return ConfigFactory(
            {
                param: _get_params_iterator(value)
                for param, value in config_dict.items()
            },
            format_fn=format_fn,
        )

    @classmethod
    def from_json(cls, filepath, format_fn=None):
        with open(filepath, "r") as file:
            return cls.from_dict(json.load(file), format_fn=format_fn)
