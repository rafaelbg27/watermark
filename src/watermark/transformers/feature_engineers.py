import pandas as pd
from watermark.interfaces.transformer import Transformer
from watermark.utils.helper_functions import check_integrity


class Selector(Transformer):

    def __init__(self, selection_drop_columns):
        check_integrity(selection_drop_columns, list)
        self.selection_drop_columns = selection_drop_columns

    def transform(self, X):
        X = X.copy()
        X = X.drop(columns=self.selection_drop_columns)
        return X


class Dumminizer(Transformer):

    def __init__(self, dummies_columns):
        check_integrity(dummies_columns, list)
        self.dummies_columns = dummies_columns

    def transform(self, X):
        X = X.copy()
        X = pd.get_dummies(X, columns=self.dummies_columns)
        return X


class Scaler(Transformer):

    def __init__(self, scale_meta: dict = None):
        check_integrity(scale_meta, dict)
        self.scale_meta = scale_meta

    def transform(self, X):
        X = X.copy()
        for scaler_name, meta in self.scale_meta.items():
            scaler = getattr(self, '_{}'.format(scaler_name))
            for col in meta['columns']:
                X[col] = scaler(X=X[col], **meta['params'])
        return X

    def _minmax(self, X: pd.Series, min: float = 0, max: float = 1):
        X = X.copy()
        return (X - X.min()) / (X.max() - X.min()) * (max - min) + min

    def _standard(self, X: pd.Series):
        X = X.copy()
        return (X - X.mean()) / X.std()
