from pprint import pprint
import time

import matplotlib.pyplot as plt
import pytest

from tuneconfig.plotter import ExperimentPlotter


@pytest.fixture
def plotter(analysis_list):
    kwargs = {
        "plot_type": "line",
        "figsize": (7, 5),
        "sharex": False,
        "sharey": False,
        "target_x_axis_label": None,
        "target_y_axis_label": None,
    }

    return ExperimentPlotter(*analysis_list, **kwargs)


def test_line_plot(plotter, confplot):
    fig = plotter.plot(*confplot)
    assert isinstance(fig, plt.Figure)
    # plt.show()
    fig.clear()
    plt.close(fig)


def test_bar_plot(plotter, confplot):
    plotter.kwargs["plot_type"] = "bar"
    targets, x_axis, y_axis, anchors = confplot
    targets = [f"mean/{target}" for target in targets]
    fig = plotter.plot(targets, x_axis, y_axis, anchors)
    assert isinstance(fig, plt.Figure)
    # plt.show()
    fig.clear()
    plt.close(fig)
