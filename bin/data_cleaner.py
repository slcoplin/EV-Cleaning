
# Currently not true, Pint may be enabled later.: 
# Pint must be installed to use this library. Pint handles units, which 
# reduces errors. Documentation for Pint is https://pint.readthedocs.io/en/latest/.
# In this file, unit is shorthand for pint.UnitRegistry() which can be used to add
# units to numbers.
# 
# If this runs slowly, consider removing Pint and units. It will likely speed things
# up.
# 
# TODO: Install if not installed and use?
# To install run 'pip install pint' on Windows.
# 
# 
# 
# Functions in this file
# 
# clean_data (data,
#             more_info = False,
#             min_charge_time = np.timedelta64(2, 'm'),
#             min_datapoint_loss = 0.95,
#             min_energy = 1,
#             min_maxpower = 2000 / 208 
#             ) 
#             -> {True | False}
#   Takes 
#       data : Entry. Input data.
#       more_info : Bool. Decides output type.
#       min_charge_time : np.timedelta64. Minimum profile length to be valid.
#       max_time: np.timedelta64. Maximum profile length to be valid.
#       min_datapoint_loss : float. 
#           From 0 to 1. Minimum fraction of points available to be valid.
#       min_energy : float, W * hr. Minimum energy used to be valid.
#       min_maxpower : float, W. Power must get up to this level to be valid.
#       
#   Returns
#       If more_info: ({True | False}, Error, other_results*) 
#           True if the data is valid and False otherwise.
#           Where error indicates why invalid. Choices: 
#           ValidData, ShortTime, LongTime, LostDatapoints, LittleEnergyUsed, 
#           PowerTooLow
#           Where other_results is the output from other_tests
#       Else: {True | False}
#       
#
# df_to_entry (data) -> Entry
#   Takes a charging profile of type dataFrame and converts it to an instance  
#   of Entry with the following attributes:
#       startTime : a time in the form
#       endTime : a time in the form
#       energyDemand : an integer
#       chargingProfile: a numpy array of 2-tuples (time : int, power : float) 
#           that can be accessed as charginProfile['time'] and 
#           chargingProfile['power']
#   We may want to add info like
#       date
#       location
"""what about this"""
import numpy as np
# import Pint
# unit = Pint.UnitRegistry()

# Sec 1. Data Manager
class Entry:
    def __init__ (self, start, end, profile, demand, profile_fetch):
        self.startTime = start
        self.endTime = end
        self.energyDemand = demand
        self.profile = profile
        self.get_curr = lambda time: profile_fetch(time, self.profile)

"""this one"""
# Input: df : pandas DataFrame
#   Index: timestamps
#   mamps_last: current in mA
#   mamps_limit: 'limit' in mA
# Returns an instance of Entry with data from input.
def df_to_entry ( df ):
    """ Is this a docstring """
    start = df.index[0]
    end = df.index[-1]
    # For more with dataframes : https://www.shanelynn.ie/select-pandas-dataframe-rows-and-columns-using-iloc-loc-and-ix/
    # Assumes current is 0th column, and in mA
    # Demand in W*hr = A * V * hr. Assume 208 V.
    mA_to_A_V = 1/10000.0 * 208
    integral = np.trapz(df.iloc[:,0], df.index)
    hour = np.timedelta64(1, 'h')
    demand = integral / hour * mA_to_A_V

    profile_fetch = lambda time, profile: profile.loc[time][0]
    
    entry = Entry(start, end, df, demand, profile_fetch)
    return entry
    # Put chargingProfile into a nice form.
    # newDict[chargingProfile] = np.array([(_, _), (_, _)..], dtype=[('time', int), ('energy', float)])


# Sec 2. Cleaning functions and sub-functions

# Cleans given data and returns a tuple ({True | False}, ReasonCode)
# where ReasonCode has the options: 
# ValidData, ShortTime, LongTime, LostDatapoints, LittleEnergyUsed, PowerTooLow
# and returns True if the data is clean, False if out of bounds.
# 
# other_tests is a list of lambda functions that take data of the form Entry
# and returns some desired value which will be appended to the return tuple,
# one item per test. more_info must be set to True.
def clean_data( data, \
                more_info = False,  \
                min_charge_time = np.timedelta64(20, 'm'), \
                min_datapoint_loss = 0.9, \
                supposed_time_gap = np.timedelta64(10, 's'), \
                max_gap_allowed = np.timedelta64(1, 'm'), \
                min_energy = 1, \
                min_maxpower = 2000, \
                max_time = np.timedelta64(20, 'h'), \
                other_tests = False
                ):

    # Check charge period is long enough
    if not long_enough(data, min_charge_time): result = (False, ShortTime)
    
    elif not no_gap(data, max_gap_allowed): result = (False, BigGap)
    
    # Check if charge session is too long
    elif not short_enough(data, max_time): result = (False, LongTime)

    # Check the profile has enough data points (loss of datapoints)
    elif not enough_points(data, min_datapoint_loss, supposed_time_gap): result = (False, LostDatapoints)

    # Check the profile consumed enough energy
    elif not enough_energy_used(data, min_energy): result = (False, LittleEnergyUsed)

    # Check the profile had high enough maximum power
    elif not enough_power(data, min_maxpower): result = (False, PowerTooLow)

    # If all of the previous functions passed, then valid data.
    else: result = (True, ValidData)

    if not more_info: return result[0]
    else:
        # Other tests to do on an Entry
        if other_tests:
            others = []
            for test in other_tests:
                others.append(test(data))
            return result + tuple(others)
        else: 
            return result

