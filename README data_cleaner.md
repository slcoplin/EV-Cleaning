

# Module data\_cleaner

## Overview

This module finds the validity and features of individual charging sessions. All functions use data of type Entry. To create an instance of Entry from a charging profile dataframe, use &#39;df\_to\_entry&#39;.


## Classes

### class Entry

Stores data about one charging session.

#### startTime

Time of first datapoint recorded.

If user input is added, create a different attribute for this class (e.g. supposedStart).

#### endTime

Time of last datapoint recorded.

If user input is added, create a different attribute for this class (e.g. supposedEnd).

#### energyDemand

Energy used in the profile, in AV. Integral of profile over time, assuming 208 V.

If user input is added, create a different attribute for this class (e.g. supposedEnergyDemand).

#### profile

pandas.DataFrame with pandas.Timestamp index and column &quot;mamps\_last&quot; corresponding to the current charging (in mA) at a given time.

#### get\_curr(time)

Function to get the current from &#39;profile&#39; at a requested time.

#### \_\_init\_\_ (self, start, end, energyDemand, profile)

Returns an instance of Entry with parameters as given.

## Functions

### df\_to\_entry(df)

#### Parameters

| Name | Type | Description |
| --- | --- | --- |
| df | pandas DataFrame withindex : pandas.Timestamp and column labeled &quot;mamps\_last&quot;:  number | One session&#39;s charging profile_Index_: time for given datapoint_mamps\_last_: current at time in mA |

#### Returns

| Name | Type | Description |
| --- | --- | --- |
| data | Entry | Entry with values calculated from profile. energyDemand from integrating &#39;df&#39; and assuming 208 V. |

### is\_clean( data, min\_charge\_time = np.timedelta64(20, &#39;m&#39;), min\_average\_time\_gap = np.timedelta64(11, &#39;s&#39;), max\_gap\_allowed = np.timedelta64(1, &#39;m&#39;), min\_energy = 1, min\_maxpower = 2000, max\_time = np.timedelta64(20, &#39;h&#39;) )

Returns True or False based on whether the data meets all given criteria or not, respectively.

#### Parameters

| Name | Type | Description |
| --- | --- | --- |
| data | Entry | Once charging profileIndex: time for given datapointmamps\_last: current at time in mA |
| min\_charge\_time | numpy.timdedelta64 | Minimum length of session to be valid.Default: 20 minutesThis criterion will be ignored if None. |
| max\_time | numpy.timdedelta64 | Minimum length of session to be valid.Default: 1 minuteThis criterion will be ignored if None. |
| max\_gap\_allowed | numpy.timdedelta64 | Maximum gap between consecutive points in a profile to be valid. Large gaps indicate connectivity issues with the station. Even short gaps seem to cause problematic data. If this is resolved, 10 minutes or greater is appropriate.Default: 1 minuteThis criterion will be ignored if None. |
| min\_average\_time\_gap | numpy.timdedelta64 | Minimum average gap between datapoints in profile. If average gap is large, data has not been recorded frequently enough.Default: 11 secondsThis criterion will be ignored if None. |
| min\_energy | int or float | Minumum energy consumed in the session to be considered valid, in kWh.Default: 1 (kWh)This criterion will be ignored if 0. |
| min\_maxpower | int or float | Minimum power reached for session to be valid, in Watts.Default: 2000 (W)This criterion will be ignored if 0. |
| other\_tests | list of functions with:parameter: data : Entryreturn: anything | A list of functions to be run on &#39;data&#39; and returned.For example, a function that takes data and returns the length of the session. |

#### Returns

Boolean, True is the data has no problems, False otherwise.

### clean\_data( data, min\_charge\_time = np.timedelta64(20, &#39;m&#39;), min\_average\_time\_gap = np.timedelta64(11, &#39;s&#39;), max\_gap\_allowed = np.timedelta64(1, &#39;m&#39;), min\_energy = 1, min\_maxpower = 2000, max\_time = np.timedelta64(20, &#39;h&#39;), other\_tests = False )

