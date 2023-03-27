import pandas as pd
import pytest
from library.matching import (age_diff_filter, age_tolerance, get_assoc_candidates,
                              get_residuals, mult_match, run_single_matchkey, std_lev, std_lev_filter)


@pytest.fixture(name="df")
def setup_fixture():
    test = pd.DataFrame(
        {
            'puid_1': [1, 2, 3, 4, 5],
            'puid_2': [21, 22, 23, 24, 25],
            'hhid_1': [1, 1, 1, 1, 1],
            'hhid_2': [2, 2, 2, 2, 2],
            'name_1': ['CHARLIE', 'JOHN', 'STEVE', 'SAM', 'PAUL'],
            'name_2': ['CHARLES', 'JONTHON', 'STEPHEN', 'S', 'PAUL'],
            'age_1': [5, 17, 28, 55, 100],
            'age_2': [2, 16, 28, 65, 99],
        }
    )
    return test


def test_age_diff_filter(df):
    intended = pd.DataFrame(
        {
            'puid_1': [2, 3, 5],
            'puid_2': [22, 23, 25],
            'hhid_1': [1, 1, 1],
            'hhid_2': [2, 2, 2],
            'name_1': ['JOHN', 'STEVE', 'PAUL'],
            'name_2': ['JONTHON', 'STEPHEN', 'PAUL'],
            'age_1': [17, 28, 100],
            'age_2': [16, 28, 99],
        }
    )
    result = age_diff_filter(df, age_1="age_1", age_2="age_2")
    pd.testing.assert_frame_equal(intended, result)


def test_age_tolerance():
    intended = True
    result = age_tolerance(5, 5)
    assert intended == result

    intended = False
    result = age_tolerance(5, 2)
    assert intended == result

    intended = True
    result = age_tolerance(25, 28)
    assert intended == result

    intended = False
    result = age_tolerance(25, 30)
    assert intended == result

    intended = True
    result = age_tolerance(55, 59)
    assert intended == result


def test_get_assoc_candidates():
    intended_1 = pd.DataFrame(
        {
            'puid_1': [2, 3, 4],
            'hhid_1': [1, 1, 1],
            'name_1': ['JOHN', 'STEVE', 'SAM'],
            'hhid_2': [2, 2, 2],
        }
    )
    intended_2 = pd.DataFrame(
        {
            'puid_2': [22, 23, 24],
            'hhid_2': [2, 2, 2],
            'name_2': ['JON', 'STEPHEN', 'SAMANTHA'],
            'hhid_1': [1, 1, 1],
        }
    )
    test_1 = pd.DataFrame(
        {
            'puid_1': [1, 2, 3, 4, 5],
            'hhid_1': [1, 1, 1, 1, 1],
            'name_1': ['CHARLIE', 'JOHN', 'STEVE', 'SAM', 'PAUL'],
        }
    )
    test_2 = pd.DataFrame(
        {
            'puid_2': [21, 22, 23, 24, 25],
            'hhid_2': [2, 2, 2, 2, 2],
            'name_2': ['CHARLES', 'JON', 'STEPHEN', 'SAMANTHA', 'PAUL'],
        }
    )
    test_matches = pd.DataFrame({'puid_1': [1, 5], 'puid_2': [21, 25]})
    result = get_assoc_candidates(test_1, test_2, suffix_1='_1', suffix_2='_2',
                                  matches=test_matches, person_id='puid', hh_id='hhid')
    pd.testing.assert_frame_equal(intended_1, result[0])
    pd.testing.assert_frame_equal(intended_2, result[1])


