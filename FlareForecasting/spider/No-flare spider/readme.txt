
The process of downloading the No-flare level samples through web spider is mainly as follows:

1. We obtain the information of AR number, location, level, and starttime from the website of solarmonitor (https://www.solarmonitor.org/).

2. We process the above website information, and then obtain the downloading information.

3. According to the above downloading information, we obtain the No-flare level SHARP samples through web spider from the website of JSOC (http://jsoc.stanford.edu/ajax/lookdata.html?ds=hmi.sharp_cea_720s).

############################################################################################################

The execution order of the codes in the folder of No-flare spider is as follows:
1. SolarMonitor.py
2. Combine.py
3. Negative.py
4. RequestID.py
5. FromRequestIDGetURL.py


