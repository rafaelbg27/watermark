import joblib
from watermark import get_models_path
from abc import ABC, abstractmethod


class Model(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def fit(self):
        self.is_fitted_ = True
        return self

    @abstractmethod
    def predict(self, X):
        pass

    def evaluate(self, X, y):
        pass

    def save(self):
        joblib.dump(
            self, get_models_path('{}.joblib'.format(self.__class__.__name__)))

    def load(self):
        return joblib.load(
            get_models_path('{}.joblib'.format(self.__class__.__name__)))
