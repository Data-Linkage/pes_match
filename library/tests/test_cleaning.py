import pandas as pd
import numpy as np
import pytest
from library.cleaning import alpha_name, change_types
# clean_name,
# concat, derive_list, derive_names, n_gram, pad_column, replace_vals,
# select, soundex)


@pytest.fixture()
def df():
    test = pd.DataFrame(
        {"forename": ["Charlie", "RacH!el", "JHON"],
         "surname": ["Smith", "Thompson", ""],
         "sex": [1, 2, 1],
         "puid": [1, 2, 3],
         "hhid": [1, 1, 15]}
    )
    return test


def test_alphaname(df):
    intended = pd.DataFrame(
        {"alphaname": ["ACEHILR", "ACEHLR", "HJNO"]}
    )
    result = alpha_name(
        df, 'forename', 'alphaname'
    )
    pd.testing.assert_frame_equal(intended[['alphaname']], result[['alphaname']])


def test_change_types(df):
    intended = pd.DataFrame(
        {"sex": ["1", "2", "1"]}
    )
    result = change_types(
        df, 'sex', str
    )
    pd.testing.assert_frame_equal(intended[['sex']], result[['sex']])

