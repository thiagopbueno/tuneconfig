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

    def __init__(self, config_dict, format_func=None):
        self._config_dict = config_dict
        self._format_func = format_func

        self._base_dict = {}
        self._params_iterators = {}

        for param, value in self._config_dict.items():
            if self._format_func is not None:
                param = self._format_func(param)

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

    def name(self, config):
        assignments = []
        for param in sorted(config):
            if param not in self._params:
                continue
            value = config[param]
            assignments.append(f"{param}={value}")
        return '/'.join(assignments)

    def full_name(self, config):
        assignments = []
        for param in sorted(config):
            value = config[param]
            assignments.append(f"{param}={value}")
        return '/'.join(assignments)

    def dump(self, basepath, fullname=True):
        json_files_created = []

        for config in self:

            experiment_id = self.full_name(config) if fullname else self.name(config)

            dirpath = os.path.join(basepath, experiment_id)

            if not os.path.exists(dirpath):
                os.makedirs(dirpath)

            filename = "config.json"
            filepath = os.path.join(dirpath, filename)

            with open(filepath, "w") as file:
                json.dump(config, file)
                json_files_created.append(filepath)

        return json_files_created
