import json
import time

import pandas as pd
import requests

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


def get_id():
    data = pd.read_csv("./id.csv", header=None, delimiter=",")
    data = data.as_matrix()
    result = []
    for line in data:
        result.append(line[-1])
    return result


def get_url():
    ids = get_id()
    with open("ID_URL.csv", "a+") as file1:
        with open("URL.csv", "a+") as file2:
            for id in ids:
                if id != "JSOC_20181028_236":
                    url = get_file_url(id)
                    file1.write(id + "," + url + "\n")
                    file2.write(url + "\n")
                    file1.flush()
                    file2.flush()


get_url()
