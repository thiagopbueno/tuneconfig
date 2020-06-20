import contextlib
import enum
import itertools
import multiprocessing as mp
import os
import re
import shutil

from tqdm import tqdm, trange


@enum.unique
class ExperimentMode(enum.Enum):
    APPEND = 0
    SKIP = 1
    OVERWRITE = 2


class Experiment:
    """
    Experiment -> trials -> runs.
    """

    CONFIG_FILE = "config.json"
    RUN_DIR_REGEX = r"run\d+$"

    def __init__(self, config_iterator, logdir, name=None, description=None):
        self.config_iterator = config_iterator
        self.logdir = logdir
        self.name = name
        self.description = description

    def start(self):
        config_files = self.config_iterator.dump(self.logdir)

    def run(self, exec_func, num_samples, num_workers=None, mode=ExperimentMode.APPEND, verbose=False):
        """
        Executes the trial runner function a given number of times.

        Args:
            exec_func (Callable[Dict] -> Result): The trial runner function.
            num_samples (int): The number of runs per trial.
            num_workers (int): The number of worker processes.
        """
        results = {}

        total_num_trials = len(self.config_iterator)

        for i, config in enumerate(self.config_iterator):
            trial_id, trial_dir = self._get_trial(config)

            info = ""
            skip = False
            if mode == ExperimentMode.OVERWRITE:
                self.remove_old_runs(trial_dir)
                info = "[OVERWRITTEN]"
            elif mode == ExperimentMode.SKIP and self.has_old_runs(trial_dir):
                skip = True
                info = "[SKIPPED]"

            if verbose:
                print(f"\n>> Trial #{i+1}/{total_num_trials} {info}")
                print(config)

            if skip:
                continue

            range_num_samples = self._get_run_ids(trial_dir, num_samples)

            trial_configs = []
            for i, j in enumerate(range_num_samples):
                logdir = os.path.join(trial_dir, f"run{j}")
                if not os.path.exists(logdir):
                    os.makedirs(logdir)

                trial_configs.append({
                    **config,
                    "run_id": j,
                    "logdir": logdir,
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

    @classmethod
    @contextlib.contextmanager
    def trange(cls, epochs, run_id, num_workers, unit="epoch", desc=None, show_progress=True):
        pid = os.getpid()
        position = run_id % num_workers
        desc = f"/ {desc}" if desc else ""
        desc = f"(pid={pid} Run #{run_id:<3d}{desc})"
        disable = not show_progress

        with trange(epochs, desc=desc, unit=unit, position=position, leave=False, disable=disable) as t:
            yield t

    @classmethod
    def is_trial_dir(cls, dirname):
        return cls.CONFIG_FILE in os.listdir(dirname)

    @classmethod
    def is_run_dir(cls, basename):
        return re.search(cls.RUN_DIR_REGEX, basename)

    @classmethod
    def has_old_runs(cls, trial_dir):
        return any(cls.is_run_dir(f.path) for f in os.scandir(trial_dir))

    @classmethod
    def get_run_dirs(cls, trial_dir):
        return [
            f.path for f in os.scandir(trial_dir)
            if cls.is_run_dir(f.path)
        ]

    @classmethod
    def remove_old_runs(cls, trial_dir):
        for path in cls.get_run_dirs(trial_dir):
            shutil.rmtree(path)

    def _get_trial(self, config):
        trial_id = self.config_iterator._trial_id(config)
        trial_dir = os.path.join(self.logdir, trial_id)
        return trial_id, trial_dir

    @classmethod
    def _get_run_ids(cls, trial_dir, num_samples):
        previous_run_dirs = cls.get_run_dirs(trial_dir)
        start_id = len(previous_run_dirs)
        return range(start_id, start_id + num_samples)
