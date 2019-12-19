import copy
import time
from datetime import datetime, timedelta


def get_merge_dic():
    # start_time,end_time,SN,EW,level
    result = {}
    with open("../Data/merge.csv", "r") as file:
        for line in file.readlines():
            line = line.split(",")
            if line[2] not in result:
                result[line[2]] = [[line[0], line[1], int(line[3]),
                                    int(line[4]), line[5].replace("\n", "")]]
            else:
                result[line[2]].append([line[0], line[1], int(line[3]),
                                        int(line[4]), line[5].replace("\n", "")])
    return result


def position_filter(data, sn, ew):
    result = {}
    for index in data:
        for flare in data[index]:
            if flare[2] <= sn:
                if flare[3] <= ew:
                    if index not in result:
                        result[index] = [flare]
                    else:
                        result[index].append(flare)
    return result


def move_fixed_hours(hours, data):
    result = copy.deepcopy(data)
    format = '%Y:%m:%d:%H:%M:%S'
    for index in result:
        for i in range(len(result[index])):
            result[index][i][0] = time.strptime(result[index][i][0], format)
            result[index][i][1] = time.strptime(result[index][i][1], format)
            # time_a = datetime.fromtimestamp(time.mktime(time_a))
            result[index][i][0] = datetime.fromtimestamp(time.mktime(result[index][i][0]))
            result[index][i][1] = datetime.fromtimestamp(time.mktime(result[index][i][1]))
            result[index][i][0] = (result[index][i][0] - timedelta(hours=hours)).strftime(format)
            result[index][i][1] = result[index][i][1].strftime(format)
    return result


def check_correctness(data):
    result = copy.deepcopy(data)
    format = '%Y:%m:%d:%H:%M:%S'
    for index in data:
        if len(data[index]) == 1:
            continue
        for i in range(1, len(data[index])):
            before = data[index][i - 1][1]
            behind = data[index][i][0]
            before = datetime.fromtimestamp(
                time.mktime(time.strptime(before, format)))
            behind = datetime.fromtimestamp(
                time.mktime(time.strptime(behind, format)))
            if before > behind:
                result[index][i][0] = data[index][i - 1][1]
    return result


def get_write_line(data):
    result = []
    for index in data:
        for document in data[index]:
            line = index + "," + document[0] + "," + document[1] + "," \
                   + str(document[2]) + "," + str(document[3]) + "," + document[4]
            result.append(line)
    return result


def write(data):
    with open("../Data/NeedDownload.csv", "a+") as file:
        for i in data:
            file.write(i + "\n")
    return True


print(write(get_write_line(check_correctness(move_fixed_hours(24, position_filter(get_merge_dic(), 360, 45))))))
