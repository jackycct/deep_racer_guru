import tkinter as tk
import numpy as np
from scipy import stats

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.gridspec import GridSpec
from matplotlib.axes import Axes

from src.analyze.graph.graph_analyzer import GraphAnalyzer
from src.utils.lists import get_list_of_empty_lists

from src.episode.episode import Episode

AXIS_DISTANCE = 1
AXIS_PEAK_TRACK_SPEED = 2
AXIS_STARTING_POINT = 3
AXIS_AVERAGE_REWARD = 4
AXIS_TOTAL_REWARD = 5
AXIS_SMOOTHNESS = 6
AXIS_ITERATION = 7
AXIS_FLYING_START = 8




class AnalyzeLapTimeCorrelations(GraphAnalyzer):

    def __init__(self, guru_parent_redraw, matplotlib_canvas :FigureCanvasTkAgg, control_frame :tk.Frame):

        super().__init__(guru_parent_redraw, matplotlib_canvas, control_frame)

        self.show_all = tk.BooleanVar()
        self.show_filtered = tk.BooleanVar(value="True")

        self.correlation_tk_var = tk.IntVar(value = AXIS_DISTANCE)

        self.swap_axes = tk.BooleanVar()


    def build_control_frame(self, control_frame):

        episodes_group = tk.LabelFrame(control_frame, text="Episodes", padx=5, pady=5)
        episodes_group.grid(column=0, row=0, pady=5, padx=5)

        tk.Checkbutton(
            episodes_group, text="All",
            variable=self.show_all,
            command=self.guru_parent_redraw).grid(column=0, row=0, pady=5, padx=5)

        tk.Checkbutton(
            episodes_group, text="Filtered",
            variable=self.show_filtered,
            command=self.guru_parent_redraw).grid(column=0, row=1, pady=5, padx=5)

        #####

        axis_group = tk.LabelFrame(control_frame, text="Correlate With", padx=5, pady=5)
        axis_group.grid(column=0, row=2, pady=5, padx=5)

        tk.Radiobutton(axis_group, text="Total Distance", variable=self.correlation_tk_var,
            value=AXIS_DISTANCE, command=self.guru_parent_redraw).grid(column=0, row=0, pady=2, padx=5)

        tk.Radiobutton(axis_group, text="Peak Track Speed", variable=self.correlation_tk_var,
                       value=AXIS_PEAK_TRACK_SPEED, command=self.guru_parent_redraw).grid(column=0, row=1, pady=2, padx=5)

        tk.Radiobutton(axis_group, text="Starting Point", variable=self.correlation_tk_var,
                       value=AXIS_STARTING_POINT, command=self.guru_parent_redraw).grid(column=0, row=2, pady=2, padx=5)

        tk.Radiobutton(axis_group, text="Average Reward", variable=self.correlation_tk_var,
                       value=AXIS_AVERAGE_REWARD, command=self.guru_parent_redraw).grid(column=0, row=3, pady=2, padx=5)

        tk.Radiobutton(axis_group, text="Total Reward", variable=self.correlation_tk_var,
                       value=AXIS_TOTAL_REWARD, command=self.guru_parent_redraw).grid(column=0, row=4, pady=2, padx=5)

        tk.Radiobutton(axis_group, text="Smoothness", variable=self.correlation_tk_var,
                       value=AXIS_SMOOTHNESS, command=self.guru_parent_redraw).grid(column=0, row=5, pady=2, padx=5)

        tk.Radiobutton(axis_group, text="Training Iteration", variable=self.correlation_tk_var,
                       value=AXIS_ITERATION, command=self.guru_parent_redraw).grid(column=0, row=6, pady=2, padx=5)

        tk.Radiobutton(axis_group, text="Flying Start", variable=self.correlation_tk_var,
                       value=AXIS_FLYING_START, command=self.guru_parent_redraw).grid(column=0, row=7, pady=2, padx=5)

        ######

        format_group = tk.LabelFrame(control_frame, text="Format", padx=5, pady=5)
        format_group.grid(column=0, row=3, pady=5, padx=5)

        tk.Checkbutton(
            format_group, text="Swap Axes",
            variable=self.swap_axes,
            command=self.guru_parent_redraw).grid(column=0, row=0, pady=5, padx=5)


    def add_plots(self):
        axes: Axes = self.graph_figure.add_subplot()

        if self.show_all.get():
            self.plot_episodes(axes, self.all_episodes, "C1", "All")

        if self.show_filtered.get():
            self.plot_episodes(axes, self.filtered_episodes, "C2", "Filtered")

        self.format_axes(axes)

    def plot_episodes(self, axes: Axes, episodes: list, colour, label):

        if not episodes:
            return

        plot_y = []

        if self.correlation_tk_var.get() == AXIS_DISTANCE:
            plot_y = get_plot_data_distances(episodes)
        if self.correlation_tk_var.get() == AXIS_PEAK_TRACK_SPEED:
            plot_y = get_plot_data_peak_speeds(episodes)
        if self.correlation_tk_var.get() == AXIS_STARTING_POINT:
            plot_y = get_plot_data_starting_points(episodes)
        if self.correlation_tk_var.get() == AXIS_AVERAGE_REWARD:
            plot_y = get_plot_data_averge_rewards(episodes)
        if self.correlation_tk_var.get() == AXIS_TOTAL_REWARD:
            plot_y = get_plot_data_total_rewards(episodes)
        if self.correlation_tk_var.get() == AXIS_SMOOTHNESS:
            plot_y = get_plot_data_repeats(episodes)
        if self.correlation_tk_var.get() == AXIS_ITERATION:
            plot_y = get_plot_data_iterations(episodes)
        if self.correlation_tk_var.get() == AXIS_FLYING_START:
            plot_y = get_plot_data_flying_starts(episodes)

        plot_x = get_plot_data_lap_times(episodes)

        # Calculate linear regression line through the points

        slope, intercept, r, p, std_err = stats.linregress(plot_x, plot_y)
        def linear_line(x):
            return slope * x + intercept
        if abs(r) > 0.25:
            slope_y = list(map(linear_line, plot_x))
            r_label = "R = " + str(round(r, 2))
        else:
            (slope_y, r_label) = (None, None)


        # Finally plot the data we have gathered

        if self.swap_axes.get():
            axes.plot(plot_y, plot_x, "o", color=colour, label=label)
            if slope_y:
                axes.plot(slope_y, plot_x, color=colour, label=r_label)
        else:
            axes.plot(plot_x, plot_y, "o", color=colour, label=label)
            if slope_y:
                axes.plot(plot_x, slope_y, color=colour, label=r_label)


    def format_axes(self, axes :Axes):

        general_title = "???"
        axis_label = "???"

        if self.correlation_tk_var.get() == AXIS_DISTANCE:
            general_title = "Distance"
            axis_label = "Distance / metres"
        if self.correlation_tk_var.get() == AXIS_PEAK_TRACK_SPEED:
            general_title = "Peak Track Speed"
            axis_label = "Peak Speed / metres per second"
        if self.correlation_tk_var.get() == AXIS_STARTING_POINT:
            general_title = "Starting Point"
            axis_label = "Start Waypoint Id"
        if self.correlation_tk_var.get() == AXIS_AVERAGE_REWARD:
            general_title = "Average Reward Per Step"
            axis_label = general_title
        if self.correlation_tk_var.get() == AXIS_TOTAL_REWARD:
            general_title = "Total Reward"
            axis_label = general_title
        if self.correlation_tk_var.get() == AXIS_SMOOTHNESS:
            general_title = "Repeat Action Percent"
            axis_label = general_title
        if self.correlation_tk_var.get() == AXIS_ITERATION:
            general_title = "Training Iteration"
            axis_label = general_title
        if self.correlation_tk_var.get() == AXIS_FLYING_START:
            general_title = "Track Speed At One Second"
            axis_label = general_title

        axes.set_title("Lap Time Correlated With " + general_title)

        if self.swap_axes.get():
            axes.set_ylabel("Lap Time / Seconds")
            axes.set_xlabel(axis_label)
        else:
            axes.set_xlabel("Lap Time / Seconds")
            axes.set_ylabel(axis_label)

        if axes.has_data():
            axes.legend(frameon=True, framealpha=0.8, shadow=True)


