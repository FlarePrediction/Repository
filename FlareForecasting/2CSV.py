import os
import warnings

import cv2
import numpy as np
import pandas as pd
from astropy.io import fits


warnings.filterwarnings("ignore")

img_rows, img_cols = 128, 128


def get_data_from_fits(file_name):
    img, t, n, c = 0, 0, 0, 0
    try:
        with fits.open(file_name, mode="append") as file:
            file.verify('fix')
            if len(file) > 1:
                img = cv2.resize(file[1].data, (img_rows, img_cols))
                img = img.astype(np.int32)
                t = file[1].header["T_REC"]
                n = file[1].header["NOAA_NUM"]
                c = file[1].header["NOAA_AR"]
                return img, t, n, c
    except fits.verify.VerifyError:
        return img, t, n, c


def get_files_path(directory):
    for i, j, k in os.walk(directory):
        for file_name in k:
            if file_name.split(".")[-1] == "fits":
                yield file_name


def shuffle_dic(dic, rate=0.8):
    # shuffle
    keys = list(dic.keys())
    np.random.shuffle(keys)
    # split
    train_quality = int(rate * len(keys))
    train, test = [], []
    # add into train and test
    for i in range(len(keys)):
        if i < train_quality:
            train.append(keys[i])
        else:
            test.append(keys[i])
    # return
    return [id for key in train for id in dic[key]], \
           [id for key in test for id in dic[key]]


def positive(rate=0.8):
    m_area, x_area = [], []
    data = pd.read_csv("./spider/C_M_X spider/Data/classificationEvidence.csv", header=None, delimiter=",").as_matrix()
    except_tar_name = ["JSOC_20181030_231", "JSOC_20181028_236", "JSOC_20181122_369"]

    def positive_x():
        x_dic = {}
        for document in data:
            if document[3] == "X" and document[-1] not in except_tar_name:
                if document[0] in x_dic:
                    x_dic[document[0]].append(document[-1])
                else:
                    x_dic[document[0]] = [document[-1]]
                    x_area.append(document[0])
        return shuffle_dic(x_dic, rate)

    def positive_m():
        m_dic = {}
        for document in data:
            if document[3] == "M" and document[0] not in x_area \
                    and document[-1] not in except_tar_name:
                if document[0] in m_dic:
                    m_dic[document[0]].append(document[-1])
                else:
                    m_dic[document[0]] = [document[-1]]
                    m_area.append(document[0])
        return shuffle_dic(m_dic, rate)

    def positive_c():
        c_dic = {}
        for document in data:
            if document[3] == "C" and document[0] not in x_area and \
                    document[0] not in m_area and document[-1] not in except_tar_name:
                if document[0] in c_dic:
                    c_dic[document[0]].append(document[-1])
                else:
                    c_dic[document[0]] = [document[-1]]
        return shuffle_dic(c_dic, rate)

    train, test = [], []
    x_train, x_test = positive_x()
    m_train, m_test = positive_m()
    c_train, c_test = positive_c()
    train.extend(x_train)
    train.extend(m_train)
    train.extend(c_train)
    test.extend(x_test)
    test.extend(m_test)
    test.extend(c_test)
    return train, test


def negative(rate=0.8):
    data = pd.read_csv("./spider/No-flare spider/Negative/id.csv", header=None, delimiter=",").as_matrix()
    train_quality = int(rate * len(data))
    train_id, test_id = [], []
    np.random.shuffle(data)
    except_tar_name = ["JSOC_20181030_231", "JSOC_20181028_236", "JSOC_20181122_369"]
    for i in range(len(data)):
        if data[i][-1] not in except_tar_name:
            if i <= train_quality:
                train_id.append(data[i][-1])
            else:
                test_id.append(data[i][-1])
    return train_id, test_id


class SelectLevel(object):
    def __init__(self):
        data = pd.read_csv("./spider/C_M_X spider/Data/classificationEvidence.csv", header=None, delimiter=",").as_matrix()
        self.__dic = {}
        for line in data:
            self.__dic[line[-1]] = line[3]

    def select(self, id_name):
        if id_name in self.__dic:
            return self.__dic[id_name]
        else:
            return "N"


