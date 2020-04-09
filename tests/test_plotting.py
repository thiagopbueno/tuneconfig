import pytest

from tuneconfig.plotting import ExperimentPlotter


def test_plot_line(analysis):
    targets = ["data:foo", "data:baz"]
    anchors = ["batch=32", "lr=0.01"]
    x_axis, y_axis = None, "optimizer"
    kwargs = {
        "plot_type": "line",
        "target_x_axis_label": "Epochs",
        "target_y_axis_label": "Loss",
    }

    plotter = ExperimentPlotter(analysis)
    plotter.plot(targets, anchors, x_axis, y_axis, show_fig=False, **kwargs)


def test_plot_line_multiple_analysis(analysis_list):
    for analysis in analysis_list:
        print()
        analysis.info()

    targets = ["data:bar", "metric:test"]
    anchors = ["batch=128", "lr=0.1"]
    x_axis, y_axis = "optimizer", None
    kwargs = {
        "plot_type": "line",
        "target_x_axis_label": "Epochs",
        "target_y_axis_label": "Loss",
    }

    plotter = ExperimentPlotter(analysis_list)
    plotter.plot(targets, anchors, x_axis, y_axis, show_fig=False, **kwargs)


def test_plot_bar(analysis):
    targets = ["sum/data:foo", "mean/data:baz"]
    anchors = ["batch=32", "lr=0.01"]
    x_axis, y_axis = None, "optimizer"
    kwargs = {
        "plot_type": "bar",
        "target_x_axis_label": "",
        "target_y_axis_label": "Cumulative Reward",
    }

    plotter = ExperimentPlotter(analysis)
    plotter.plot(targets, anchors, x_axis, y_axis, show_fig=False, **kwargs)


def test_plot_bar_multiple_analysis(analysis_list):
    for analysis in analysis_list:
        print()
        analysis.info()

    targets = ["mean/data:bar", "sum/metric:test"]
    anchors = ["batch=128", "lr=0.1"]
    x_axis, y_axis = "optimizer", None
    kwargs = {
        "plot_type": "bar",
        "target_x_axis_label": "",
        "target_y_axis_label": "Cumulative Reward",
    }

    plotter = ExperimentPlotter(analysis_list)
    plotter.plot(targets, anchors, x_axis, y_axis, show_fig=False, **kwargs)
