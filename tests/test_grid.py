import pytest

from tuneconfig.grid import TrialGrid


@pytest.fixture(scope="module")
def grid(analysis_list):
    return TrialGrid(*analysis_list)


def test_grid_select_empty(grid):
    anchors = []
    rslt = grid.select(anchors)
    assert rslt is grid
    assert hasattr(grid, "_trials")
    assert isinstance(grid._trials, dict)
    assert len(grid._trials) == len(grid.analyses)


def test_grid_select_single_anchor(grid):
    anchors = ["batch_size=32"]
    rslt = grid.select(anchors)
    assert rslt is grid
    assert hasattr(grid, "_trials")
    assert isinstance(grid._trials, dict)
    assert len(grid._trials) == len(grid.analyses)
    assert all(len(trials) == 6 for trials in grid._trials.values())


def test_grid_select_multiple_anchors(grid):
    anchors = ["batch_size=32", "optimizer=RMSProp"]
    rslt = grid.select(anchors)
    assert rslt is grid
    assert hasattr(grid, "_trials")
    assert isinstance(grid._trials, dict)
    assert len(grid._trials) == len(grid.analyses)
    assert all(len(trials) == 2 for trials in grid._trials.values())


def test_grid_single_target_no_axes(grid, cfg_single_target_no_axes):
    targets, x_axis, y_axis, anchors = cfg_single_target_no_axes
    trial_grid = grid.select(anchors).build(targets, x_axis, y_axis)
    assert grid.shape == (1, 1)
    assert len(trial_grid[None][None]) == len(grid.analyses)


def test_grid_multiple_targets_no_axes(grid, cfg_multiple_targets_no_axes):
    targets, x_axis, y_axis, anchors = cfg_multiple_targets_no_axes
    trial_grid = grid.select(anchors).build(targets, x_axis, y_axis)
    assert grid.shape == (1, 1)
    assert len(trial_grid[None][None]) == len(grid.analyses)
    assert all(len(metrics[-1]) == len(targets) for metrics in trial_grid[None][None])


def test_grid_single_target_multiple_plots_no_axes(grid, cfg_single_target_multiple_plots_no_axes):
    targets, x_axis, y_axis, anchors = cfg_single_target_multiple_plots_no_axes
    trial_grid = grid.select(anchors).build(targets, x_axis, y_axis)
    assert grid.shape == (1, 1)
    assert len(trial_grid[None][None]) == 3 * len(grid.analyses)


def test_grid_multiple_targets_multiple_plots_no_axes(grid, cfg_multiple_targets_multiple_plots_no_axes):
    targets, x_axis, y_axis, anchors = cfg_multiple_targets_multiple_plots_no_axes
    trial_grid = grid.select(anchors).build(targets, x_axis, y_axis)
    assert grid.shape == (1, 1)
    assert len(trial_grid[None][None]) == 3 * len(grid.analyses)
    assert all(len(metrics[-1]) == len(targets) for metrics in trial_grid[None][None])


def test_grid_single_target_x_axis(grid, cfg_single_target_x_axis):
    targets, x_axis, y_axis, anchors = cfg_single_target_x_axis
    trial_grid = grid.select(anchors).build(targets, x_axis, y_axis)
    assert grid.shape == (1, 3)
    assert all(len(plots) == len(grid.analyses) for plots in trial_grid[None].values())


def test_grid_multiple_targets_x_axis(grid, cfg_multiple_targets_x_axis):
    targets, x_axis, y_axis, anchors = cfg_multiple_targets_x_axis
    trial_grid = grid.select(anchors).build(targets, x_axis, y_axis)
    assert grid.shape == (1, 3)
    assert all(len(plots) == len(grid.analyses) for plots in trial_grid[None].values())
    assert all(
        len(metrics[-1]) == len(targets)
        for plots in trial_grid[None].values()
        for metrics in plots
    )


def test_grid_single_target_y_axis(grid, cfg_single_target_y_axis):
    targets, x_axis, y_axis, anchors = cfg_single_target_y_axis
    trial_grid = grid.select(anchors).build(targets, x_axis, y_axis)
    assert grid.shape == (3, 1)
    assert all(
        len(plots) == len(grid.analyses)
        for y_values in trial_grid.keys()
        for plots in trial_grid[y_values].values()
    )


def test_grid_multiple_targets_y_axis(grid, cfg_multiple_targets_y_axis):
    targets, x_axis, y_axis, anchors = cfg_multiple_targets_y_axis
    trial_grid = grid.select(anchors).build(targets, x_axis, y_axis)
    assert grid.shape == (3, 1)
    assert all(
        len(plots) == len(grid.analyses)
        for y_values in trial_grid.keys()
        for plots in trial_grid[y_values].values()
    )
    assert all(
        len(metrics[-1]) == len(targets)
        for y_values in trial_grid.keys()
        for plots in trial_grid[y_values].values()
        for metrics in plots
    )


def test_grid_single_target_both_axis(grid, cfg_single_target_both_axis):
    targets, x_axis, y_axis, anchors = cfg_single_target_both_axis
    trial_grid = grid.select(anchors).build(targets, x_axis, y_axis)
    assert grid.shape == (2, 3)
    assert all(
        len(plots) == len(grid.analyses)
        for y_values in trial_grid.keys()
        for plots in trial_grid[y_values].values()
    )


def test_grid_multiple_targets_both_axis(grid, cfg_multiple_targets_both_axis):
    targets, x_axis, y_axis, anchors = cfg_multiple_targets_both_axis
    trial_grid = grid.select(anchors).build(targets, x_axis, y_axis)
    assert grid.shape == (2, 3)
    assert all(
        len(plots) == len(grid.analyses)
        for y_values in trial_grid.keys()
        for plots in trial_grid[y_values].values()
    )
    assert all(
        len(metrics[-1]) == len(targets)
        for y_values in trial_grid.keys()
        for plots in trial_grid[y_values].values()
        for metrics in plots
    )