# Sec 2.1. Sub-functions for clean_data

# Takes data and returns True if the charging profile spans more than or equal
# to min_time minutes. If min_time is 0, return True.
def long_enough (data, min_time):
    # Check initial case
    if min_time == 0: return True

    return (data.endTime - data.startTime) >= min_time

# Takes data and returns True if the charging profile spans less than or equal
# to max_time (as a numpy timedelta64).
def short_enough (data, max_time):
    return (data.endTime - data.startTime) <= max_time

def session_length (data):
    return data.endTime - data.startTime

# Takes data and a minumim proportion (0 to 1) and returns {True | False}
# If min_loss is 0, then return True.
# Find the proportion of points in a charging profile of the data to the total
# charging time in minutes [minutes? have bins? TODO\] and return True if
# higher than the cutoff, False otherwise.
def enough_points(data, min_loss, supposed_time_gap):
    # Check initial case
    if min_loss == 0: return True
    
    # Check if enough
    return datapoint_fraction(data, supposed_time_gap) > min_loss

def datapoint_fraction(data, supposed_time_gap = np.timedelta64(10, 's')):
     # Actual # of points
    numPoints = data.profile.shape[0] # Number of rows. Assumes a dataframe.
    # Theoretical # of points
    profileTime = data.endTime - data.startTime
    if profileTime == np.timedelta64(0, 's'): return 1
    # Some sessions had >1, so ignore for now.
    return min (numPoints / (profileTime / supposed_time_gap), 1)

# Returns a np.timedelta64
def average_gap(data):
     # Actual # of points
    numPoints = data.profile.shape[0] # Number of rows. Assumes a dataframe.
    # Theoretical # of points
    profileTime = data.endTime - data.startTime
    if profileTime == np.timedelta64(0, 's'): return profileTime
    ave_gap = np.timedelta64(profileTime / numPoints)
    return ave_gap

# Takes data : Entry and a max_gap : np.timedelta64 and returns {True | False}
# Returns True if the profile has no gaps greater than max_gap
def no_gap(data, max_gap_allowed):
    return max_gap(data) < max_gap_allowed

# Returns maximum difference between two consecutive records in a profile
# If more_info, returns tuple of
# (max difference, fraction from 0 to 1, timedelta64)
# where fraction is how far into the session (as fraction of whole session)
# the first lare gap was and the timedelta is how far into session the first
# large gap occurred.
def max_gap(data, more_info = False):
    profile = data.profile
    times = data.profile.index
    difference = np.diff(times)
    # If difference is empty, return no gap (this is case with one datapoint)
    if difference.size == 0: return np.timedelta64(0, 's')
    else:
        # Get the index of the first instance of the maximum value of gaps between points
        ind = np.argmax(difference)
        max_diff = difference[ind]
        if more_info : return (max_diff, ind/float(times.shape), times[ind]-times[0])
        else: return max_diff # A numpy timedelta64

# Takes data and a cutoff point (0 to 1) and returns {True | False}
# If cutoff is 0, then return True.
# Looks up how much energy used and if greater than or equal to cutoff_energy,
# then returns True. Else returns False.
def enough_energy_used(data, min_energy):
    # Check initial case
    if min_energy == 0: return True

    return data.energyDemand > min_energy

# Takes data and returns True if the maximum power of the charging profile uses
# more than or equal to to min_power. If min_power is 0, return True.
def enough_power (data, min_power):
    # Check initial case
    if min_power == 0: return True
    
    # Profile in mA. To get power, divide by 1000, multiply by 208
    maxPower = data.profile['mamps_last'].max() / 1000.0 * 208
    return maxPower >= min_power


# TODO: Tail drops off.

# TODO: cut off profile. 

# Sec 2.2. Reasons for data to be invaid. These are custom exceptions that are a
# subclass of the Exception class.
# TODO: Find a more elegant solution
#class ValidData(Exception):
    # When all other tests pass, we have vaid data.
#    pass
#class ShortTime(Exception):
    # When long_enough returns False.
#    pass
#class LostDatapoints(Exception):
    # When enough_points returns False.
#    pass
#class LittleEnergyUsed(Exception):
    # When enough_energy_used returns False.
#    pass
#class PowerTooLow(Exception):
    # When enough_power returns False.
#    pass

ValidData = "ValidData"
ShortTime = "ShortTime"
LostDatapoints = "LostDatapoints"
LittleEnergyUsed = "LittleEnergyUsed"
PowerTooLow = "PowerTooLow"
LongTime = "LongTime"
BigGap = "BigGap"