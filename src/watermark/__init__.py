import os

import seaborn as sns

# _ROOT = os.path.dirname(
#     os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
_ROOT = os.path.dirname(os.path.abspath(os.path.dirname('__file__')))

def get_data_path(path):
    return os.path.join(_ROOT, 'data', path)


def get_queries_path(path):
    return os.path.join(_ROOT, 'data/queries', path)


def get_lib_path(path):
    return os.path.join(_ROOT, 'lib', path)


def get_models_path(path):
    return os.path.join(_ROOT, 'models', path)


def get_docs_path(path):
    return os.path.join(_ROOT, 'docs', path)


def get_color_palette(size: int, name: str = 'husl'):
    return list(sns.color_palette(name, size).as_hex())


color_pallete = {
    'generic_gradient':
    ['#E10F80', '#FF4568', '#FF7554', '#FFA349', '#FFCF51', '#F9F871'],
    'matching_gradient':
    ['#E10F80', '#B249C2', '#3D6FE9', '#0085E9', '#008FC5', '#00918C']
}
