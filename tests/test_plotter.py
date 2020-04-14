import matplotlib.pyplot as plt
import pytest

from tuneconfig.plotter import ExperimentPlotter


@pytest.fixture
def plotter(analysis_list):
    return ExperimentPlotter(*analysis_list)


def test_plot_single_target_no_axis(plotter):
    targets = ["metric:test"]
    x_axis, y_axis = None, None
    anchors = [
        "batch_size=32",
        "learning_rate=0.1",
        "optimizer=Adam",
        "epochs=1000",
        "horizon=40",
    ]
    fig = plotter.plot(targets, x_axis, y_axis, anchors)
    assert isinstance(fig, plt.Figure)