def get_plot_data_distances(episodes :list):
    distances = []

    for e in episodes:
        if e.lap_complete:
            distances.append(e.distance_travelled)

    return np.array(distances)

def get_plot_data_peak_speeds(episodes :list):
    speeds = []

    for e in episodes:
        if e.lap_complete:
            speeds.append(e.peak_track_speed)

    return np.array(speeds)


def get_plot_data_lap_times(episodes: list):
    lap_times = []

    for e in episodes:
        if e.lap_complete:
            lap_times.append(e.time_taken)

    return np.array(lap_times)

def get_plot_data_starting_points(episodes: list):
    starts = []

    for e in episodes:
        if e.lap_complete:
            starts.append(e.events[0].closest_waypoint_index)

    return np.array(starts)

def get_plot_data_averge_rewards(episodes: list):
    rewards = []

    for e in episodes:
        if e.lap_complete:
            rewards.append(e.average_reward)

    return np.array(rewards)

def get_plot_data_total_rewards(episodes: list):
    rewards = []

    for e in episodes:
        if e.lap_complete:
            rewards.append(e.total_reward)

    return np.array(rewards)

def get_plot_data_repeats(episodes: list):
    repeats = []

    for e in episodes:
        if e.lap_complete:
            repeats.append(e.repeated_action_percent)

    return np.array(repeats)

def get_plot_data_iterations(episodes: list):
    iterations = []

    for e in episodes:
        if e.lap_complete:
            iterations.append(e.iteration)

    return np.array(iterations)

def get_plot_data_flying_starts(episodes: list):
    starts = []

    for e in episodes:
        if e.lap_complete:
            starts.append(e.flying_start_speed)

    return np.array(starts)

