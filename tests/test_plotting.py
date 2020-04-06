import pytest

from tuneconfig.plotting import ExperimentPlotter


@pytest.fixture(scope="module")
def plotter(analysis):
    return ExperimentPlotter(analysis)


def test_plot(plotter):
    targets = ["data:foo", "data:baz"]
    anchors = ["batch=32", "lr=0.01"]
    x_axis, y_axis = None, "optimizer"
    kwargs = {
        "target_x_axis_label": "Epochs",
        "target_y_axis_label": "Loss"
    }

    plotter.plot(targets, anchors, x_axis, y_axis, **kwargs)
