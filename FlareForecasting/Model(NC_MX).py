import sys
import time

import keras
import numpy as np
import pandas as pd
from keras import Model
from keras.applications.vgg16 import VGG16
from keras.callbacks import ModelCheckpoint
from keras.layers import Conv2D, MaxPooling2D, Activation
from keras.layers import Flatten, Dense, Dropout, BatchNormalization
from keras.models import Sequential, load_model
from keras.optimizers import SGD
from sklearn.metrics import confusion_matrix
from tensorflow import set_random_seed

np.random.seed(11)
set_random_seed(12)


class Metric(object):
    def __init__(self, y_true, y_pred):
        self.__matrix = confusion_matrix(y_true, y_pred)

    def Matrix(self):
        return self.__matrix

    def TP(self):
        tp = np.diag(self.__matrix)
        return tp.astype(float)

    def TN(self):
        tn = self.__matrix.sum() - (self.FP() + self.FN() + self.TP())
        return tn.astype(float)

    def FP(self):
        fp = self.__matrix.sum(axis=0) - np.diag(self.__matrix)
        return fp.astype(float)

    def FN(self):
        fn = self.__matrix.sum(axis=1) - np.diag(self.__matrix)
        return fn.astype(float)

    def TPRate(self):
        return self.TP() / (self.TP() + self.FN() + sys.float_info.epsilon)

    def TNRate(self):
        return self.TN() / (self.TN() + self.FP() + sys.float_info.epsilon)

    def FPRate(self):
        return 1 - self.TNRate()

    def FNRate(self):
        return 1 - self.TPRate()

    def Accuracy(self):
        ALL = self.TP() + self.FP() + self.TN() + self.FN()
        RIGHT = self.TP() + self.TN()
        return RIGHT / (ALL + sys.float_info.epsilon)

    def Recall(self):
        return self.TP() / (self.TP() + self.FN() + sys.float_info.epsilon)

    def Precision(self):
        return self.TP() / (self.TP() + self.FP() + sys.float_info.epsilon)

    def TSS(self):
        return self.TPRate() - self.FPRate()

    def HSS(self):
        P = self.TP() + self.FN()
        N = self.TN() + self.FP()
        up = 2 * (self.TP() * self.TN() - self.FN() * self.FP())
        below = P * (self.FN() + self.TN()) + N * (self.TP() + self.FP())
        return up / (below + sys.float_info.epsilon)


class Read(object):
    def __init__(self, directory, order):
        def read_csv(name):
            return pd.read_csv(name, header=None, delimiter=",").values

        names = [directory + "/" + str(order) + "_positive_test.csv",
                 directory + "/" + str(order) + "_positive_train.csv",
                 directory + "/" + str(order) + "_negative_test.csv",
                 directory + "/" + str(order) + "_negative_train.csv"]
        self.__positive_test, self.__positive_train, \
        self.__negative_test, self.__negative_train = map(read_csv, names)

    def get_original_data(self):
        return self.__positive_test, self.__positive_train, \
               self.__negative_test, self.__negative_train


