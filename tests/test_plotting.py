import pytest

from tuneconfig.plotting import ExperimentPlotter


def test_plot_single_target_no_axis(analysis):
    targets = ["metric:test"]
    anchors = ["batch=32", "lr=0.01"]
    kwargs = {
        "plot_type": "line",
        "target_x_axis_label": "Epochs",
        "target_y_axis_label": "Values",
    }

    plotter = ExperimentPlotter(analysis)
    plotter.plot(targets, anchors, show_fig=False, **kwargs)


def test_plot_multiple_targets_no_axis(analysis):
    targets = ["data:foo", "data:bar", "data:baz"]
    anchors = ["batch=32", "lr=0.01"]
    kwargs = {
        "plot_type": "line",
        "target_x_axis_label": "Epochs",
        "target_y_axis_label": "Values",
    }

    plotter = ExperimentPlotter(analysis)
    plotter.plot(targets, anchors, show_fig=False, **kwargs)


def test_plot_single_target_both_axis(analysis):
    targets = ["metric:test"]
    anchors = ["batch=32"]
    x_axis, y_axis = "optimizer", "learning_rate"
    kwargs = {
        "plot_type": "line",
        "target_x_axis_label": "Epochs",
        "target_y_axis_label": "Values",
    }

    plotter = ExperimentPlotter(analysis)
    plotter.plot(targets, anchors, x_axis, y_axis, show_fig=False, **kwargs)


def test_plot_multiple_targets_both_axis(analysis):
    targets = ["data:foo", "data:baz"]
    anchors = ["batch=32"]
    x_axis, y_axis = "optimizer", "learning_rate"
    kwargs = {
        "plot_type": "line",
        "target_x_axis_label": "Epochs",
        "target_y_axis_label": "Values",
    }

    plotter = ExperimentPlotter(analysis)
    plotter.plot(targets, anchors, x_axis, y_axis, show_fig=False, **kwargs)


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
        "target_y_axis_label": "Cumulative Reward",
    }

    plotter = ExperimentPlotter(analysis)
    plotter.plot(targets, anchors, x_axis, y_axis, show_fig=False, **kwargs)


def test_plot_bar_multiple_analysis(analysis_list):
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
