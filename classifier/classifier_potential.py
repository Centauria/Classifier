import numpy as np
import utils
import classifier


class PotentialFunctions:
    @staticmethod
    def exponential(alpha=1):
        return lambda x, y: np.exp(-alpha * np.sum((x - y) ** 2))
    
    @staticmethod
    def cauchy(alpha=1):
        return lambda x, y: 1 / (1 + alpha * np.sum((x - y) ** 2))


class PotentialClassifier(classifier.AbstractClassifier):
    
    def __init__(self, X, y, classes: iter = None,
                 potential_function=PotentialFunctions.exponential()):
        self.X = np.array(X)
        self.y = np.array(y)
        self.W = None
        classes = classes or set(y)
        self.class_binder = utils.Binder.create_standard_binder(classes)
        self.data_type = lambda index: self.class_binder.infer(self.y[index])
        self.potential_function = potential_function
        self.initialize()
    
    def initialize(self):
        data_num, data_dim = self.X.shape
        assert data_num == len(self.y), 'Data length not match'
        
        potential = np.zeros((data_num, data_num))
        for i in range(data_num):
            for j in range(data_num):
                potential[i, j] = self.potential_function(self.X[i, :], self.X[j, :])
        
        point_flag = np.zeros((data_num, 1))
        point_potential = np.zeros((data_num, len(self.class_binder.input_names)))
        i = 0
        while i < data_num:
            if point_potential[i, self.data_type(i)] == np.max(np.squeeze(point_potential[i, :])) \
                    and point_potential[i, self.data_type(i)] != 0:
                i += 1
            else:
                point_flag[i] += 1
                for j in range(data_num):
                    point_potential[j, self.data_type(i)] += potential[i, j]
                i = 0
        self.W = point_flag
        return point_flag
    
    def evaluate(self, test_data: np.ndarray):
        train_len, train_dim = self.X.shape
        test_len, test_dim = test_data.shape
        assert train_dim == test_dim, 'Data dimension not match'
        potential = np.zeros((test_len, train_len))
        for i in range(test_len):
            for j in range(train_len):
                potential[i, j] = self.potential_function(test_data[i, :], self.X[j, :])
        
        test_potential = np.zeros((test_len, len(self.class_binder.input_names)))
        for i in range(test_len):
            for j in range(train_len):
                test_potential[i, self.data_type(j)] += self.W[j] * potential[i, j]

        test_type = np.zeros((test_len, 1), dtype=np.object)
        for i in range(test_len):
            height = np.max(test_potential[i, :])
            test_flag = np.argmax(test_potential[i, :])
            test_type[i] = self.class_binder.refer(test_flag)
        return test_type