def write_csv(img, time_record, area_num, num_of_area_in_fits, level, csv_num, is_positive=True, is_train=True):
    def rotate(image, angle):
        return np.rot90(np.array(image).reshape((img_rows, img_cols)), angle / 90)

    def flip(image, flag=True):
        if flag:
            return np.fliplr(np.array(image).reshape((img_cols, img_rows)))
        else:
            return np.flipud(np.array(image).reshape((img_cols, img_rows)))

    def convert_writeable(image):
        new_line = time_record[:-4] + "," + str(area_num) + "," + \
                   str(num_of_area_in_fits) + "," + level + ","
        for new_pixel in np.array(image).reshape((1, img_rows * img_cols))[0]:
            new_line += str(new_pixel) + ","
        new_line = new_line[:-1] + "\n"
        return new_line

    # ARs where N level and C/M/X level overlap
    except_area = [11121, 11163, 11366, 11410, 11470, 11490, 11534,
                   11579, 11585, 11634, 11638, 11670, 11694, 11691,
                   11784, 11868, 12065, 12082, 12232, 12237, 12258,
                   12293, 12394, 12511, 12648]
    img = np.array(img).reshape((1, img_rows * img_cols))[0]
    if -2147483648 in img:
        return -1
    if num_of_area_in_fits in except_area and level == "N":
        return -1

    print(time_record)
    line = convert_writeable(img)
    if level == "X":
        line += convert_writeable(flip(rotate(img, 90), True))
        line += convert_writeable(flip(rotate(img, 180), True))
        line += convert_writeable(flip(rotate(img, 270), True))
        line += convert_writeable(flip(rotate(img, 90), False))
        line += convert_writeable(flip(rotate(img, 180), False))
        line += convert_writeable(flip(rotate(img, 270), False))
        line += convert_writeable(rotate(img, 90))
        line += convert_writeable(rotate(img, 180))
        line += convert_writeable(rotate(img, 270))
        line += convert_writeable(flip(img, True))
        line += convert_writeable(flip(img, False))
    elif level == "M":
        line += convert_writeable(rotate(img, 90))
        line += convert_writeable(rotate(img, 180))
        line += convert_writeable(rotate(img, 270))
        line += convert_writeable(flip(img, True))
        line += convert_writeable(flip(img, False))

    if is_positive:
        if is_train:
            with open(str(csv_num) + "_positive_train.csv", "a+") as file:
                file.write(line)
        else:
            with open(str(csv_num) + "_positive_test.csv", "a+") as file:
                file.write(line)
    else:
        if is_train:
            with open(str(csv_num) + "_negative_train.csv", "a+") as file:
                file.write(line)
        else:
            with open(str(csv_num) + "_negative_test.csv", "a+") as file:
                file.write(line)


def main_work():
    for i in range(0, 10):
        np.random.seed(i)
        db = SelectLevel()
        positive_train, positive_test = positive()
        negative_train, negative_test = negative()
        PATH = "E:\\New\\"
        for dir_name in positive_train:
            for fits_file in get_files_path(PATH + dir_name):
                if db.select(dir_name) == "X" and np.random.random() <= 1.:
                    img, time_record, num_of_area, area_count = \
                        get_data_from_fits(PATH + dir_name + "\\" + fits_file)
                    write_csv(img, time_record, num_of_area, area_count, "X", i)
                elif db.select(dir_name) == "M" and np.random.random() <= 1.:
                    img, time_record, num_of_area, area_count = \
                        get_data_from_fits(PATH + dir_name + "\\" + fits_file)
                    write_csv(img, time_record, num_of_area, area_count, "M", i)
                elif db.select(dir_name) == "C" and np.random.random() <= 0.2:
                    img, time_record, num_of_area, area_count = \
                        get_data_from_fits(PATH + dir_name + "\\" + fits_file)
                    write_csv(img, time_record, num_of_area, area_count, "C", i)
        for dir_name in positive_test:
            for fits_file in get_files_path(PATH + dir_name):
                if db.select(dir_name) == "X" and np.random.random() <= 1.:
                    img, time_record, num_of_area, area_count = \
                        get_data_from_fits(PATH + dir_name + "\\" + fits_file)
                    write_csv(img, time_record, num_of_area, area_count, "X", i, is_train=False)
                elif db.select(dir_name) == "M" and np.random.random() <= 1.:
                    img, time_record, num_of_area, area_count = \
                        get_data_from_fits(PATH + dir_name + "\\" + fits_file)
                    write_csv(img, time_record, num_of_area, area_count, "M", i, is_train=False)
                elif db.select(dir_name) == "C" and np.random.random() <= 0.2:
                    img, time_record, num_of_area, area_count = \
                        get_data_from_fits(PATH + dir_name + "\\" + fits_file)
                    write_csv(img, time_record, num_of_area, area_count, "C", i, is_train=False)
        for dir_name in negative_train:
            for fits_file in get_files_path(PATH + dir_name):
                if np.random.random() <= 0.2:
                    img, time_record, num_of_area, area_count = \
                        get_data_from_fits(PATH + dir_name + "\\" + fits_file)
                    write_csv(img, time_record, num_of_area, area_count, "N", i, is_positive=False)
        for dir_name in negative_test:
            for fits_file in get_files_path(PATH + dir_name):
                if np.random.random() <= 0.2:
                    img, time_record, num_of_area, area_count = \
                        get_data_from_fits(PATH + dir_name + "\\" + fits_file)
                    write_csv(img, time_record, num_of_area, area_count, "N", i, is_positive=False, is_train=False)


main_work()
