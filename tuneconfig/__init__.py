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


class TuneConfig:

    def __init__(self, config_dict, format_fn=None):
        self._config_dict = config_dict
        self._format_fn = format_fn

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

    def __len__(self):
        return len(self._value_instantiations)

    def __getitem__(self, i):
        values = self._value_instantiations[i]
        return {
            **self._base_dict,
            **dict(zip(self._params, values))
        }

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

        return '/'.join(assignments)

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
