import pandas as pd
from watermark.interfaces.transformer import Transformer
from watermark.utils.helper_functions import check_integrity

import logging
import sys

import numpy as np
import pandas as pd
from unidecode import unidecode


class Dropper(Transformer):

    def __init__(self, drop_columns: list = None):
        check_integrity(drop_columns, list)
        self.drop_columns = drop_columns

    def transform(self, X):
        X = X.copy()
        X = X.drop(columns=self.drop_columns)
        return X


class Renamer(Transformer):

    def __init__(self, rename_meta: dict = None):
        check_integrity(rename_meta, dict)
        self.rename_meta = rename_meta

    def transform(self, X):
        X = X.copy()
        X = X.rename(columns=self.rename_meta)
        return X


class Binner(Transformer):

    def __init__(self,
                 bins_cut_meta: dict = None,
                 bins_qcut_meta: dict = None,
                 bins_other_meta: dict = None):
        check_integrity(bins_cut_meta, dict)
        check_integrity(bins_qcut_meta, dict)
        check_integrity(bins_other_meta, dict)
        self.bins_cut_meta = bins_cut_meta
        self.bins_qcut_meta = bins_qcut_meta
        self.bins_other_meta = bins_other_meta

    def transform(self, X):
        X = X.copy()
        for column, bins in self.bins_cut_meta.items():
            X[column + '_categ'] = pd.cut(X[column],
                                          bins=bins,
                                          include_lowest=True)
        for column, q in self.bins_qcut_meta.items():
            X[column + '_categ'] = pd.qcut(X[column], q=q, precision=1)
        for var, meta in self.bins_other_meta.items():
            X[meta['var_name']] = pd.cut(X[var],
                                         bins=meta['bins'],
                                         labels=meta['bins_labels'],
                                         include_lowest=True)
        return X


class MinimumPercentageFilter(Transformer):

    def __init__(self, minimum_percentage_meta: dict = None):
        check_integrity(minimum_percentage_meta, dict)
        self.minimum_percentage_meta = minimum_percentage_meta

    def transform(self, X):
        X = X.copy()
        if len(self.minimum_percentage_meta) > 0:
            for col in self.minimum_percentage_meta.keys():
                aux = (X[col].value_counts().index)[(
                    X[col].value_counts() >
                    (self.minimum_percentage_meta[col] *
                     pd.notnull(X[col]).sum()))]
                X[col] = X[col].apply(lambda x: x if x in aux else 'other')
        return X


class Binarizer(Transformer):

    def __init__(self, binarizer_meta: dict = None):
        check_integrity(binarizer_meta, dict)
        self.binarizer_meta = binarizer_meta

    def transform(self, X):
        X = X.copy()
        for column, element in self.binarizer_meta.items():
            if len(X[column].unique()) != 2:
                logging.error(
                    'Cannot binarize a column that does not have exactly 2 categories! Error in {} column'
                    .format(column))
                sys.exit(1)
            X['{}_is_{}'.format(
                column,
                element)] = X[column].apply(lambda x: 1 if x == element else 0)
        return X


class Encoder(Transformer):

    def __init__(self, encoder_meta: dict = None):
        check_integrity(encoder_meta, dict)
        self.encoder_meta = encoder_meta

    def transform(self, X):
        X = X.copy()
        for var, meta in self.encoder_meta.items():
            if var not in X.columns.values.tolist():
                pass
            for unique_elem in X[var].unique().tolist():
                if unique_elem not in meta.keys():
                    meta[unique_elem] = unique_elem
            X[var] = X[var].map(meta)
        return X


