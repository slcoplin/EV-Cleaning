
"""
This module finds the validity and features of individual charging
sessions.All functions use data of type Entry. To create an instance
of Entry from a charging profile dataframe, use 'df_to_entry'.
"""
import numpy as np

# Sec 0. Reasons for data to be invaid, in the order they are checked.
ShortTime = "ShortTime"
BigGap = "BigGap"
LongTime = "LongTime"
LostDatapoints = "LostDatapoints"
LittleEnergyUsed = "LittleEnergyUsed"
PowerTooLow = "PowerTooLow"
ValidData = "ValidData"

# Sec 1. Data Manager
class Entry:
    """
    Stores data about one charging session.

    Attributes:
    startTime : Time of first datapoint recorded.
    
    endTime : Time of last datapoint recorded.
    
    energyDemand : Energy used in the profile, in AV. Integral of profile over
    time, assuming 208 V.
    
    profile : pandas.DataFrame with pandas.Timestamp index and
    column "mamps_last" corresponding to the current charging (in mA) at a
    given time. Fine if other columns exist too.
    """
    
    def __init__ (self, start, end, profile, energyDemand):
        """ Returns an instance of Entry with parameters as given. """
        
        self.startTime = start
        self.endTime = end
        self.energyDemand = energyDemand
        self.profile = profile
        # The module could get rewritten to only use functions defined in
        # the Entry, for which the following line could be useful
        # self.get_curr = lambda time: profile_fetch(time, self.profile)
    

def df_to_entry ( df ):
    """
    Creates an instance of Entry from a charging session DataFrame.
    
    Parameters:
    df:	pandas DataFrame with
        index : pandas.Timestamp and
        column "mamps_last" :  number.
    One session's charging profile with provided current in mA over time.
    
    Returns:
    Instance of Entry with values calculated from profile and energyDemand from
    integrating 'df' and assuming 208 V.

    """
    start = df.index[0]
    end = df.index[-1]
    # For more with dataframes : https://www.shanelynn.ie/select-pandas-dataframe-rows-and-columns-using-iloc-loc-and-ix/
    # Assumes current is 0th column, and in mA
    # Demand in W*hr = A * V * hr. Assume 208 V.
    mA_to_A_V = 1/10000.0 * 208
    integral = np.trapz(df.iloc[:,0], df.index)
    hour = np.timedelta64(1, 'h')
    demand = integral / hour * mA_to_A_V

    # The lambda function to fetch the current from the dataframe, if this is
    # ever needed
    # profile_fetch = lambda time, profile: profile.loc[time][0]
    
    entry = Entry(start, end, df, demand)
    return entry


# Sec 2. Cleaning functions and sub-functions

def is_clean(   data, \
                min_charge_time = np.timedelta64(20, 'm'), \
                min_average_time_gap = np.timedelta64(11, 's'), \
                max_gap_allowed = np.timedelta64(5, 'm'), \
                min_energy = 1, \
                min_maxpower = 2000, \
                max_time = np.timedelta64(20, 'h')):
    """
    Returns True or False based on whether the data meets all given criteria or
    not, respectively.
    
    
    Parameters:
    data (Entry) - One charging session
    
    min_charge_time (numpy.timedelta64)  - Minimum length of session to be
    valid. This criterion will be ignored if None. Default: 20 minutes
    
    
    max_time (numpy.timedelta64) - Minimum length of session to be valid.
    Default: 1 minute. This criterion will be ignored if None.
    
    max_gap_allowed (numpy.timedelta64) - Maximum gap between consecutive points
    in a profile to be valid. This criterion will be ignored if None.
    Default: 5 minutes
    
        Large gaps indicate connectivity issues with the station. Even short
        gaps seem to cause problematic data. If this is resolved, 10 minutes or
        greater is appropriate.
    
    
    min_average_time_gap (numpy.timedelta64) - Minimum average gap between
    datapoints in profile. If average gap is large, data has not been recorded
    frequently enough. This criterion will be ignored if None.
    Default: 11 seconds.
    
    
    min_energy (number) - Minumum energy consumed in the session to be
    considered valid, in kWh. This criterion will be ignored if 0.
    Default: 1 (kWh).
    
    min_maxpower (number) - Minimum power reached for session to be valid, in
    Watts. This criterion will be ignored if 0. Default: 2000 (W)    
    
    
    
    Returns: Boolean, True is the data has no problems, False otherwise.
    """
    return clean_data(  data, \
                        min_charge_time, \
                        min_average_time_gap, \
                        max_gap_allowed, \
                        min_energy, \
                        min_maxpower, \
                        max_time)[0]

                

