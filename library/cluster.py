import networkx as nx
import pandas as pd


def cluster_number(df, id_column, suffix_1, suffix_2):
    """
    Takes dataframe of matches with two id columns and assigns
    a cluster number to the dataframe based on the unique id pairings.

    Parameters
    ----------
    df: pandas.DataFrame
        DataFrame to add new column 'Cluster_Number' to.
    id_column: str
        ID column that should be common to both DataFrames (excluding
        suffixes).
    suffix_1: str
        Suffix used for id_column in first DataFrame.
    suffix_2: str
        Suffix used for id_column in second DataFrame.

    Raises
    ------
    TypeError
        if variables 'id'+suffix_1 or 'id_2'+suffix_2 are not strings.

    Returns
    ------
    df: pandas.DataFrame
        dataframe with Cluster_Number added

    Example
    --------
    >>> import pandas as pd
    >>> import numpy as np
    >>> import networkx as nx
    >>> df = pd.DataFrame({"id_1":["C1","C2","C3","C4","C5","C6"],
    ...                    "id_2":["P1","P2","P2","P3","P1","P6"]})
    >>> df.head(n=6)
      id_1 id_2
    0   C1   P1
    1   C2   P2
    2   C3   P2
    3   C4   P3
    4   C5   P1
    5   C6   P6
    >>> df = cluster_number(df = df, id_column='id', suffix_1="_1", suffix_2="_2")
    >>> df.head(n=6)
      id_1 id_2  Cluster_Number
    0   C1   P1               1
    1   C2   P2               2
    2   C3   P2               2
    3   C4   P3               3
    4   C5   P1               1
    5   C6   P6               4
    """
    id_1 = id_column + suffix_1
    id_2 = id_column + suffix_2
    if not ((isinstance(id_1, str)) and (isinstance(id_2, str))):
        raise TypeError("ID variables must be strings")
    df_cluster = df[[id_1, id_2]].copy()
    g = nx.from_edgelist(df_cluster.to_numpy().tolist())
    results = []
    for i, item in enumerate(list(nx.connected_components(g))):
        for ids in item:
            results.append([ids, i + 1])
    results_df = pd.DataFrame(results, columns=[id_column, "Cluster_Number"])
    df_merged = df.merge(
        results_df, how="inner", left_on=id_1, right_on=id_column
    ).drop([id_column], axis=1)
    return df_merged