class Parse(object):
    def __init__(self, _positive_test, _positive_train, _negative_test, _negative_train, is_vgg):
        # is_vgg flag
        self.__is_vgg = is_vgg
        # return data
        self.__train_x, self.__train_y, self.__test_x, self.__test_y = [], [], [], []
        # class_weight data
        # [image_number, [AR]]
        self.__zero, self.__one = [0, []], [0, []]
        for line in _positive_test:
            if line[1] == 1:
                if self.__is_vgg is False:
                    self.__test_x.append(line[4:])
                else:
                    self.__test_x.append([line[4:], line[4:], line[4:]])
                self.__test_y.append(line[3])
        for line in _negative_test:
            if line[1] == 1:
                if self.__is_vgg is False:
                    self.__test_x.append(line[4:])
                else:
                    self.__test_x.append([line[4:], line[4:], line[4:]])
                self.__test_y.append(line[3])
        for line in _positive_train:
            if self.__is_vgg is False:
                self.__train_x.append(line[4:])
            else:
                self.__train_x.append([line[4:], line[4:], line[4:]])
            self.__train_y.append([line[2], line[3]])
        for line in _negative_train:
            if self.__is_vgg is False:
                self.__train_x.append(line[4:])
            else:
                self.__train_x.append([line[4:], line[4:], line[4:]])
            self.__train_y.append([line[2], line[3]])

    def __prepare_data(self):
        level_map = {"N": 0., "C": 0., "M": 1., "X": 1.}
        for indices in range(len(self.__train_y)):
            if level_map[self.__train_y[indices][1]] == 0:
                self.__zero[0] += 1
                self.__zero[1].append(self.__train_y[indices][0])
            elif level_map[self.__train_y[indices][1]] == 1:
                self.__one[0] += 1
                self.__one[1].append(self.__train_y[indices][0])
            self.__train_y[indices] = level_map[self.__train_y[indices][1]]
        for indices in range(len(self.__test_y)):
            self.__test_y[indices] = level_map[self.__test_y[indices]]

    def class_weight(self, zero=True, alpha=1., beta=1.):
        if zero:
            result = self.__zero[0] / 10000 * len(list(set(self.__zero[1]))) / 100 * alpha
            print("Zero percent:", result)
            return result
        else:
            result = self.__one[0] / 10000 * len(list(set(self.__one[1]))) / 100 * beta
            print("One percent:", result)
            return result

    def load_data(self):
        # prepare data
        self.__prepare_data()
        if self.__is_vgg is False:
            # process train_X
            self.__train_x = np.array(self.__train_x, dtype=np.float32)
            self.__train_x /= 4000
            self.__train_x = self.__train_x.reshape((self.__train_x.shape[0], 128, 128, 1))
            # process test_x
            self.__test_x = np.array(self.__test_x, dtype=np.float32)
            self.__test_x /= 4000
            self.__test_x = self.__test_x.reshape((self.__test_x.shape[0], 128, 128, 1))
        # else:
        #     # process train_X
        #     self.__train_x = np.array(self.__train_x, dtype=np.float32)
        #     self.__train_x /= 4000
        #     self.__train_x = self.__train_x.reshape((self.__train_x.shape[0], 128, 128, 3))
        #     # process test_x
        #     self.__test_x = np.array(self.__test_x, dtype=np.float32)
        #     self.__test_x /= 4000
        #     self.__test_x = self.__test_x.reshape((self.__test_x.shape[0], 128, 128, 3))
        # process y
        self.__train_y = keras.utils.to_categorical(self.__train_y, int(max(self.__train_y) + 1))
        self.__test_y = keras.utils.to_categorical(self.__test_y, int(max(self.__test_y) + 1))
        return self.__train_x, self.__train_y, self.__test_x, self.__test_y


class ConstructModel(object):
    def __init__(self, configure_maps):
        self.__configure_maps = configure_maps

    def normal(self):
        model = Sequential()
        model.add(Conv2D(64, kernel_size=(11, 11), input_shape=self.__configure_maps["1"]["input_shape"]))
        model.add(BatchNormalization())
        model.add(Activation('relu'))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Conv2D(64, (11, 11)))
        model.add(BatchNormalization())
        model.add(Activation('relu'))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Conv2D(64, (3, 3)))
        model.add(BatchNormalization())
        model.add(Activation('relu'))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Conv2D(64, (3, 3)))
        model.add(BatchNormalization())
        model.add(Activation('relu'))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Conv2D(64, (3, 3)))
        model.add(BatchNormalization())
        model.add(Activation('relu'))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Flatten())
        model.add(Dense(128))
        model.add(BatchNormalization())
        model.add(Dropout(0.5))
        model.add(Dense(64))
        model.add(BatchNormalization())
        model.add(Dropout(0.5))
        model.add(Dense(self.__configure_maps["num_of_classes"]))
        model.add(Activation('softmax'))

        model.compile(loss=keras.losses.categorical_crossentropy,
                      optimizer=SGD(lr=self.__configure_maps["1"]["learning_rate"],
                                    momentum=self.__configure_maps["1"]["momentum"],
                                    decay=self.__configure_maps["1"]["decay"],
                                    nesterov=self.__configure_maps["nesterov"]),
                      metrics=["accuracy"])
        return model

    # def vgg(self):
    #     model_vgg = VGG16(include_top=False, weights='imagenet',
    #                       input_shape=self.__configure_maps["2"]["input_shape"])
    #     for layer in model_vgg.layers:
    #         layer.trainable = False
    #     vgg = Flatten(name='flatten')(model_vgg.output)
    #     vgg = Dense(128, activation='relu', name='fc1')(vgg)
    #     vgg = (BatchNormalization())(vgg)
    #     vgg = Dense(self.__configure_maps["num_of_classes"],
    #                 activation='softmax')(vgg)
    #     model = Model(inputs=model_vgg.input, outputs=vgg, name='vgg16')
    #
    #     model.compile(loss=keras.losses.categorical_crossentropy,
    #                   optimizer=SGD(lr=self.__configure_maps["2"]["learning_rate"],
    #                                 momentum=self.__configure_maps["2"]["momentum"],
    #                                 decay=self.__configure_maps["2"]["decay"],
    #                                 nesterov=self.__configure_maps["nesterov"]),
    #                   metrics=['accuracy'])
    #     return model


