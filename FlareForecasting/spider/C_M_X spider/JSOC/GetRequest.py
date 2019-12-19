import json
import time

import requests

Header = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                        '(KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36'}


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


def get_request_ID(date, col, out_path, test):
    id = get_request_id(date, col, test)
    with open(out_path + "/RequestID.csv", "a+") as file:
        start = date[0][0] + ":" + date[0][1] + ":" + date[0][2] \
                + ":" + date[0][3] + ":" + date[0][4] + ":" + date[0][5]
        end = date[1][0] + ":" + date[1][1] + ":" + date[1][2] \
              + ":" + date[1][3] + ":" + date[1][4] + ":" + date[1][5]
        file.writelines(start + "," + end + "," + col + "," + str(id) + "\n")


def get():
    with open("../Data/NeedDownload.csv", "r") as file:
        count, length = 0, 6181
        for line in file.readlines():
            count += 1
            # 3224
            print(count / length)
            date = []
            line = line.replace("\n", "").split(",")
            date.append(line[1].split(":"))
            date.append(line[2].split(":"))
            col = line[0]
            get_request_ID(date, col, "../Data", False)


get()