class FeatureTransformer(Transformer):

    def __init__(self, transformer_meta: dict = None):
        check_integrity(transformer_meta, dict)
        self.transformer_meta = transformer_meta

    def _duplicated_flag(self, X: pd.DataFrame, feature_name: str,
                         columns: list):
        X = X.copy()
        X[feature_name] = X[columns].duplicated(keep=False).astype(int)
        return X

    def _no_show_flag(self, X: pd.DataFrame, feature_name: str, columns: list,
                      first_column_value: str, second_column_value: str):
        X.loc[(X[columns[0]] != first_column_value) &
              (X[columns[1]] == second_column_value), feature_name] = 1
        X[feature_name] = X[feature_name].fillna(0)
        return X

    def _add(self, X: pd.DataFrame, feature_name: str, columns: list):
        X = X.copy()
        X[feature_name] = X[columns[0]] + X[columns[1]]
        return X

    def _subtract(self, X: pd.DataFrame, feature_name: str, columns: list):
        X = X.copy()
        X[feature_name] = X[columns[0]] - X[columns[1]]
        return X

    def _round(self,
               X: pd.DataFrame,
               feature_name: str,
               columns: list,
               decimals: int = 0):
        X = X.copy()
        X[feature_name] = np.round(X[columns[0]], decimals=decimals)
        return X

    def _floor(self, X: pd.DataFrame, feature_name: str, columns: list):
        X = X.copy()
        X[feature_name] = np.floor(X[columns[0]])
        return X

    def _multiply(self, X: pd.DataFrame, feature_name: str, columns: list):
        X = X.copy()
        for column in columns:
            if column == columns[0]:
                X[feature_name] = X[column]
            else:
                X[feature_name] = X[feature_name] * X[column]
        return X

    def _divide(self, X: pd.DataFrame, feature_name: str, columns: list):
        X = X.copy()
        X[feature_name] = X[columns[0]] / X[columns[1]]
        return X

    def _fix_texts(self, X: pd.DataFrame, feature_name: str, columns: list):
        X = X.copy()
        for column in columns:
            X[column] = X[column].apply(
                lambda x: '_'.join(unidecode(str(x).lower()).split(' ')))
        return X

    def transform(self, X):
        X = X.copy()
        for name, iter in self.transformer_meta.items():
            transformation = getattr(self, '_{}'.format(name))
            for meta in iter.values():
                X = transformation(X=X,
                                   feature_name=meta['feature_name'],
                                   columns=meta['columns'],
                                   **meta['params'])
        return X


class CustomTransformer(Transformer):

    def __init__(self, custom_transformer_name: str = None):
        check_integrity(custom_transformer_name, str)
        self.custom_transformer_name = custom_transformer_name

    def _transform_example(self, X: pd.DataFrame):

        X = X.copy()

        return X

    def transform(self, X: pd.DataFrame):

        if hasattr(self, '_transform_{}'.format(self.custom_transformer_name)):

            transformation = getattr(
                self, '_transform_{}'.format(self.custom_transformer_name))

            X = transformation(X=X)

        return X


class MissingInputer(Transformer):

    def __init__(self,
                 default_numerical_missing_columns: list = None,
                 default_categorical_missing_columns: list = None,
                 other_missing_meta: dict = None,
                 default_fill_meta: dict = None):
        check_integrity(default_numerical_missing_columns, list)
        check_integrity(default_categorical_missing_columns, list)
        check_integrity(other_missing_meta, dict)
        check_integrity(default_fill_meta, dict)
        self.default_numerical_missing_columns = default_numerical_missing_columns
        self.default_categorical_missing_columns = default_categorical_missing_columns
        self.other_missing_meta = other_missing_meta
        self.default_fill_meta = default_fill_meta

    def transform(self, X):
        X = X.copy()
        if len(self.default_numerical_missing_columns) > 0:
            X[self.default_numerical_missing_columns] = X[
                self.default_numerical_missing_columns].fillna(
                    self.default_fill_meta['numerical'])
        if len(self.default_categorical_missing_columns) > 0:
            for column in self.default_categorical_missing_columns:
                if pd.api.types.is_categorical_dtype(X[column]):
                    X[column] = X[column].cat.add_categories([
                        self.default_fill_meta['categorical']
                    ]).fillna(self.default_fill_meta['categorical'])
                else:
                    X[column] = X[column].fillna(
                        self.default_fill_meta['categorical'])
        if len(self.other_missing_meta) > 0:
            for var, meta in self.other_missing_meta.items():
                if pd.api.types.is_categorical_dtype(X[var]):
                    X[var] = X[var].cat.add_categories([meta]).fillna(meta)
                else:
                    X[var] = X[var].fillna(meta)
        return X
