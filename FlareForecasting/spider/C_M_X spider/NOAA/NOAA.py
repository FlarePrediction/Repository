import requests
import time

def get_url(year):
    if year == 2015:
        return "https://www.ngdc.noaa.gov/stp/space-weather/solar-data/solar-features/solar-flares/x-rays/goes/xrs/goes-xrs-report_2015_modifiedreplacedmissingrows.txt"
    elif year == 2017:
        return "https://www.ngdc.noaa.gov/stp/space-weather/solar-data/solar-features/solar-flares/x-rays/goes/xrs/goes-xrs-report_2017-ytd.txt"
    else:
        return "https://www.ngdc.noaa.gov/stp/space-weather/solar-data/solar-features/solar-flares/x-rays/goes/xrs/goes-xrs-report_" + str(year) + ".txt"


def save(data):
    # with open("../Data/SM.csv", 'a+') as file:
    with open("../Data/NOAA.csv", 'a+') as file:
        for d in data:
            line = ""
            for i in range(len(d)):
                if i != len(d) - 1:
                    line += (d[i] + ",")
                else:
                    line += (d[i] + "\n")
            file.write(line)
            file.flush()


def get_data_matrix(year):
    data = requests.get(get_url(year), timeout=10).text.split("\n")
    result = []
    for line in data:
        print(line)
        if len(line) >= 59:
            date = str(year)[:2] + line[5:11]
            # print("111" ,len("31777750901  "))
            start = line[13:13 + 4]
            # print("222",len("31777750901  1512E"))
            end = line[18:18 + 4]
            # print("333",len("31777750901  1512E1519 "))
            M = line[23:23 + 4]
            # print("444",len("31777750901  1512E1519 1512 N03E54SN "))
            level = line[59]
            if level != " ":
                result.append([date, start, M, end, level])
    return result


for i in range(1975, 2018):
    print(i)
    data = 0
    while True:
        try:
            data = get_data_matrix(i)
            break
        except requests.exceptions.ConnectionError:
            print("ConnectionError")
        except requests.exceptions.ReadTimeout:
            print("ReadTimeout")
        except requests.exceptions:
            print("Exception!")
    save(data)
