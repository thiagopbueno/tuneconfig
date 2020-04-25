from tuneconfig.experiment import Experiment, ExperimentMode
from tuneconfig.analysis import ExperimentAnalysis


def run_experiment(exec_func,
                   config_factory,
                   logdir,
                   num_samples=1,
                   num_workers=1,
                   mode=ExperimentMode.APPEND,
                   name=None,
                   verbose=True):
    # pylint: disable=too-many-arguments

    experiment = Experiment(config_factory, logdir)
    experiment.start()
    experiment.run(
        exec_func, num_samples, num_workers, mode=mode, verbose=verbose)

    analysis = ExperimentAnalysis(logdir, name=name)
    analysis.setup()
    return analysis
