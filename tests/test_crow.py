import pandas as pd
import numpy as np
import pytest
from library.crow import collect_uniques, collect_conflicts, crow_output_updater


@pytest.fixture(name="df")
def setup_fixture():
    test = pd.DataFrame(
        {
            "id_1": ["A1", "A2", "A3", "A4", "A5", "A6"],
            "id_2": ["B1", "B2", "B3", "B3", "B4", "B5"],
        }
    )
    return test


def test_collect_uniques(df):
    intended = pd.DataFrame(
        {
            "id_1": ["A1", "A2", "A5", "A6"],
            "id_2": ["B1", "B2", "B4", "B5"],
            "CLERICAL": [0, 0, 0, 0],
            "Match_Type": [
                "Auto_Matches",
                "Auto_Matches",
                "Auto_Matches",
                "Auto_Matches",
            ],
        }
    )
    intended["CLERICAL"] = intended["CLERICAL"].astype(np.int32)
    result = collect_uniques(df, id_1="id_1", id_2="id_2", match_type="Auto_Matches")
    pd.testing.assert_frame_equal(intended, result)


def test_collect_conflicts(df):
    intended = pd.DataFrame(
        {"id_1": ["A3", "A4"], "id_2": ["B3", "B3"], "CLERICAL": [1, 1]}
    )
    intended["CLERICAL"] = intended["CLERICAL"].astype(np.int32)
    result = collect_conflicts(df, id_1="id_1", id_2="id_2")
    pd.testing.assert_frame_equal(intended, result)


def test_crow_output_updater():
    test = pd.DataFrame(
        {
            "puid": ["A1", "B1", "A2", "B2", "B3", "A4", "B4"],
            "Cluster_Number": [1, 1, 2, 2, 2, 3, 3],
            "Match": [
                "A1,B1",
                "A1,B1",
                "A2,B2,B3",
                "A2,B2,B3",
                "A2,B2,B3",
                "No match in cluster",
                "No match in cluster",
            ],
            "Source_Dataset": ["_1", "_2", "_1", "_2", "_2", "_1", "_2"],
        }
    )
    intended = pd.DataFrame(
        {
            "puid_1": ["A1", "A2", "A2"],
            "puid_2": ["B1", "B2", "B3"],
            "Match_Type": [
                "Matchkey_Conflicts",
                "Matchkey_Conflicts",
                "Matchkey_Conflicts",
            ],
            "CLERICAL": [1, 1, 1],
            "MK": [0, 0, 0],
        }
    )
    result = crow_output_updater(
        output_df=test,
        id_column="puid",
        source_column="Source_Dataset",
        suffix_1="_1",
        suffix_2="_2",
        match_type="Matchkey_Conflicts",
    )
    pd.testing.assert_frame_equal(intended, result)
