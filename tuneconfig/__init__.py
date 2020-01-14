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

        for key, value in self._config_dict.items():
            if isinstance(value, ParamsIterator):
                self._params_iterators[key] = list(value)
            else:
                self._base_dict[key] = value

        self._params = self._params_iterators.keys()
        self._values = self._params_iterators.values()
        self._value_instantiations = list(itertools.product(*self._values))

    def __len__(self):
        return len(self._value_instantiations)

    def __getitem__(self, i):
        values = self._value_instantiations[i]

        name = []
        for param, value in zip(self._params, values):
            if self._format_func:
                param = self._format_func(param)
            name.append(f"{param}={value}")
        name = '/'.join(name)

        return {
            "index": i,
            "name": name,
            "value": {
                **self._base_dict,
                **dict(zip(self._params, values))
            }
        }

    def __iter__(self):
        self._index = 0
        return self

    def __next__(self):
        i = self._index
        self._index += 1

        if i == len(self._value_instantiations):
            raise StopIteration

        return self[i]["value"]

    def dump(self, dirpath, subfolders=True):
        json_files_created = []

        basepath = dirpath
        for index, params_config in enumerate(self):

            if subfolders:
                dirpath = os.path.join(basepath, str(index))
                filename = "config.json"
            else:
                dirpath = basepath
                filename = f"config{index}.json"

            if not os.path.exists(dirpath):
                os.makedirs(dirpath)

            filepath = os.path.join(dirpath, filename)

            with open(filepath, "w") as file:
                json.dump(params_config, file)
                json_files_created.append(filepath)

        return json_files_created
