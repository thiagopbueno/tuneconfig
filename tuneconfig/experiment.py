import itertools
import multiprocessing as mp
import os
import re
from tqdm import tqdm


class Experiment:
    """
    Experiment -> trials -> runs.
    """

    def __init__(self, config_iterator, logdir, name=None, description=None):
        self.config_iterator = config_iterator
        self.logdir = logdir
        self.name = name
        self.description = description

    def start(self):
        config_files = self.config_iterator.dump(self.logdir)

    def run(self, exec_func, num_samples, num_workers=None):
        """
        Executes the trial runner function a given number of times.

        Args:
            exec_func (Callable[Dict] -> Result): The trial runner function (e.g., exec_func(config, logdir)).
            num_samples (int): The number of runs per trial.
            num_workers (int): The number of worker processes.
        """
        results = {}

        for config in self.config_iterator:
            trial_id = self.config_iterator._trial_id(config)
            trial_dir = os.path.join(self.logdir, trial_id)

            range_num_samples = self._run_ids(trial_dir, num_samples)

            trial_configs = []
            for i, j in enumerate(range_num_samples):
                trial_configs.append({
                    **config,
                    "run_id": i,
                    "logdir": os.path.join(trial_dir, f"run{j}"),
                })

            pool = mp.Pool(
                processes=num_workers,
                initializer=tqdm.set_lock,
                initargs=(tqdm.get_lock(),)
            )
            results[trial_id] = pool.map(exec_func, trial_configs)
            pool.close()
            pool.join()

        return results


    def _run_ids(self, trial_dir, num_samples):
        previous_run_dirs = [
            path for path in os.listdir(trial_dir) if re.search(r"run\d+$", path)
        ]
        start_id = len(previous_run_dirs)
        return range(start_id, start_id + num_samples)
