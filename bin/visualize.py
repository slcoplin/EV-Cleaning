import data_cleaner as dc
import directory_cleaner as dir_c
import matplotlib.pyplot as plt
import glob
# For more interactive plotting
# Need to install this and IPython
from pivottablejs import pivot_ui
# Bokeh doesn't look bad.
 
# Not close to exhaustive
station_ids = ["020320","020321","020322","020324","020326","020327","020330"]

# Plots a dataframe's 'mamps_last' column against its index which is a time.
def plot_profile(profile, scatter = False):
    if not scatter:
        return profile['mamps_last'].plot()
    else:
        return plt.scatter(profile.index, profile['mamps_last'])
        #profile.plot.scatter(x='ind', y='mamps_last')

# Plot all profiles for a station, may not be complete
def plot_station(directory, station_id):
    # File path
    id_caltech = "0003"
    month = "*"
    day = "*-"
    time = "*"
    filename = id_caltech + station_id + "_" + month + day + time + ".pkl"
    path_regx = directory + filename

    # Plot each file matching path_regx
    handles = []
    names = []
    for pathname in glob.glob(path_regx):
        df = dir_c.load_obj(pathname)
        data = dc.df_to_entry(df)
        reason = dc.clean_data(data, more_info = True)[1]
        if reason == dc.ShortTime: 
            plt.figure(1)
            handle = plot_profile(df)
        else:
            plt.figure(2)
            handle = plot_profile(df)
        handles.append(handle)
        names.append(pathname)
    plt.legend(handles, names)
    plt.show()

# Plot all pickled (.pkl) profiles in a given list of pathnames with locations there
def plot_sessions(profile_pathnames, save = False):
    for pathname in profile_pathnames:
        df = dir_c.load_obj(pathname)
        data = dc.df_to_entry(df)
        plot_profile(df)
        destination = "../Output/Profiles/"
        if save:
            plt.savefig(destination + "plotted_" + pathname[21:-4] + ".png", \
                        bbox_inches='tight')
            plt.clf()
        else: plt.show()

# Incomplete.
# Gives dataframe and plots grouped bar chart where main groups are group and
# colored bars represent subgroup. group and subgroup are column names for the
# dataframe.
def plot_subgroups(data, group, subgroup):
    grouped = dir_c.group_invalids(data, group, subgroup)
    # Plotting the bars
    fig_width = 10.
    # fig, ax = plt.subplots(figsize=(fig_width,5))

    
    group_options = grouped[group].unique()

    # nbars = grouped.shape[0]
    # group_width = 0.9 * fig_width / len(group_options)
    for option in group_options:
        subgroup = grouped.loc[grouped[group] == option]
        # subgroup_width = group_width / len(subgroup)
        plt.bar()
    grouped.plot.bar()

def plot_dataframe(df):
    pivot_ui(df)