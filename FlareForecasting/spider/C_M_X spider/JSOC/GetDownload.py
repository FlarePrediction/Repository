import json
import time

import requests


def get_request_dic():
    result = {}
    with open("../Data/RequestID.csv", "r") as file:
        for line in file.readlines():
            line = line.split(",")
            index = line[0] + line[1]
            data = line[-1].replace("\n", "")
            result[index] = data
    return result


def get_need_download_dic():
    result = {}
    with open("../Data/NeedDownload.csv", "r") as file:
        for line in file.readlines():
            line = line.split(",")
            index = line[1] + line[2]
            data = line[0] + "," + line[3] + "," + \
                   line[4] + "," + line[-1].replace("\n", "")
            result[index] = data
    return result


def gen_request_id_2():
    request_dic = get_request_dic()
    need_download_dic = get_need_download_dic()
    with open("../Data/classificationEvidence.csv", "a+") as file:
        for i in need_download_dic:
            if i in request_dic:
                file.write(need_download_dic[i] + "," +
                           i[:19] + "," + i[19:] + "," + request_dic[i] + "\n")


gen_request_id_2()


'''
The above code is used to generate a classificationEvidence.csv file.
'''


Header = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                        '(KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36'}


def get_file_url(request_id):
    download_url = "http://jsoc.stanford.edu/cgi-bin/ajax/jsoc_fetch"
    download_parameter = {"op": "exp_status", "requestid": request_id}
    while True:
        try:
            file_url = json.loads(requests.get(download_url,
                                               download_parameter,
                                               headers=Header, timeout=10).text)
            print(file_url)
            print(file_url['count'], "Fits，"
                                              "size:", file_url['size'], "MB!", file_url)
            return "http://jsoc.stanford.edu" + file_url['tarfile']
        except Exception:
            time.sleep(5)
            pass


def write_url():
    with open("../Data/classificationEvidence.csv", "r") as reader:
            with open("../Data/url.csv", "a+") as url_writer:
                for document in reader.readlines():
                    document = document.replace("\n", "")
                    line = document.split(",")
                    url = get_file_url(line[-1]) + "\n"
                    print(url)
                    # url
                    url_writer.write(url)
                    url_writer.flush()


write_url()