class TrainModel(object):
    def __init__(self, conf):
        self.__conf = conf

    def train(self, move):
        reader = Read("./data", move)
        a, b, c, d = reader.get_original_data()
        constructor = ConstructModel(self.__conf)
        parser = Parse(a, b, c, d, self.__conf["is_vgg"])
        train_x, train_y, test_x, test_y = parser.load_data()

        if not self.__conf["is_vgg"]:
            # train normal
            model = constructor.normal()
            model.fit(train_x, train_y, batch_size=self.__conf["1"]["batch_size"],
                      epochs=self.__conf["1"]["epochs"], verbose=self.__conf["verbose"],
                      class_weight={0.: parser.class_weight(alpha=self.__conf["1"]["alpha"]),
                                    1.: parser.class_weight(False, beta=self.__conf["1"]["beta"])},
                      validation_data=(test_x, test_y),
                      callbacks=[ModelCheckpoint("./model/2classification/" + str(move) + ".h5",
                                                 monitor='val_loss', verbose=1, mode='min',
                                                 save_best_only=True, save_weights_only=False)])
            model = load_model("./model/2classification/" + str(move) + ".h5")
            y_true, y_pred = test_y, model.predict(test_x)
            return y_true.argmax(axis=1), y_pred.argmax(axis=1)
        # else:
        #     # train vgg
        #     model = constructor.vgg()
        #     model.fit(train_x, train_y, batch_size=self.__conf["2"]["batch_size"],
        #               epochs=self.__conf["2"]["epochs"], verbose=self.__conf["verbose"],
        #               class_weight={0.: parser.class_weight(alpha=self.__conf["2"]["alpha"]),
        #                             1.: parser.class_weight(False, beta=self.__conf["2"]["beta"])},
        #               validation_data=(test_x, test_y),
        #               callbacks=[ModelCheckpoint("./model/vgg/" + str(move) + ".h5",
        #                                          monitor='val_loss', verbose=1, mode='min',
        #                                          save_best_only=True, save_weights_only=False)])
        #     model = load_model("./model/vgg/" + str(move) + ".h5")
        #     y_true, y_pred = test_y, model.predict(test_x)
        #     return y_true.argmax(axis=1), y_pred.argmax(axis=1)


def Main(is_vgg):
    all_nums = 10
    std_file_name = "./logs/" + time.strftime("%Y_%b_%d_%H_%M_%S", time.gmtime()) + ".txt"
    sys.stdout = open(std_file_name, "w+")
    conf = {"num_of_classes": 2, "nesterov": True, "verbose": 2, "is_vgg": is_vgg,
            "1": {
                "batch_size": 16, "epochs": 80, "learning_rate": 1e-3,
                "momentum": 0.5, "decay": 5 * 1e-6, "alpha": 1, "beta": 30,
                "input_shape": (128, 128, 1),
            }
            # ,"2": {
            #     "batch_size": 16, "epochs": 80, "learning_rate": 4 * 1e-4,
            #     "momentum": 0.6, "decay": 1e-6, "alpha": 1., "beta": 40,
            #     "input_shape": (128, 128, 3),
            # }
            }
    all_metric = {"Recall": [0, 0], "Precision": [0, 0], "Accuracy": [0, 0],
                  "TSS": [0, 0], "HSS": [0, 0]}
    all_matrix = np.array([[0, 0], [0, 0]])
    for i in range(all_nums):
        trainer = TrainModel(conf)
        a, b = trainer.train(i)
        metric = Metric(a, b)
        print("Matrix:\n", metric.Matrix())
        print("Recall:", metric.Recall())
        print("Precision:", metric.Precision())
        print("Accuracy:", metric.Accuracy())
        print("TSS:", metric.TSS())
        print("HSS:", metric.HSS())
        sys.stdout.flush()

        all_matrix += metric.Matrix()
        all_metric["Recall"] += metric.Recall()
        all_metric["Precision"] += metric.Precision()
        all_metric["Accuracy"] += metric.Accuracy()
        all_metric["TSS"] += metric.TSS()
        all_metric["HSS"] += metric.HSS()

    print("\n-----------------------")
    print(all_matrix)
    for index in all_metric:
        print(index, np.array(all_metric[index]) / all_nums)


if __name__ == '__main__':
    Main(False)
