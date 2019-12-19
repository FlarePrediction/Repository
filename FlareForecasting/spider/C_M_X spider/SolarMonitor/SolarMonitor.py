import datetime

import requests
from bs4 import BeautifulSoup


class SolarMonitor(object):
    def __init__(self):
        self.URL = "https://www.solarmonitor.org/full_disk.php"
        self.Parameter = {"date": "20160213", "type": "shmi_maglc", "indexnum": "1"}
        self.Header = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                                     '(KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36'}

    def set_date(self, date):
        self.Parameter['date'] = date

    def get_today_date(self):
        return self.Parameter['date']

    def get_yesterday_date(self):
        year = int(self.Parameter['date'][:4])
        month = int(self.Parameter['date'][4:6])
        day = int(self.Parameter['date'][6:])
        today = datetime.date(year, month, day)
        yesterday = today + datetime.timedelta(days=-1)
        return str(yesterday).replace("-", '')

    def get_content(self):
        return BeautifulSoup(requests.get(self.URL, self.Parameter, headers=self.Header).text, 'html.parser')

    def save(self, doc):
        # with open("../Data/sm/" + self.get_today_date()[:4] + ".csv", 'a+') as file:
        with open("../Data/sm/" + self.get_today_date()[:4] + ".csv", 'a+') as file:
            for d in doc:
                line = ""
                for i in range(len(d)):
                    if i != len(d) - 1:
                        line += (d[i] + ",")
                    else:
                        if len(d[i]) != 0:
                            line += (d[i][0] + "," + d[i][1] + "\n")
                        else:
                            line += ("N" + "," + "N" + "\n")
                file.write(line)

    def get_data(self):
        contents = self.get_content().select('.noaaresults')
        for content in contents:
            document = []
            number = content.find(id='noaa_number').a.string
            position = content.find(id='position').get_text().replace(" ", '').replace("\"", '')[0:6]
            todays = []
            yesterdays = []
            for i in content.find(id='events'):
                # have flare
                if hasattr(i, 'a'):
                    try:
                        if i['style'] == 'color:#0000FF;':
                            text = i.get_text().replace(' ', '').replace("/", ''). \
                                replace("-", '').replace('\n', '')
                            if len(text) >= 10:
                                todays.append([text[0], text[5:10]])
                        if i['style'] == 'color:#58ACFA;':
                            text = i.get_text().replace(' ', '').replace("/", ''). \
                                replace("-", '').replace('\n', '')
                            if len(text) >= 10:
                                yesterdays.append([text[0], text[5:10]])
                    except KeyError:
                        pass
                # no flare
                else:
                    todays.append(["N", "99:99"])
            if len(todays) != 0:
                for today in todays:
                    # document.append([self.get_today_date(), number, position[:3], position[3:], today])
                    document.append([self.get_today_date(), number, position[1:3], position[4:], today])
            if len(yesterdays) != 0:
                for yesterday in yesterdays:
                    # document.append([self.get_today_date(), number, position[:3], position[3:], yesterday])
                    document.append([self.get_today_date(), number, position[1:3], position[4:], yesterday])
            self.save(document)
            print(document)


def main(x, y):
    test = SolarMonitor()
    start = datetime.date(x, 1, 1)
    end = datetime.date(y, 10, 1)
    while start != end:
        test.set_date(str(start).replace("-", ''))
        try:
            test.get_data()
        except requests.exceptions.ConnectionError:
            print("Retry!")
            continue
        start = start + datetime.timedelta(days=1)


# main(2010, 2018)
main(1996, 2018)
