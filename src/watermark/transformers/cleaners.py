import numpy as np
import pandas as pd

# from watermark.interfaces.transformer import Transformer
# from watermark.utils.helper_functions import check_integrity


class Cleaner(Transformer):

    def __init__(self,
                 variable_columns: list = None,
                 duplicate_columns: list = None):
        check_integrity(variable_columns, list)
        check_integrity(duplicate_columns, list)
        self.variable_columns = variable_columns
        self.duplicate_columns = duplicate_columns

    def transform(self, X):
        X = X.copy()[self.variable_columns]
        X = X.replace(r'^\s*$', np.nan, regex=True)
        X = X.applymap(lambda x: x.strip() if isinstance(x, str) else x)
        # drop duplicates if not empty list
        if self.duplicate_columns:
            X = X.drop_duplicates(subset=self.duplicate_columns)
        X = X.reset_index(drop=True)
        return X


class Filter(Transformer):

    def __init__(self,
                 filter_notnull_columns: list = None,
                 filter_custom_query_columns: list = None,
                 filter_other_meta: dict = None):

        check_integrity(filter_notnull_columns, list)
        check_integrity(filter_custom_query_columns, list)
        check_integrity(filter_other_meta, dict)
        self.filter_notnull_columns = filter_notnull_columns
        self.filter_custom_query_columns = filter_custom_query_columns
        self.filter_other_meta = filter_other_meta

    def transform(self, X):
        X = X.copy()
        if self.filter_notnull_columns:
            X = X.loc[pd.notnull(X[self.filter_notnull_columns]).all(1), :]
        if self.filter_other_meta:
            X = X.loc[(X[list(self.filter_other_meta)] == pd.Series(
                self.filter_other_meta)).all(axis=1)]
        if self.filter_custom_query_columns:
            for column in self.filter_custom_query_columns:
                X = X.query(column)
        X = X.reset_index(drop=True)
        return X