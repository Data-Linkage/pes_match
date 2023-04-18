import pandas as pd
from library.cluster import cluster_number


def test_cluster_number():
    test = pd.DataFrame(
        {
            "id_1": ["C1", "C2", "C3", "C4", "C5", "C6"],
            "id_2": ["P1", "P2", "P2", "P3", "P1", "P6"]
        }
    )
    intended = pd.DataFrame(
        {
            "id_1": ["C1", "C2", "C3", "C4", "C5", "C6"],
            "id_2": ["P1", "P2", "P2", "P3", "P1", "P6"],
            "Cluster_Number": [1, 2, 2, 3, 1, 4]
        }
    )
    result = cluster_number(df=test, id_column="id", suffix_1="_1", suffix_2="_2")
    pd.testing.assert_frame_equal(intended, result)
