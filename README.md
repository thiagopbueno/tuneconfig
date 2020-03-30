# tuneconfig [![Py Versions][py-versions.svg]][pypi-project] [![PyPI version][pypi-version.svg]][pypi-version] [![Build Status][travis.svg]][travis-project] [![Documentation Status][rtd-badge.svg]][rtd-badge] [![License: GPL v3][license.svg]][license]

Hyperparameter config file generator and experiment runner.


## Quickstart

```bash
$ pip install -U tuneconfig
```


## Usage


### Config file generator

```python
import pprint

import tuneconfig

# Define parameter formatting function
def format_fn(param):
    fmt = {
        "batch_size": "batch",
        "horizon": "hr",
        "learning_rate": "lr",
        "optimizer": "opt",
        "epochs": None,
        "num_samples": None,
    }
    return fmt.get(param, param)

# Define a configuration template for grid search
config_iterator = tuneconfig.TuneConfig({
    "batch_size": tuneconfig.grid_search([32, 128]),
    "horizon": 40,
    "learning_rate": tuneconfig.grid_search([0.01, 0.1]),
    "epochs": 1000,
    "optimizer": tuneconfig.grid_search(["Adam", "RMSProp"]),
    "num_samples": 10
    },
    format_fn=format_fn
)

# Iterate over config dicts
for idx, config in enumerate(config_iterator):
    name = config_iterator._trial_id(config)
    print(f"config {idx} ({name}):")
    pprint.pprint(config)
    print()

# Dump config dicts as JSON files
tmp = "/tmp/tuneconfig"
json_config_files = config_iterator.dump(tmp)
print(">> Saved config files:")
pprint.pprint(json_config_files)
```

```bash
config 0 (batch=32/hr=40/lr=0.01/opt=Adam):
{'batch_size': 32,
 'epochs': 1000,
 'horizon': 40,
 'learning_rate': 0.01,
 'num_samples': 10,
 'optimizer': 'Adam'}

config 1 (batch=32/hr=40/lr=0.01/opt=RMSProp):
{'batch_size': 32,
 'epochs': 1000,
 'horizon': 40,
 'learning_rate': 0.01,
 'num_samples': 10,
 'optimizer': 'RMSProp'}

config 2 (batch=32/hr=40/lr=0.1/opt=Adam):
{'batch_size': 32,
 'epochs': 1000,
 'horizon': 40,
 'learning_rate': 0.1,
 'num_samples': 10,
 'optimizer': 'Adam'}

config 3 (batch=32/hr=40/lr=0.1/opt=RMSProp):
{'batch_size': 32,
 'epochs': 1000,
 'horizon': 40,
 'learning_rate': 0.1,
 'num_samples': 10,
 'optimizer': 'RMSProp'}

config 4 (batch=128/hr=40/lr=0.01/opt=Adam):
{'batch_size': 128,
 'epochs': 1000,
 'horizon': 40,
 'learning_rate': 0.01,
 'num_samples': 10,
 'optimizer': 'Adam'}

config 5 (batch=128/hr=40/lr=0.01/opt=RMSProp):
{'batch_size': 128,
 'epochs': 1000,
 'horizon': 40,
 'learning_rate': 0.01,
 'num_samples': 10,
 'optimizer': 'RMSProp'}

config 6 (batch=128/hr=40/lr=0.1/opt=Adam):
{'batch_size': 128,
 'epochs': 1000,
 'horizon': 40,
 'learning_rate': 0.1,
 'num_samples': 10,
 'optimizer': 'Adam'}

config 7 (batch=128/hr=40/lr=0.1/opt=RMSProp):
{'batch_size': 128,
 'epochs': 1000,
 'horizon': 40,
 'learning_rate': 0.1,
 'num_samples': 10,
 'optimizer': 'RMSProp'}

>> Saved config files:
['/tmp/tuneconfig/batch=32/hr=40/lr=0.01/opt=Adam/config.json',
 '/tmp/tuneconfig/batch=32/hr=40/lr=0.01/opt=RMSProp/config.json',
 '/tmp/tuneconfig/batch=32/hr=40/lr=0.1/opt=Adam/config.json',
 '/tmp/tuneconfig/batch=32/hr=40/lr=0.1/opt=RMSProp/config.json',
 '/tmp/tuneconfig/batch=128/hr=40/lr=0.01/opt=Adam/config.json',
 '/tmp/tuneconfig/batch=128/hr=40/lr=0.01/opt=RMSProp/config.json',
 '/tmp/tuneconfig/batch=128/hr=40/lr=0.1/opt=Adam/config.json',
 '/tmp/tuneconfig/batch=128/hr=40/lr=0.1/opt=RMSProp/config.json']

```


# License

Copyright (c) 2020 Thiago Pereira Bueno All Rights Reserved.

tuneconfig is free software: you can redistribute it and/or modify it
under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at
your option) any later version.

tuneconfig is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser
General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with tuneconfig. If not, see http://www.gnu.org/licenses/.


[py-versions.svg]: https://img.shields.io/pypi/pyversions/tuneconfig.svg?logo=python&logoColor=white
[pypi-project]: https://pypi.org/project/tuneconfig

[pypi-version.svg]: https://badge.fury.io/py/tuneconfig.svg
[pypi-version]: https://badge.fury.io/py/tuneconfig

[travis.svg]: https://img.shields.io/travis/thiagopbueno/tuneconfig/master.svg?logo=travis
[travis-project]: https://travis-ci.org/thiagopbueno/tuneconfig

[rtd-badge.svg]: https://readthedocs.org/projects/tuneconfig/badge/?version=latest
[rtd-badge]: https://tuneconfig.readthedocs.io/en/latest/?badge=latest

[license.svg]: https://img.shields.io/badge/License-GPL%20v3-blue.svg
[license]: https://github.com/thiagopbueno/tuneconfig/blob/master/LICENSE
