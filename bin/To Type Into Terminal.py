python directory_cleaner.py "../Data/All-Caltech" output

from directory_cleaner import *
import data_cleaner as dc
import pickle
import pandas as pd
import numpy as np
ex_dir = "../Data/Charging-Sessions/"
ex_file = "0003020330_2017-12-21-12-56-50.pkl"
file_source=ex_dir+ex_file
with open(file_source, 'rb') as file:
        df = pickle.load(file)

data = dc.df_to_entry(df)
times = dc.max_gap(data)

a=[pd.Timestamp('2017-12-21 21:44:13.173865975'),pd.Timestamp('2018-12-21 21:44:18.299998632')]

from directory_cleaner import *
a = stations_info_df(filenames = ["_acs_lut.txt"])
b = stations_info_df(filenames = ["_acs_lut.txt", "_acs_lut2.txt"])

import visualize as v
a= ["../Data/All-Caltech\\0003010101_2018-02-18-23-27-48.pkl",
"../Data/All-Caltech\\0003010102_2018-02-18-23-27-48.pkl",
"../Data/All-Caltech\\0003010103_2018-02-18-23-27-48.pkl",
"../Data/All-Caltech\\0003010104_2018-02-18-23-27-48.pkl",
"../Data/All-Caltech\\0003010105_2018-02-18-23-27-48.pkl",
"../Data/All-Caltech\\0003010106_2018-02-18-23-27-48.pkl",
"../Data/All-Caltech\\0003010108_2018-02-18-23-27-48.pkl",
"../Data/All-Caltech\\0003010217_2018-02-18-23-27-48.pkl",
"../Data/All-Caltech\\0003010222_2018-02-18-23-27-48.pkl",
"../Data/All-Caltech\\0003010223_2018-02-18-23-27-48.pkl",
"../Data/All-Caltech\\0003010224_2018-02-18-23-27-48.pkl",
"../Data/All-Caltech\\0003010525_2018-02-18-23-27-48.pkl",
"../Data/All-Caltech\\0003010526_2018-02-18-23-27-48.pkl",
"../Data/All-Caltech\\0003010627_2018-02-18-23-27-48.pkl",
"../Data/All-Caltech\\0003010628_2018-02-18-23-27-48.pkl",
"../Data/All-Caltech\\0003010733_2018-02-18-23-27-48.pkl",
"../Data/All-Caltech\\0003010834_2018-02-18-23-27-48.pkl",
"../Data/All-Caltech\\0003010910_2018-02-18-23-27-48.pkl",
"../Data/All-Caltech\\0003010935_2018-02-18-23-27-48.pkl",
"../Data/All-Caltech\\0003011032_2018-02-18-23-27-48.pkl"]

v.plot_sessions(a, save=True)




import directory_cleaner as dir_c
import visualize as v
import matplotlib.pyplot as plt
ex_dir = "../Data/Charging-Sessions/"
df = dir_c.load_obj(ex_dir+"0003020330_2017-07-21-14-36-08.pkl")
v.plot_profile(df)
plt.show()


import directory_cleaner as dir_c
ex_dir = "../Data/Charging-Sessions/"
invalids = dir_c.invalids_in_dir(ex_dir)
invalids
dir_c.df_to_excel(invalids, "All Sessions, 10 min cutoff, .8 Datapoint")


import directory_cleaner as dir_c
ex_dir = "../Data/ChargeSessions2/"
invalids = dir_c.invalids_in_dir(ex_dir, pickled = False)
invalids
dir_c.df_to_excel(invalids, "From Website, All2, 10min, .8 Data 2")



dir_c.df_to_excel(invalids, "All Sessions, 10 min cutoff, .8 Datapoint")

import directory_cleaner as dir_c
longs = dir_c.long_sessions()


file_source = "../Data/ChargeSessions2/0002010101_2017-05-12-17-04-31.txt"
import pandas as pd
data = pd.read_csv(file_source, sep='\t')

import pickle, glob
pickled = False
directory = "../Data/ChargeSessions2/"
# 2 should be a 3 when pickled. 2 when from text. TODO
id_caltech = "00020"
station_id = "*"
month = "2017-05-"
day = "*12-"
time = "*"
filename = id_caltech + station_id + "_" + month + day + time + ".txt"
path_regx = directory + filename
dir_len = len(directory)
extra_len = len(id_caltech)
ext_len = len('txt')
for pathname in glob.glob(path_regx):
        if pickled: df = load_obj(pathname)
        else: df = load_txt(pathname)
        print(df)
        data = dc.df_to_entry(df)


# See one day:
exit()
python
import visualize as v
import directory_cleaner as dir_c
filenames, dfs = dir_c.get_files()
plt.ax.set_xlim(df.index[0], df.index[-1])
for df in dfs:
        v.plot_profile(df, scatter=True)

v.plt.show()

exit()
python
import directory_cleaner as dir_c
dir_c.excel_template_writer("test")

location_id = "00030"
station_id = "10101"
month = "2018-01-"
day = "09-"
time = "*"
filename = location_id + station_id + "_" + month + day + time + ".*"
path_regx = directory + filename

# All files matching regex path
files = glob.glob(path_regx)
