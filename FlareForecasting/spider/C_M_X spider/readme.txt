
The process of downloading the C/M/X-level samples through web spider is mainly as follows:

1. We obtain the information of AR number, location, level, and starttime from the website of solarmonitor (https://www.solarmonitor.org/).

2. We obtain the information of startime, level from the website of NOAA (https://www.ngdc.noaa.gov/stp/space-weather/solar-data/solar-features/solar-flares/x-rays/goes/xrs/).

3. We match and process the above two website information, and then obtain the downloading information.

4. According to the above downloading information, we obtain the C/M/X-level SHARP samples through web spider from the website of JSOC (http://jsoc.stanford.edu/ajax/lookdata.html?ds=hmi.sharp_cea_720s).

############################################################################################################

The execution order of the codes in the folder of C_M_X spider is as follows:
1. SolarMonitor.py
2. Combine.py
3. NOAA.py
4. Merge.py
5. MoveTime.py
6. GetRequest.py
7. GetDownload.py