def test_get_residuals(df):
    intended_1 = pd.DataFrame({'puid_1': list(range(6, 11))})
    intended_2 = pd.DataFrame({'puid_2': list(range(26, 31))})
    test_all_records_1 = pd.DataFrame({'puid_1': list(range(1, 11))})
    test_all_records_2 = pd.DataFrame({'puid_2': list(range(21, 31))})
    result_1 = get_residuals(all_records=test_all_records_1, matched_records=df,
                             id_column='puid_1')
    result_2 = get_residuals(all_records=test_all_records_2, matched_records=df,
                             id_column='puid_2')
    pd.testing.assert_frame_equal(intended_1, result_1)
    pd.testing.assert_frame_equal(intended_2, result_2)


def test_mult_match():
    intended = pd.DataFrame(
        {
            'puid_1': [2, 3],
            'puid_2': [22, 23],
            'hhid_1': [2, 2],
            'hhid_2': [6, 6],
            'name_1': ['JOHN', 'STEVE'],
            'name_2': ['JONTHON', 'STEPHEN'],
        }
    )
    test = pd.DataFrame(
        {
            'puid_1': [1, 2, 3, 4, 5],
            'puid_2': [21, 22, 23, 24, 25],
            'hhid_1': [1, 2, 2, 3, 4],
            'hhid_2': [5, 6, 6, 7, 7],
            'name_1': ['CHARLIE', 'JOHN', 'STEVE', 'SAM', 'PAUL'],
            'name_2': ['CHARLES', 'JONTHON', 'STEPHEN', 'S', 'PAUL'],
        }
    )
    result = mult_match(test, hh_id_1='hhid_1', hh_id_2='hhid_2')
    pd.testing.assert_frame_equal(intended, result)


def test_run_single_matchkey():
    intended = pd.DataFrame(
        {
            'puid_1': [2,5],
            'hhid_1': [1, 1],
            'EA_1': [1, 2],
            'name_1': ['JOHN', 'PAUL'],
            'age_1': [17, 100],
            'puid_2': [22, 25],
            'hhid_2': [6, 7],
            'EA_2': [1, 2],
            'name_2': ['JOHN', 'PAUL'],
            'age_2': [16, 99],
            'MK': [1, 1],
        }
    )
    test_1 = pd.DataFrame(
        {
            'puid_1': [1, 2, 3, 4, 5],
            'hhid_1': [1, 1, 1, 1, 1],
            'EA_1': [1, 1, 2, 2, 2],
            'name_1': ['CHARLIE', 'JOHN', 'STEVE', 'SAM', 'PAUL'],
            'age_1': [5, 17, 28, 55, 100],
        }
    )
    test_2 = pd.DataFrame(
        {
            'puid_2': [21, 22, 23, 24, 25],
            'hhid_2': [5, 6, 6, 7, 7],
            'EA_2': [1, 1, 2, 2, 2],
            'name_2': ['CHARLES', 'JOHN', 'STEPHEN', 'S', 'PAUL'],
            'age_2': [2, 16, 28, 65, 99],
        }
    )
    result = run_single_matchkey(df1=test_1, df2=test_2, suffix_1='_1', suffix_2='_2',
                                 hh_id='hhid', level='EA', matchkey=1,
                                 variables=['name'], age_threshold=True)
    pd.testing.assert_frame_equal(intended, result)


def test_std_lev():
    intended = 0.7142857142857143
    result = std_lev('CHARLIE', 'CHARLES')
    assert intended == result

    intended = None
    result = std_lev('CHARLIE', None)
    assert intended == result

    intended = 1.0
    result = std_lev('CHARLIE', 'CHARLIE')
    assert intended == result


def test_std_lev_filter(df):
    intended = pd.DataFrame(
        {
            'puid_1': [1, 5],
            'puid_2': [21, 25],
            'hhid_1': [1, 1],
            'hhid_2': [2, 2],
            'name_1': ['CHARLIE', 'PAUL'],
            'name_2': ['CHARLES', 'PAUL'],
            'age_1': [5, 100],
            'age_2': [2, 99],
        }
    )
    result = std_lev_filter(df, column1="name_1", column2="name_2", threshold=0.7)
    pd.testing.assert_frame_equal(intended, result)