Returns a tuple with information about whether the data meets all given criteria, why, and other tests.

#### Parameters

| Name | Type | Description |
| --- | --- | --- |
| data | Entry | Once charging profileIndex: time for given datapointmamps\_last: current at time in mA |
| min\_charge\_time | numpy.timdedelta64 | Minimum length of session to be valid.If &#39;data&#39; does not pass this criterion, second element of return error will be &quot;ShortTime&quot;.Default: 20 minutesThis criterion will be ignored if None. |
| max\_time | numpy.timdedelta64 | Minimum length of session to be valid.If &#39;data&#39; does not pass this criterion, second element of return error will be &quot;BigGap&quot;.Default: 1 minuteThis criterion will be ignored if None. |
| max\_gap\_allowed | numpy.timdedelta64 | Maximum gap between consecutive points in a profile to be valid. Large gaps indicate connectivity issues with the station. Even short gaps seem to cause problematic data. If this is resolved, 10 minutes or greater is appropriate.If &#39;data&#39; does not pass this criterion, second element of return error will be &quot;BigGap&quot;.Default: 1 minuteThis criterion will be ignored if None. |
| min\_average\_time\_gap | numpy.timdedelta64 | Minimum average gap between datapoints in profile. If average gap is large, data has not been recorded frequently enough.If &#39;data&#39; does not pass this criterion, second element of return error will be &quot;LostDatapoints&quot;.Default: 11 secondsThis criterion will be ignored if None. |
| min\_energy | int or float | Minumum energy consumed in the session to be considered valid, in kWh.If &#39;data&#39; does not pass this criterion, second element of return error will be &quot;LittleEnergyUsed&quot;.Default: 1 (kWh)This criterion will be ignored if 0. |
| min\_maxpower | int or float | Minimum power reached for session to be valid, in Watts.If &#39;data&#39; does not pass this criterion, second element of return error will be &quot;PowerTooLow&quot;.Default: 2000 (W)This criterion will be ignored if 0. |
| other\_tests | list of functions with:parameter: data : Entryreturn: anything | A list of functions to be run on &#39;data&#39; and returned.For example, a function that takes data and returns the length of the session. |

#### Returns

(is\_clean, error, other\_results\*)

| Name | Type | Description |
| --- | --- | --- |
| is\_clean | boolean | True if data passes all parameters. False otherwise. |
| error | string | Corresponding to passing all tests (ValidData) or which criterion failed.One of: ValidData, ShortTime, BigGap, LongTime, LostDatapoints, LittleEnergyUsed, PowerTooLow, |
| other\_results\* (optional) | anything | Each element corresponds to the output of each function in &#39;other\_tests&#39;, in order. |

### session\_length( data )

Takes data of type Entry

Returns the length of time from the first datapoint to last in a profile.

### datapoint\_fraction( data, supposed\_time\_gap = np.timedelta64(10, &#39;s&#39;) )

Takes data of type Entry and an expected timedelta of type numpy.timedelta64.

Returns the fraction of datapoints in a profile compared to the number of points expected based on the length of time and given &#39;supposed\_time\_gap&#39;.

### average\_gap( data )

Takes data of type Entry

Returns the average gap in time between consecutive datapoints in the data.profile.

### max\_gap( data )

Takes data of type Entry

Returns the maximum gap in time between two consecutive datapoints in the data.profile.

### Helper functions for &#39;is\_clean&#39; and &#39;clean\_data&#39;

#### \_long\_enough(data, min\_charge\_time)

Check charge period is long enough

#### \_no\_gap(data, max\_gap\_allowed)

Check that all gaps are small enough

#### \_short\_enough(data, max\_time)

Check if charge session is too long

#### \_enough\_points(data, min\_average\_time\_gap)

Check the profile has enough data points (loss of datapoints)

#### \_enough\_energy\_used(data, min\_energy)

Check the profile consumed enough energy

#### \_enough\_power(data, min\_maxpower)

Check the profile had high enough maximum power

