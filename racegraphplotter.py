import fastf1
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import fastf1.plotting as ff1plt
import seaborn as sns

class RacePlot:

    def __init__(self, year, round):
        fastf1.Cache.enable_cache('/Users/viggnah/Documents/fastf1-cache')
        # fastf1.plotting.setup_mpl()
        self.setup_graph_properties()
        self.year = year
        self.round = round
        self.race = fastf1.get_session(year, round, 'race')
        self.race.load()

        self.race_winner = self.get_race_winner()
        self.lap_start_times_winner = self.get_lap_start_times_for_driver(self.race_winner)
        self.no_of_laps = len(self.lap_start_times_winner) + 1
        self.lap_no = np.arange(1, self.no_of_laps+1, 1)

    def setup_graph_properties(self):
        sns.set_style('darkgrid') # darkgrid, white grid, dark, white and ticks
        plt.rc('axes', titlesize=18)     # fontsize of the axes title
        plt.rc('axes', labelsize=14)    # fontsize of the x and y labels
        plt.rc('xtick', labelsize=13)    # fontsize of the tick labels
        plt.rc('ytick', labelsize=13)    # fontsize of the tick labels
        plt.rc('legend', fontsize=13)    # legend fontsize
        plt.rc('font', size=13)          # controls default text sizes
        plt.rcParams['axes.xmargin'] = 0
    
    def get_race_winner(self, ):
        print("The race winner was {0}!".format(self.race.results.Abbreviation[0]))
        return self.race.results.Abbreviation[0]

    def get_lap_time_list_for_driver_in_position_x(self, x):
        driver_name = self.race.results.Abbreviation[x-1]
        print("Picking lap times for " + driver_name)
        drivers_laps = self.race.laps.pick_driver(driver_name)['LapTime']
        drivers_laps = drivers_laps[1:]
        print(type(drivers_laps))
        return drivers_laps

    def plot_race_gap_for_driver_list(self, driver_list):
        fig, self.ax = plt.subplots(figsize=(15, 10), tight_layout=True)

        self.plot_race_winner_base_line()
        for driver in driver_list:
            self.plot_race_gap_for_one_driver(driver)

        formatter = matplotlib.ticker.FuncFormatter(lambda ms, x: ms/1000)
        self.ax.yaxis.set_major_formatter(formatter)
        self.ax.set_xlabel('Lap Number')
        self.ax.set_ylabel('Gap to P1 (s)')
        self.ax.set_title('Race Gap in the {0}'.format(self.race.event.EventName))
        self.ax.legend()
        # plt.show()
        return fig
            
    def plot_race_winner_base_line(self, ):
        base_line = [0] * self.no_of_laps
        self.ax.plot(self.lap_no, base_line, label=self.race_winner+' (P1)', color=ff1plt.driver_color(self.race_winner))

    def plot_race_gap_for_one_driver(self, driver_abbr):
        driver_finished_race = True
        if driver_abbr == self.race_winner:
            return
        lap_start_times_driver = self.get_lap_start_times_for_driver(driver_abbr)
        if len(lap_start_times_driver) < len(self.lap_start_times_winner):
            driver_finished_race = False
            nan_list = [np.nan] * (len(self.lap_start_times_winner) - len(lap_start_times_driver))
            lap_start_times_driver.extend(nan_list)

        driver_pace = self.calc_running_gap_to_leader(lap_start_times_driver, self.lap_start_times_winner)
        if driver_finished_race:
            final_lap_time_diff = np.timedelta64(list(self.race.laps.pick_driver(driver_abbr)['LapTime'])[-1]-list(self.race.laps.pick_driver(self.race_winner)['LapTime'])[-1], 'ms')
            driver_pace.append(driver_pace[-1] + final_lap_time_diff)
        else:
            driver_pace.append(np.nan)
        print(driver_pace)
        self.ax.plot(self.lap_no, driver_pace, label=driver_abbr, color=ff1plt.driver_color(driver_abbr), marker='o')

    def get_lap_start_times_for_driver(self, driver_abbr):
        print("Picking lap start times for " + driver_abbr)
        driver_lap_start_times = self.race.laps.pick_driver(driver_abbr)['LapStartTime']
        driver_lap_start_times = [np.nan if pd.isnull(time) else np.timedelta64(time, 'ms') for time in driver_lap_start_times]
        return driver_lap_start_times
    
    def calc_running_gap_to_leader(self, driver_times, leader_times):
        return [driver_time - leader_time 
                if not(np.isnan(driver_time) or np.isnan(leader_time)) 
                else np.nan 
                for driver_time, leader_time in zip(driver_times, leader_times)]

    def get_lap_start_times_for_driver_in_position_x(self, x):
        driver_name = self.race.results.Abbreviation[x-1]
        print("Picking lap start times for " + driver_name)
        driver_lap_start_times = self.race.laps.pick_driver(driver_name)['LapStartTime']
        driver_lap_start_times = [np.nan if pd.isnull(time) else np.timedelta64(time, 'ms') for time in driver_lap_start_times]
        return driver_lap_start_times

    def get_cumulative_time_for_position_x(self, x):
        drivers_laps = self.get_lap_time_list_for_driver_in_position_x(x)
        cmlt_time = np.timedelta64('0', 'ns')
        for lap in drivers_laps:
            if not pd.isna(lap):
                cmlt_time += lap
        return cmlt_time
        