def clean_data( data, \
                min_charge_time = np.timedelta64(20, 'm'), \
                min_average_time_gap = np.timedelta64(11, 's'), \
                max_gap_allowed = np.timedelta64(5, 'm'), \
                min_energy = 1, \
                min_maxpower = 2000, \
                max_time = np.timedelta64(20, 'h'), \
                other_tests = False
                ):
    """
    Returns a tuple with information about whether the data meets all given
    criteria, why, and other tests. Find errors in order: ShortTime, BigGap,
    LongTime, LostDatapoints, LittleEnergyUsed, PowerTooLow.
    
    
    Parameters:
    
    data (Entry) - One charging session
    
    min_charge_time (numpy.timedelta64)  - Minimum length of session to be
    valid. This criterion will be ignored if None. Default: 20 minutes
    
    
    max_time (numpy.timedelta64) - Minimum length of session to be valid.
    Default: 1 minute. This criterion will be ignored if None.
    
    max_gap_allowed (numpy.timedelta64) - Maximum gap between consecutive points
    in a profile to be valid. This criterion will be ignored if None.
    Default: 5 minutes
    
        Large gaps indicate connectivity issues with the station. Even short
        gaps seem to cause problematic data. If this is resolved, 10 minutes or
        greater is appropriate.
    
    
    min_average_time_gap (numpy.timedelta64) - Minimum average gap between
    datapoints in profile. If average gap is large, data has not been recorded
    frequently enough. This criterion will be ignored if None.
    Default: 11 seconds.
    
    
    min_energy (number) - Minumum energy consumed in the session to be
    considered valid, in kWh. This criterion will be ignored if 0.
    Default: 1 (kWh).
    
    min_maxpower (number) - Minimum power reached for session to be valid, in
    Watts. This criterion will be ignored if 0. Default: 2000 (W)    
    
    other_tests (list of functions with:
                    input data (Entry) and output: anything)
                - A list of functions to be run on 'data' and returned.
    For example, a function that takes data and returns the length of the
    session.
    Recommend using module functions session_length, average_gap, and max_gap.
    No other tests will be performed if other_tests is False or [].
    Default: False.

    
    
    
    Returns: (is_clean, error, other_results*)
    
    is_clean (boolean) - True if data passes all parameters. False otherwise.
    
    error (string) - Corresponding to passing all tests (ValidData) or
    which criterion failed. Options (in order of which checked first):
    ValidData, ShortTime, BigGap, LongTime, LostDatapoints, LittleEnergyUsed,
    PowerTooLow.

    other_results* (optional, any type) - Each element corresponds to the output
    of each function in 'other_tests', in order.
    
    """
    # Check charge period is long enough
    if not _long_enough(data, min_charge_time): result = (False, ShortTime)
    
    # Check that all gaps are small enough
    elif not _no_gap(data, max_gap_allowed): result = (False, BigGap)
    
    # Check if charge session is too long
    elif not _short_enough(data, max_time): result = (False, LongTime)
   
    # Check the profile has enough data points (loss of datapoints)
    elif not _enough_points(data, min_average_time_gap): result = (False, LostDatapoints)

    # Check the profile consumed enough energy
    elif not _enough_energy_used(data, min_energy): result = (False, LittleEnergyUsed)

    # Check the profile had high enough maximum power
    elif not _enough_power(data, min_maxpower): result = (False, PowerTooLow)

    # If all of the previous functions passed, then valid data.
    else: result = (True, ValidData)
    
    # Other tests to do on an Entry
    if other_tests:
        others = []
        for test in other_tests:
            others.append(test(data))
        return result + tuple(others)
    else: 
        return result

# Sec 2.1. Sub-functions for clean_data

