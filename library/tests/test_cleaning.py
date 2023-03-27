import pandas as pd
import numpy as np
import pytest
from library.cleaning import (alpha_name, change_types, clean_name, concat, derive_list,
                              derive_names, n_gram, pad_column, replace_vals, select, soundex)


@pytest.fixture(name="df")
def setup_fixture():
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
    result = alpha_name(df, input_col="forename", output_col="alpha_forename")
    pd.testing.assert_frame_equal(
        intended[["alpha_forename"]], result[["alpha_forename"]]
    )


def test_change_types(df):
    intended = pd.DataFrame({"sex": ["1", "2", "1", "1"]})
    result = change_types(df, input_cols="sex", types=str)
    pd.testing.assert_frame_equal(intended[["sex"]], result[["sex"]])
    intended = pd.DataFrame({"sex": [1.0, 2.0, 1.0, 1.0]})
    result = change_types(df, input_cols="sex", types=np.float64)
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
            "forename_clean": ["CHARLIE", "RACHEL", "JHON", "99"],
            "puid": [1, 2, 3, 4],
            "hhid": [1, 1, 15, 15],
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
    pd.testing.assert_frame_equal(intended, result)


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


def test_n_gram(df):
    intended = pd.DataFrame({"fn_first_3": ["CHA", "RAC", "JHO", ""]})
    result = n_gram(
        df, input_col="forename", output_col="fn_first_3", missing_value="", n=3
    )
    pd.testing.assert_frame_equal(intended[["fn_first_3"]], result[["fn_first_3"]])

    intended = pd.DataFrame({"sn_last_2": ["IE", "EL", "ON", ""]})
    result = n_gram(
        df, input_col="forename", output_col="sn_last_2", missing_value="", n=-2
    )
    pd.testing.assert_frame_equal(intended[["sn_last_2"]], result[["sn_last_2"]])


def test_pad_column(df):
    intended = pd.DataFrame({"hhid_pad": ["00001", "00001", "00015", "00020"]})
    result = pad_column(df, input_col="hhid", output_col="hhid_pad", length=5)
    pd.testing.assert_frame_equal(intended[["hhid_pad"]], result[["hhid_pad"]])


def test_replace_vals(df):
    intended = pd.DataFrame(
        {
            "forename": ["Charlie", "RacH!el", "JHON", "99"],
            "surname": ["Smith", "Thompson", "99", "Jones"],
        }
    )
    result = replace_vals(df, subset=["forename", "surname"], dic={"99": ""})
    pd.testing.assert_frame_equal(
        intended[["forename", "surname"]], result[["forename", "surname"]]
    )

    intended = pd.DataFrame({"sex": ["MALE", "FEMALE", "MALE", "MALE"]})
    result = replace_vals(df, subset=["sex"], dic={"MALE": 1, "FEMALE": 2})
    pd.testing.assert_frame_equal(intended[["sex"]], result[["sex"]])


def test_select(df):
    intended = pd.DataFrame(
        {
            "forename": ["Charlie", "RacH!el", "JHON", ""],
            "puid": [1, 2, 3, 4],
            "hhid": [1, 1, 15, 20],
        }
    )
    result = select(df, columns=["forename", "puid", "hhid"])
    pd.testing.assert_frame_equal(intended, result)


def test_soundex(df):
    intended = pd.DataFrame({"surname_sdx": ["S530", "T512", "", "J520"]})
    result = soundex(
        df, input_col="surname", output_col="surname_sdx", missing_value=""
    )
    pd.testing.assert_frame_equal(intended[["surname_sdx"]], result[["surname_sdx"]])
