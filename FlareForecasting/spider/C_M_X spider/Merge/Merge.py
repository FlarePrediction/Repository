def format_time(data):
    year = data[0:4]
    month = data[4:6]
    day = data[6:8]
    hour = data[8:10]
    minute = data[10:12]
    return year + ":" + month + ":" + day + ":" + hour + ":" + minute + ":00"


'''
sm dic:
{start_time：[end_time, level]}
'''


def get_noaa_dic():
    result = {}
    # with open("../Data/SM.csv", "r") as file:
    with open("../Data/NOAA.csv", "r") as file:
        for line in file.readlines():
            line = line.split(",")
            start_time = line[0] + line[1]
            if start_time not in result:
                result[start_time] = [line[0] + line[3], line[4].replace("\n", "")]
    return result


'''
sm_dic:
{starttime：[AR_number，SN，EW，level]}
'''


def get_sm_dic():
    result = {}
    with open("../Data/SM.csv", "r") as file:
        for line in file.readlines():
            line = line.split(",")
            start_time = line[0] + line[-1].replace(":", "").replace("\n", "")
            if start_time not in result:
                result[start_time] = [line[1], line[2], line[3], line[4]]
    return result


def write(data):
    with open("../Data/merge.csv", "a+") as file:
        file.write(data + "\n")


def merge():
    noaa_dic = get_noaa_dic()
    sm_dic = get_sm_dic()
    for start_time in noaa_dic:
        if start_time in sm_dic:
            print(sm_dic[start_time][-1])
            print(noaa_dic[start_time][-1])
            if sm_dic[start_time][-1] == noaa_dic[start_time][-1]:
                print(start_time)
                end_time = noaa_dic[start_time][0]
                sm = sm_dic[start_time]
                line = format_time(start_time) + "," + format_time(end_time) + "," \
                       + sm[0] + "," + sm[1] + "," + sm[2] + "," + sm[3]
                write(line)


merge()