def _long_enough (data, min_time):
    """
    Takes data and returns True if the charging profile spans more than or equal
    to min_time minutes. If min_time is 0, return True.
    """
    
    # Check initial case
    if min_time == None: return True

    return (data.endTime - data.startTime) >= min_time

def _no_gap(data, max_gap_allowed):
    """
    Takes data : Entry and a max_gap : np.timedelta64 and returns {True | False}
    Returns True if the profile has no gaps greater than max_gap.
    """
    if max_gap_allowed == None: True
    return max_gap(data) < max_gap_allowed

def _short_enough (data, max_time):
    """
    Takes data and returns True if the charging profile spans less than or equal
    to max_time (as a numpy timedelta64).
    """
    return (data.endTime - data.startTime) <= max_time

def _enough_points(data, min_average_time_gap):
    """ Check the profile has enough data points (loss of datapoints). """
    # Check initial case
    if min_average_time_gap == None: return True
    
    # Check if enough
    return average_gap(data) < min_average_time_gap

def _enough_energy_used(data, min_energy):
    """
    Takes data of type Entry.
    
    Looks up how much energy used and if greater than or equal to cutoff_energy,
    then returns True. Else returns False.
    """
    # Check initial case
    if min_energy == 0: return True

    return data.energyDemand > min_energy

def _enough_power (data, min_power):
    """
    Takes data of type Entry and returns True if the maximum power of the 
    charging profile uses more than or equal to to min_power. If min_power is 0,
    return True.
    """
    # Check initial case
    if min_power == 0: return True
    
    # Profile in mA. To get power, divide by 1000, multiply by 208
    maxPower = data.profile['mamps_last'].max() / 1000.0 * 208
    return maxPower >= min_power

# Sec 2.2 Helper functions or more info functions that take data in the form
# Entry.

def session_length (data):
    """
    Takes data of type Entry 
    Returns the length of time from the first datapoint to last in a profile.
    """
    return data.endTime - data.startTime

def datapoint_fraction(data, supposed_time_gap = np.timedelta64(10, 's')):
    """
    Takes data of type Entry and an expected timedelta of type
    numpy.timedelta64.
    
    Returns the fraction of datapoints in a profile compared to the number of
    points expected based on the length of time and given 'supposed_time_gap'.
    """
     # Actual # of points
    numPoints = data.profile.shape[0] # Number of rows. Assumes a dataframe.
    # Theoretical # of points
    profileTime = data.endTime - data.startTime
    if profileTime == np.timedelta64(0, 's'): return 1
    # Some sessions had >1, so ignore for now.
    return min (numPoints / (profileTime / supposed_time_gap), 1)


def average_gap(data):
    """
    Takes data of type Entry 
    
    Returns the average gap in time between consecutive datapoints in the
    data.profile as numpy.timedelta64.
    """
     # Actual # of points
    numPoints = data.profile.shape[0] # Number of rows. Assumes a dataframe.
    # Theoretical # of points
    profileTime = data.endTime - data.startTime
    if profileTime == np.timedelta64(0, 's'): return profileTime
    ave_gap = np.timedelta64(profileTime / numPoints)
    return ave_gap


def max_gap(data, more_info = False):
    """
    Takes data of type Entry and more_info of type bool.
    
    Returns the maximum gap in time between two consecutive datapoints in the data.profile.
    
    If more_info, returns tuple of
    (max difference, fraction from 0 to 1, pandas.TimeStamp) where
    fraction is how far into the session (as fraction of whole session)
        the first lare gap was and
    the pandas.Timestamp is what time the first large gap occurred.
    """
    profile = data.profile
    times = data.profile.index
    difference = np.diff(times)
    # If difference is empty, return no gap (this is case with one datapoint)
    if difference.size == 0:
        if more_info: return (np.timedelta64(0, 's'), 0, times[0])
        else: return np.timedelta64(0, 's')
    else:
        # Get the index of the first instance of the maximum value of gaps
        # between points
        ind = np.argmax(difference)
        max_diff = difference[ind]
        if more_info : return (max_diff, \
                               ind/float(times.shape[0]), \
                               times[ind])
        else: return max_diff # A numpy timedelta64
