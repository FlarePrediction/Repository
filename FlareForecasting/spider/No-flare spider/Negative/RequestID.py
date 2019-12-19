import json
import time

import numpy as np
import pandas as pd
import requests

Header = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                        '(KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36'}


def read():
    data = pd.read_csv("./negative.csv", header=None, delimiter=",")
    data = data.as_matrix()
    result = []
    for line in data:
        temp = [line[0], line[1].split(":"), line[2].split(":")]
        result.append(temp)
    return result


def get_request_id(date, col, test=True):
    def get_ds(date, col):
        ds = "hmi.sharp_cea_720s[]" \
             "[%s.%s.%s_%s:%s:%s_TAI-%s.%s.%s_%s:%s:%s_TAI]" \
             "[? NOAA_ARS ~ \"%s\" ?]{magnetogram}" \
             % (date[0][0], date[0][1], date[0][2], date[0][3],
                date[0][4], date[0][5], date[1][0], date[1][1],
                date[1][2], date[1][3], date[1][4], date[1][5], col)
        print(ds)
        return ds

    '''
    parameter dic
    '''
    parameter = {"op": "exp_request",
                 "ds": "hmi.sharp_cea_720s[][2011.12.31_16:00:00_TAI-2011.12.31_24:00:00_TAI][? NOAA_ARS ~ \"11389\" ?]{magnetogram}",
                 "sizeratio": "1", "process": "n=0|no_op", "requestor": "none",
                 "notify": "wszgrwxs@gmail.com", "method": "url-tar",
                 "filenamefmt": "hmi.sharp_cea_720s.{HARPNUM}.{T_REC:A}.{segment}",
                 "format": "json", "protocol": "FITS,compress Rice",
                 "dbhost": "hmidb2", "_": ""}
    url = "http://jsoc.stanford.edu/cgi-bin/ajax/jsocextfetch"
    if not test:
        parameter['ds'] = get_ds(date, col)
    while True:
        try:
            request_id = json.loads(requests.get(
                url, parameter, headers=Header, timeout=20).text)
            print(request_id)
            if request_id["status"] == 4 and request_id["error"][:4] == "Some":
                return "JSOC_20181028_236"
            request_id = request_id["requestid"]
            return request_id
        except Exception:
            time.sleep(5)
            print("Exception!")


def get():
    with open("./id.csv", "a+") as file:
        for i in read():
            id = get_request_id(i[1:], i[0], False)
            j = list(np.asarray(i[1:]).reshape([1, -1])[0])
            start, end = "", ""
            for x in range(0, 6):
                start += j[x] + ":"
            for x in j[6:]:
                end += x + ":"
            file.write(start[:-1] + "," + end[:-1] + "," + id + "\n")
            file.flush()


get()
