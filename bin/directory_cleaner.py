# For arguments passed to library if name = main
import sys
# For unpacking data using pickle and looking through directories with glob,
# copying files with shutil
import pickle, glob, shutil
import numpy as np
import pandas as pd

import data_cleaner as dc


# 
#  If this file is run from the commpand line, the following is how to run it.
#  Here, source directory is where the files are in and destination is where
#  the selected ones will go. 
# 
# For now, the selected ones are those that are clean.
#
# Example: python directory_cleaner.py "../Data/All-Caltech/" "output"
Usage = " \n Usage: python %s source_directory output_filename" % sys.argv[0]

ex_dir = "../Data/All-Caltech/"
# ex_file = "0003020330_2017-12-21-12-56-50.pkl" 

# Exceptions
class InvalidArgs(Exception) : pass
class InvalidDirectory(InvalidArgs): pass


## Input and Output functions

# Load and returns object that was packaged with pickle
# This is taking a lot of time.
def load_obj(file_source):
    # "with" assures that the file will be closed properly
    with open(file_source, 'rb') as file:
        data = pickle.load(file)
    return data

# Loads a charging session as a tab-delimited text file
def load_txt(file_source):
    data = pd.read_csv(file_source, sep='\t')
    import datetime
    to_time = lambda x: datetime.datetime.strptime(x, "%Y-%m-%d-%H-%M-%S")
    timeForm = data['time'].apply(to_time)
    data['time'] = pd.to_datetime(timeForm)
    data.set_index('time', inplace=True)
    return data

# Returns tuple of a list of filenames and dataframes in a given directory
# matching charging profiles
def get_files(directory=ex_dir):
    # Filename regex
    location_id = "00030"
    station_id = "10101"
    month = "2018-01-"
    day = "09-"
    time = "*"
    filename = location_id + station_id + "_" + month + day + time + ".*"
    path_regx = directory + filename

    # All files matching regex path
    files = glob.glob(path_regx)
    if files == []: raise InvalidDirectory

    # Figure out type of data. Pickled if file extension is "pkl".
    # Example filename where last element is file extension.
    ex_file_list = files[0].split('.')
    if ex_file_list[-1] == "pkl":
        pickled = True
    else:
        pickled = False

    dfs = []

    # Check each file and add to invalids list
    for pathname in files:
        if pickled: df = load_obj(pathname)
        else: df = load_txt(pathname)
        dfs.append(df)
    
    return (files, dfs)
        

# Creates an excel document with fileneame in directory with sheet 'Data' of the
# given dataframe df.
def df_to_excel(df, filename, directory = "../Output"):
    writer = pd.ExcelWriter(directory+"/"+filename+'.xlsx')
    df.to_excel(writer, 'Data')
    writer.save()

# Doesn't work yet. The goal would be to make this automatic.
# Given a path name and a new pathname, uses 'path' as a template and
# opens/creates/returns a pandas ExcelWriter with the template.
# def excel_template_writer(filename, new_directory="../Output/", \
 #                         template_path="../Output/Template.xlsx"):
 #   from openpyxl import load_workbook
 #   # Duplicate the template
 #   #shutil.copyfile(template_path, new_directory + filename)
 #   # Load the template
 #   template = load_workbook("../Output/Template.xlsx")
 #   # Create the writer
 #   #writer = pd.ExcelWriter(new_directory + filename + ".xlsx", engine = 'openpyxl')
 #   # Put template in writer
 #   #writer.book = template
 #   return 1


# Returns tuple of (bool, error) where bool is True if data is clean and False
# otherwise. error indicates the reason for bool.
def is_clean_df(df):
    data = dc.df_to_entry(df)
    is_clean = dc.is_clean(data)
    return is_clean
    
# Outputs dataframe of station info. 'id' is index. Also has 'type', 'max_mA',
# 'fallback_mA', 'site'
def stations_info_df(filenames = ["_acs_lut.txt"], data_directory = "../Data/"):
    if filenames == []: raise ValueError( "No files specified" )
    infos = [] 
    for filename in filenames:
        data_curr = pd.read_csv(data_directory+filename, sep='\t')
        infos.append(data_curr)
    if len(infos) == 1 :
        infos[0].set_index('id', inplace=True)
        return infos[0]
    else:
        all_data = pd.concat(infos)
        all_data = all_data.drop_duplicates(subset = 'id')
        all_data.set_index('id', inplace=True)
        return all_data

## Functions to pass to clean_directory.
# Takes a dataframe, returns a list with values or None if no data 
# should be appended. 
# Has attribute 'cols' which is list of strings corresponding to the non-None
# return value.

# Returns a list with values corresponding to:
# [error : string, is_valid : bool]
# according to data_cleaner.clean_data.
# error is one of:
# ShortTime, LostDatapoints, LittleEnergyUsed, PowerTooLow
def clean_df(df):
    validity = is_clean_df(df)
    return [validity[1], validity[0]]
# Corresponding to clean_df. Name of data returned
clean_df.cols = ['error', 'is_valid']

# Checks if a dataframe has a long duration, if so, return length. Else None.
def long_df(df):
    data = dc.df_to_entry(df)
    if data.endTime - data.startTime > np.timedelta64(10, 'h'):
        return [data.endTime - data.startTime]
    else: return None
