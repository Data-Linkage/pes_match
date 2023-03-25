import pandas as pd
import numpy as np
import pytest
from library.cleaning import (alpha_name, change_types, clean_name, concat, derive_list, derive_names)
# n_gram, pad_column, replace_vals, select, soundex)


@pytest.fixture()
def df(name="setup"):
    test = pd.DataFrame(
        {
            "forename": ["Charlie", "RacH!el", "JHON", ""],
            "surname": ["Smith", "Thompson", "", "Jones"],
            "sex": [1, 2, 1, 1],
            "puid": [1, 2, 3, 4],
            "hhid": [1, 1, 15, 20],
        }
    )
    return test


def test_alphaname(df):
    intended = pd.DataFrame({"alpha_forename": ["ACEHILR", "ACEHLR", "HJNO", ""]})
    result = alpha_name(df, "forename", "alpha_forename")
    pd.testing.assert_frame_equal(
        intended[["alpha_forename"]], result[["alpha_forename"]]
    )


def test_change_types(df):
    intended = pd.DataFrame({"sex": ["1", "2", "1", "1"]})
    result = change_types(df, "sex", str)
    pd.testing.assert_frame_equal(intended[["sex"]], result[["sex"]])
    intended = pd.DataFrame({"sex": [1.0, 2.0, 1.0, 1.0]})
    result = change_types(df, "sex", np.float64)
    pd.testing.assert_frame_equal(intended[["sex"]], result[["sex"]])


def test_clean_name(df):
    intended = pd.DataFrame(
        {"forename_clean_pes": ["CHARLIE", "RACHEL", "JHON", np.nan]}
    )
    result = clean_name(df, name_column="forename", suffix="_pes")
    pd.testing.assert_frame_equal(
        intended[["forename_clean_pes"]], result[["forename_clean_pes"]]
    )

    intended = pd.DataFrame(
        {"surname_clean_pes": ["SMITH", "THOMPSON", np.nan, "JONES"]}
    )
    result = clean_name(df, name_column="surname", suffix="_pes")
    pd.testing.assert_frame_equal(
        intended[["surname_clean_pes"]], result[["surname_clean_pes"]]
    )


def test_concat():
    test = pd.DataFrame(
        {
            "forename_clean": ["CHARLIE", "RACHEL", "JHON", np.nan, "C--W"],
            "surname_clean": ["SMITH", "THOMPSON", np.nan, np.nan, "EDWARDS"],
        }
    )
    intended = pd.DataFrame(
        {"fullname": ["CHARLIE-SMITH", "RACHEL-THOMPSON", "JHON", "", "C-W-EDWARDS"]}
    )
    result = concat(
        test,
        output_col="fullname",
        sep="-",
        columns=["forename_clean", "surname_clean"],
    )
    pd.testing.assert_frame_equal(intended[["fullname"]], result[["fullname"]])


def test_derive_list():
    test = pd.DataFrame(
        {
            "forename_clean": ["CHARLIE", "RACHEL", "JHON", "99"],
            "puid": [1, 2, 3, 4],
            "hhid": [1, 1, 15, 15],
        }
    )
    intended = pd.DataFrame(
        {
            "puid": [1, 2, 3, 4],
            "forename_list": [
                ["CHARLIE", "RACHEL"],
                ["CHARLIE", "RACHEL"],
                ["JHON", "99"],
                ["JHON", "99"],
            ],
        }
    )
    result = derive_list(
        test,
        partition_var="hhid",
        list_var="forename_clean",
        output_col="forename_list",
    )
    pd.testing.assert_frame_equal(
        intended[["puid", "forename_list"]], result[["puid", "forename_list"]]
    )


def test_derive_names():
    test = pd.DataFrame(
        {"fullname_1": ["CHARLIE W TOMLIN", "RACHEL SMITH", "", "JAMES"]}
    )
    intended = pd.DataFrame(
        {
            "fullname_1": ["CHARLIE W TOMLIN", "RACHEL SMITH", "", "JAMES"],
            "forename_1": ["CHARLIE", "RACHEL", np.NaN, "JAMES"],
            "middle_name_1": ["W", np.NaN, np.NaN, np.NaN],
            "last_name_1": ["TOMLIN", "SMITH", np.NaN, np.NaN],
        }
    )
    result = derive_names(test, clean_fullname_column="fullname_1", suffix="_1")
    pd.testing.assert_frame_equal(intended, result)
