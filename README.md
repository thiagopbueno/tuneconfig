# tuneconfig

Hyperparameter config file generator.


## Quickstart

```bash
$ pip install -U tuneconfig
```


## Usage

```python
import pprint

import tuneconfig

# Define a configuration template for grid search
config_template = tuneconfig.TuneConfig({
    "batch_size": tuneconfig.grid_search([32, 128]),
    "horizon": 40,
    "learning_rate": tuneconfig.grid_search([0.01, 0.1]),
    "epochs": 1000,
    "optimizer": tuneconfig.grid_search(["Adam", "RMSProp"])
})

# Iterate over config dicts
for idx, config in enumerate(config_template):
    name = config_template.name(config)
    print(f"config {idx} ({name}):")
    pprint.pprint(config)
    print()

# Dump config dicts as JSON files
tmp = "/tmp/tuneconfig"
config_template.dump(dirpath=tmp)
```

```bash
config #0 (batch_size=32/learning_rate=0.01/optimizer=Adam):
{'batch_size': 32,
 'epochs': 1000,
 'horizon': 40,
 'learning_rate': 0.01,
 'optimizer': 'Adam'}

config #1 (batch_size=32/learning_rate=0.01/optimizer=RMSProp):
{'batch_size': 32,
 'epochs': 1000,
 'horizon': 40,
 'learning_rate': 0.01,
 'optimizer': 'RMSProp'}

config #2 (batch_size=32/learning_rate=0.1/optimizer=Adam):
{'batch_size': 32,
 'epochs': 1000,
 'horizon': 40,
 'learning_rate': 0.1,
 'optimizer': 'Adam'}

config #3 (batch_size=32/learning_rate=0.1/optimizer=RMSProp):
{'batch_size': 32,
 'epochs': 1000,
 'horizon': 40,
 'learning_rate': 0.1,
 'optimizer': 'RMSProp'}

config #4 (batch_size=128/learning_rate=0.01/optimizer=Adam):
{'batch_size': 128,
 'epochs': 1000,
 'horizon': 40,
 'learning_rate': 0.01,
 'optimizer': 'Adam'}

config #5 (batch_size=128/learning_rate=0.01/optimizer=RMSProp):
{'batch_size': 128,
 'epochs': 1000,
 'horizon': 40,
 'learning_rate': 0.01,
 'optimizer': 'RMSProp'}

config #6 (batch_size=128/learning_rate=0.1/optimizer=Adam):
{'batch_size': 128,
 'epochs': 1000,
 'horizon': 40,
 'learning_rate': 0.1,
 'optimizer': 'Adam'}

config #7 (batch_size=128/learning_rate=0.1/optimizer=RMSProp):
{'batch_size': 128,
 'epochs': 1000,
 'horizon': 40,
 'learning_rate': 0.1,
 'optimizer': 'RMSProp'}
```


# License

Copyright (c) 2020 Thiago Pereira Bueno All Rights Reserved.

tf-plan is free software: you can redistribute it and/or modify it
under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at
your option) any later version.

tf-plan is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser
General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with tf-plan. If not, see http://www.gnu.org/licenses/.
