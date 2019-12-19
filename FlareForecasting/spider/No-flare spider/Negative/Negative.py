import time
from datetime import datetime, timedelta

import pandas as pd


def read_sm():
    # data = pd.read_csv("SM.csv", header=None, delimiter=",")
    data = pd.read_csv("SM.csv", header=None, delimiter=",", skiprows=1)
    data = data.as_matrix()
    result = {}
    for line in data:
        if line[1] in result:
            # date
            result[line[1]][0].append(line[0])
            # w and e
            result[line[1]][1].append(line[3][0])
            # longtitude
            result[line[1]][2].append(line[3][1:])
            # level
            result[line[1]][3].append(line[4])
        else:
            result[line[1]] = [[line[0]], [line[3][0]], [line[3][1:]], [line[4]]]
    return result


def filter():
    result = {}
    data = read_sm()
    for index in data:
        flag = True
        for i in range(len(data[index][-1])):
            if data[index][-1][i] != 'N':
                if int(data[index][-2][i]) <= 36:
                    flag = False
                    break
            if 'W' not in data[index][1] or 'E' not in data[index][1]:
                flag = False
                break
        if flag:
            result[index] = data[index][:-1]
    return result


def get_t_time():
    result = {}
    data = filter()
    for index in data:
        for i in range(len(data[index][1]) - 1):
            if data[index][1][i] == 'E':
                if data[index][1][i + 1] == 'W':
                    if int(data[index][0][i]) >= 20100501:
                        result[index] = [str(data[index][0][i]) + "000000",
                                         int(data[index][2][i])]
    return result


def move_time(hours=24):
    # move to mid line
    format = '%Y:%m:%d:%H:%M:%S'
    data = get_t_time()
    for index in data:
        real_time = data[index][0]
        real_time = real_time[:4] + ":" + real_time[4:6] + ":" \
                    + real_time[6:8] + ":" + real_time[8:10] + \
                    ":" + real_time[10:12] + ":" + real_time[12:14]
        data[index] = real_time
    # for index in data:
    #     move_seconds = (data[index][1] / 12.0) * 24 * 60 * 60
    #     real_time = data[index][0]
    #     real_time = real_time[:4] + ":" + real_time[4:6] + ":" \
    #                 + real_time[6:8] + ":" + real_time[8:10] + \
    #                 ":" + real_time[10:12] + ":" + real_time[12:14]
    #     real_time = datetime.fromtimestamp(
    #         time.mktime(time.strptime(real_time, format)))
    #     real_time = real_time + timedelta(seconds=move_seconds)
    #     real_time = real_time.strftime(format)
    #     data[index] = real_time
    # move time
    for index in data:
        mid_time = data[index]
        mid_time = datetime.fromtimestamp(
            time.mktime(time.strptime(mid_time, format)))
        start_time = (mid_time - timedelta(hours=0)).strftime(format)
        end_time = (mid_time + timedelta(hours=hours)).strftime(format)
        flush_in_disk(index, start_time, end_time)


def flush_in_disk(col, start, end):
    with open("negative.csv", "a+") as file:
        file.write(str(col) + "," + start + "," + end + "\n")


move_time()