long_df.cols = ['length']

# Checks most information available
def datapoint_length_vals(df):
    data = dc.df_to_entry(df)
    tests = (lambda data: dc.session_length(data) / np.timedelta64(1, 'h'),
             lambda data: dc.average_gap(data) / np.timedelta64(1, 's'),
             lambda data: dc.max_gap(data) / np.timedelta64(1, 'm'),
             lambda data: data.energyDemand)
    results = list(dc.clean_data(data, other_tests = tests))
    return results
# Corresponding to datapoint_length_vals. Name of data returned.
datapoint_length_vals.cols = ['is_valid', 'error', \
                              'length (hr)', 'average_gap (s)', \
                              'max_gap (min)', 'energy (AV)']

# Checks information relevant to large and problematic gaps
def gap_vals(df):
    data = dc.df_to_entry(df)
    tests = (lambda data: dc.session_length(data) / np.timedelta64(1, 'h'),
             lambda data: dc.max_gap(data, more_info = True),
             lambda data: data.energyDemand)
    results = list(dc.clean_data(data, other_tests = tests))
    
    # Deal with gap tuple
    gap_info = results[3]
     # Convert gap length to minute
    results[3] = gap_info[0] / np.timedelta64(1, 'm')
    results.append(gap_info[2])
        
    return results
# Corresponding to datapoint_length_vals. Name of data returned.
gap_vals.cols = ['is_valid', 'error', 'session_length (hr)',
                              'max_gap (min)', 'energy (AV)', 'time_max_gap']

# Helper for clean_directory
# Given 0003020330_2017-12-21-12-56-50.pkl returns 
# ['0003020330', '2017', '12', '21', '12', '56', '50']
def filename_to_list(pathname, directory_len, extension_len, extra_len = 0):
    filename = pathname[directory_len + extra_len : -extension_len]
    import re
    return re.split('_|-|\.', filename)[:-1]

# Usage: clean_directory
# directory: source directory
# check_fun: function that takes a dataframe and filename
#            Returns a list of values to be added. Has attribute cols.
#
# .pkl files will be processed as pickled dataframes. 
# Other file types will be processed as tab-delimited csv or text files.
def clean_directory(directory=ex_dir, \
                    check_fun = clean_df):
    
    # Station info
    station_df = stations_info_df(filenames = ["_acs_lut.txt",
                                              "_acs_lut2.txt",
                                              "_acs_lut3.txt"])
    station_cols = ['station_type', 'site']

    # Filename regex
    location_id = "000*0"
    station_id = "*"
    month = "201*-*-"
    day = "*-"
    time = "*"
    filename = location_id + station_id + "_" + month + day + time + ".*"
    path_regx = directory + filename

    # All files matching regex path
    files = glob.glob(path_regx)
    if files == []: raise InvalidDirectory

    # Figure out type of data. Pickled if file extension is "pkl".
    # Example filename where last element is file extension.
    ex_file_list = files[0].split('.')
    if ex_file_list[-1] == "pkl":
        pickled = True
    else:
        pickled = False

    # For future reference
    dir_len = len(directory)
    ext_len = len(ex_file_list[-1])
    extra_len = 0

    # Return array of invalid data 
    invalids = []

    # Check each file and add to invalids list
    for pathname in files:
        if pickled: df = load_obj(pathname)
        else: df = load_txt(pathname)
        
        # Filename as list
        name_list = filename_to_list(pathname, dir_len, ext_len, extra_len)
        # To ints, instead of strings
        name_list = list(map(int, name_list))

        # Station info
        # Assumes first element is station id.
        try:
            station_info = list(station_df.loc[name_list[0], ['type', 'site']])
        # Only used if not found in station info file
        except KeyError:
            n = int(name_list[0] / 10 ** 6)
            if n == 2: site = "JPL"
            elif n == 3: site = "Caltech"
            elif n == 6: site = "MVLA"
            else: site = "NaN"
            station_info = ["NaN", site]

        # New data to append
        append_val = check_fun(df)

        if append_val != None:
            invalids.append(append_val + station_info + name_list + [pathname])

    return pd.DataFrame(\
            invalids, \
            columns = check_fun.cols + \
                      station_cols + \
                      ['station_id', 'year', 'month', 'day', \
                       'hour', 'min', 'sec', 'path'])


def main():
    # Verify the correct number of arguments were passed, deal with them
    if len(sys.argv) == 3:
        import datetime
        # Deal with passed arguments
        # Source directory, ensure ends with a "/"
        source = sys.argv[1]
        if source[-1] != "/": source += "/"
        # Output filename
        new_filename = sys.argv[2] 
        print("\nChecking all files in: %s\n" % source)
        start = datetime.datetime.now()

        invalids = clean_directory(source, datapoint_length_vals)
        try:
            df_to_excel(invalids, new_filename)
        except PermissionError:
            input("Please verify the output file is not open, then press Enter")
            df_to_excel(invalids, new_filename)
        time_taken = (datetime.datetime.now() - start).seconds
        minutes = int(time_taken / 60) # minutes
        seconds = time_taken - minutes * 60
        print("Clean Complete in %.0f min, %.0f sec, in %s.xlsx.\n" % (minutes, seconds, new_filename))
    else: raise InvalidArgs( Usage )

    


if __name__ == "__main__":
    main()
