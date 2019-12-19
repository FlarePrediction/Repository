import pandas as pd
import numpy as np


def read(year):
    data = pd.read_csv(str(year) + ".csv", delimiter=",", header=None)
    return data.as_matrix()


def combine(start, end):
    result = []
    for year in range(start, end):
        print(year)
        result = np.append(result, read(year))
    return np.reshape(result, (-1, 6))


def dump(start, end):
    data = pd.DataFrame(combine(start, end))
    data.to_csv("SM.csv",
                header=["time", "col", "x", "y", "level", "time"],
                index=False)


dump(2010, 2019)
