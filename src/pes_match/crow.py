import glob
import os
import pandas as pd
import numpy as np
from pes_match.cluster import cluster_number
from pes_match.parameters import CLERICAL_PATH, CLERICAL_VARIABLES


def collect_uniques(df, id_1, id_2, match_type):
    """
    Collects unique matches from a set of matches, removing all non-unique cases.

    Parameters
    ----------
    df: pandas.DataFrame
        The dataframe to which the function is applied.
    id_1: str
        ID column in first DataFrame (including suffix).
    id_2: str
        ID column in second DataFrame (including suffix).
    match_type: str
        Indicator that is added to specify which stage the matches were made on.

    Returns
    -------
    pandas.DataFrame
        Pandas dataframe with non-unique matches removed and indicator column appended

    Example
    --------
    >>> import pandas as pd
    >>> import numpy as np
    >>> df = pd.DataFrame({"id_1":["A1","A2","A3","A4","A5","A6"],
    ...                    "id_2":["B1","B2","B3","B3","B4","B5"]})
    >>> df.head(n=6)
      id_1 id_2
    0   A1   B1
    1   A2   B2
    2   A3   B3
    3   A4   B3
    4   A5   B4
    5   A6   B5
    >>> collect_uniques(df, id_1='id_1', id_2='id_2', match_type='Stage_X_Matchkeys')
      id_1 id_2  CLERICAL         Match_Type
    0   A1   B1         0  Stage_X_Matchkeys
    1   A2   B2         0  Stage_X_Matchkeys
    2   A5   B4         0  Stage_X_Matchkeys
    3   A6   B5         0  Stage_X_Matchkeys
    """
    if not ((isinstance(id_1, str)) and (isinstance(id_2, str)) and
            (isinstance(match_type, str))):
        raise TypeError("id_1, id_2 and match_type must be strings")
    pd.options.mode.chained_assignment = None
    df["ID_count_1"] = df.groupby([id_1])[id_2].transform("count")
    df["ID_count_2"] = df.groupby([id_2])[id_1].transform("count")
    df["CLERICAL"] = np.where(((df["ID_count_1"] > 1) | (df["ID_count_2"] > 1)), 1, 0)
    df = df[df["CLERICAL"] == 0].drop(["ID_count_1", "ID_count_2"], axis=1)
    df["CLERICAL"] = df["CLERICAL"].astype(np.int32)
    df["Match_Type"] = match_type
    df = df.reset_index(drop=True)
    return df


def collect_conflicts(df, id_1, id_2):
    """
    Collects non-unique matches from a set of matches, removing all unique cases.

    Parameters
    ----------
    df: pandas.DataFrame
        The dataframe to which the function is applied.
    id_1: str
        ID column in first DataFrame (including suffix).
    id_2: str
        ID column in second DataFrame (including suffix).

    Returns
    -------
    pandas.DataFrame
        Pandas dataframe with unique matches removed

    Example
    --------
    >>> import pandas as pd
    >>> import numpy as np
    >>> df = pd.DataFrame({"id_1":["A1","A2","A3","A4","A5","A6"],
    ...                    "id_2":["B1","B2","B3","B3","B4","B5"]})
    >>> df.head(n=6)
      id_1 id_2
    0   A1   B1
    1   A2   B2
    2   A3   B3
    3   A4   B3
    4   A5   B4
    5   A6   B5
    >>> collect_conflicts(df, id_1='id_1', id_2='id_2')
      id_1 id_2  CLERICAL
    0   A3   B3         1
    1   A4   B3         1
    """
    if not ((isinstance(id_1, str)) and (isinstance(id_2, str))):
        raise TypeError("id_1 and id_2 must be strings")
    pd.options.mode.chained_assignment = None
    df["ID_count_1"] = df.groupby([id_1])[id_2].transform("count")
    df["ID_count_2"] = df.groupby([id_2])[id_1].transform("count")
    df["CLERICAL"] = np.where(((df["ID_count_1"] > 1) | (df["ID_count_2"] > 1)), 1, 0)
    df = df[df["CLERICAL"] == 1].drop(["ID_count_1", "ID_count_2"], axis=1)
    df["CLERICAL"] = df["CLERICAL"].astype(np.int32)
    df = df.reset_index(drop=True)
    return df


def crow_output_updater(output_df, id_column, source_column, suffix_1, suffix_2, match_type):
    """
    Returns the outputs of CROW in a pairwise linked format.
    Only matched pairs are retained.

    Parameters
    ----------
    output_df: pandas.DataFrame
        The dataframe containing CROW matched output
    id_column: str
        Name of record_id column in CROW matched output
    source_column: str
        Name of column in CROW matched output identifying which
        data source the record is from
    suffix_1: str
        Suffix used for the first data source.
    suffix_2: str
        Suffix used for the second data source.
    match_type: str
        indicator to say which stage matches were made at

    Return
    -------
    df: pandas.DataFrame
        CROW matches in pairwise format

    Example
    -------
    >>> import pandas as pd
    >>> import numpy as np

    >>> df = pd.DataFrame({"puid": ["A1", "B1", "A2", "B2", "B3", "A4", "B4"],
    ...                  "Cluster_Number": [1, 1, 2, 2, 2, 3, 3],
    ...                  "Match": ["A1,B1", "A1,B1", "A2,B2,B3", "A2,B2,B3",
    ...                  "A2,B2,B3", "No match in cluster", "No match in cluster"],
    ...                  "Source_Dataset": ["_cen", "_pes", "_cen", "_pes",
    ...                  "_pes", "_cen", "_pes"]})
    >>> df
      puid  Cluster_Number                Match Source_Dataset
    0   A1               1                A1,B1           _cen
    1   B1               1                A1,B1           _pes
    2   A2               2             A2,B2,B3           _cen
    3   B2               2             A2,B2,B3           _pes
    4   B3               2             A2,B2,B3           _pes
    5   A4               3  No match in cluster           _cen
    6   B4               3  No match in cluster           _pes
    >>> df_updated = crow_output_updater(output_df = df, id_column = 'puid',
    ...                                  source_column = 'Source_Dataset',
    ...                                  suffix_1 = '_cen', suffix_2 = '_pes',
    ...                                  match_type = 'Stage_1_Conflicts')
    >>> df_updated
      puid_cen puid_pes         Match_Type  CLERICAL  MK
    0       A1       B1  Stage_1_Conflicts         1   0
    1       A2       B2  Stage_1_Conflicts         1   0
    2       A2       B3  Stage_1_Conflicts         1   0
    """

    # Select required columns and only keep clusters containing matches
    df = output_df
    df = df[df["Match"] != "No match in cluster"][[id_column, source_column, "Match"]]
    df = df.rename(columns={id_column: "Record_1", source_column: "Source_Dataset_1"})

    # Create lookup of ID to Source Dataset to use later
    lookup = df[["Record_1", "Source_Dataset_1"]]
    lookup = lookup.rename(
        columns={"Record_1": "Record_2", "Source_Dataset_1": "Source_Dataset_2"}
    )

    # Remove trailing commas and convert to lists
    df["Match"] = df["Match"].str.rstrip(",")
    df["Record_2"] = df["Match"].str.split(",")
    df.drop(["Match"], axis=1, inplace=True)

    # Explode to get all combinations of matched pairs
    df = df.explode("Record_2")

    # Types
    df["Record_1"] = df["Record_1"].astype("str")
    df["Record_2"] = df["Record_2"].astype("str")
    lookup["Record_2"] = lookup["Record_2"].astype("str")

    # Join on Source Dataset for Record_2
    df = pd.merge(df, lookup, on="Record_2", how="left")

    # Reorder ID columns to identify all duplicates (including cross duplicates)
    df["Record_1_FINAL"] = np.where(
        df["Source_Dataset_1"] == suffix_1, df["Record_1"], df["Record_2"]
    )
    df["Record_2_FINAL"] = np.where(
        df["Source_Dataset_2"] == suffix_2, df["Record_2"], df["Record_1"]
    )

    # Remove duplicate (df1 to df1 and/or df2 to df2) matches
    df = df[~(df.Source_Dataset_1 == df.Source_Dataset_2)]
    df.drop(
        ["Source_Dataset_1", "Source_Dataset_2", "Record_1", "Record_2"],
        axis=1,
        inplace=True,
    )

    # Remove dups, rename columns and save
    df = df[["Record_1_FINAL", "Record_2_FINAL"]].drop_duplicates()
    df = df.rename(
        columns={
            "Record_1_FINAL": id_column + suffix_1,
            "Record_2_FINAL": id_column + suffix_2,
        }
    )
    df.reset_index(drop=True, inplace=True)

    # Extra Flags
    df["Match_Type"], df["CLERICAL"], df["MK"] = [match_type, 1, 0]
    return df


def combine_crow_results(stage):
    """
    Takes all matches made in CROW from a chosen stage and combines
    them into a single pandas DataFrame. All matching in CROW for
    the chosen stage must be completed before running this function.

    Parameters
    ----------
    stage: str
        Chosen stage of matching e.g., 'Stage_1'. The function will look inside CLERICAL_PATH and
        combine all clerically matched CSV files that contain this string. File names for completed
        matches must also end in '_DONE.csv', otherwise they will not be included in the final set of
        combined clerical matches.

    Returns
    -------
    pandas.DataFrame
        Pandas dataframe with all clerically matched records from a selected stage combined.
    """
    if not isinstance(stage, str):
        raise TypeError("stage must be a string")
    if not os.path.exists(CLERICAL_PATH):
        os.makedirs(CLERICAL_PATH)
    all_files = glob.glob(os.path.join(CLERICAL_PATH, "*.csv"))
    completed_files = []
    for filename in all_files:
        if stage in filename:
            if filename.endswith("_DONE.csv"):
                df = pd.read_csv(filename, index_col=None, iterator=False, header=0)
                completed_files.append(df)
    assert len(completed_files) > 0, f"No completed clerical matching files" \
                                     f" (ending with _DONE) found from {stage}"
    df = pd.concat(completed_files, axis=0, ignore_index=True)
    return df


def remove_large_clusters(df, n):
    """
    Filters out clusters containing n or more unique records. This
    can be required if clusters are too large for the CROW system.

    Parameters
    ----------
    df: pandas.DataFrame
        DataFrame containing all clusters ready for CROW.
    n: int
        Minimum size of clusters that will be removed.

    See Also
    --------
    save_for_crow

    Returns
    -------
    pandas.DataFrame
        Pandas dataframe with clusters >= size n removed.

    Example
    -------
    >>> import pandas as pd
    >>> df = pd.DataFrame({"puid": ["A1", "B1", "A2", "B2", "B3", "A4", "B4"],
    ...                  "Cluster_Number": [1, 1, 2, 2, 2, 3, 3],
    ...                  "Source_Dataset": ["_cen", "_pes", "_cen", "_pes",
    ...                  "_pes", "_cen", "_pes"]})
    >>> df
      puid  Cluster_Number Source_Dataset
    0   A1               1           _cen
    1   B1               1           _pes
    2   A2               2           _cen
    3   B2               2           _pes
    4   B3               2           _pes
    5   A4               3           _cen
    6   B4               3           _pes
    >>> df = remove_large_clusters(df, n=3)
    >>> df
      puid  Cluster_Number Source_Dataset
    0   A1               1           _cen
    1   B1               1           _pes
    2   A4               3           _cen
    3   B4               3           _pes
    """
    if not isinstance(n, int):
        raise TypeError("n must be an integer")
    df["Size"] = df.groupby(["Cluster_Number"])["Cluster_Number"].transform("count")
    df = df[df.Size < n].drop(["Size"], axis=1).reset_index(drop=True)
    return df


def save_for_crow(df, id_column, suffix_1, suffix_2, file_name, no_of_files=1):
    """
    Takes candidate matches, updates their format ready for CROW
    and then saves them. Split matches into multiple files if desired.
    Large clusters (size 12+) that are too big for CROW are removed.

    Parameters
    ----------
    df: pandas.DataFrame
        DataFrame containing all candidate pairs ready for CROW.
    id_column: str
        Name of record_id column in CROW candidates.
    suffix_1: str
        Suffix used for the first data source.
    suffix_2: str
        Suffix used for the second data source.
    file_name: str
        Name of file that will be saved. If multiple files are
        saved, each file will have a different suffix
        e.g. "_1", "_2", etc.
    no_of_files: int, default = 1
        Number of csv files that the output will be split into.

    See Also
    --------
    cluster_number
    remove_large_clusters
    split_save
    """
    if not ((isinstance(id_column, str)) and (isinstance(suffix_1, str)) and
            (isinstance(suffix_2, str)) and (isinstance(file_name, str))):
        raise TypeError("id_column, file_name and suffixes must be strings")

    crow_variables = CLERICAL_VARIABLES
    df = cluster_number(df, id_column=id_column, suffix_1=suffix_1, suffix_2=suffix_2)
    df = remove_large_clusters(df, n=12)

    crow_records_1 = df[
        [var + suffix_1 for var in crow_variables] + ["Cluster_Number"]
    ].drop_duplicates()
    crow_records_2 = df[
        [var + suffix_2 for var in crow_variables] + ["Cluster_Number"]
    ].drop_duplicates()
    crow_records_1.columns = crow_records_1.columns.str.replace(
        suffix_1, "", regex=True
    )
    crow_records_2.columns = crow_records_2.columns.str.replace(
        suffix_2, "", regex=True
    )
    crow_records_1["Source_Dataset"] = suffix_1
    crow_records_2["Source_Dataset"] = suffix_2
    crow_input = pd.concat([crow_records_1, crow_records_2], axis=0).sort_values(
        ["Cluster_Number", "Source_Dataset"]
    )
    split_save(crow_input, file_name=file_name, no_of_files=no_of_files)


def split_save(df, file_name, no_of_files):
    """
    Splits clusters (that are already in a format ready for
    CROW) into multiple smaller files.

    Parameters
    ----------
    df: pandas.DataFrame
        DataFrame containing all clusters ready for CROW.
    file_name: str
        Name of files that will be saved. Each file will have a
        different suffix e.g. "_1", "_2", etc.
    no_of_files: int
        Number of csv files that the output will be split into.

    See Also
    --------
    save_for_crow
    """
    if not ((isinstance(file_name, str)) and (isinstance(no_of_files, int))):
        raise TypeError("file_name must be a string, no_of_files must be an integer")
    clusters_split = np.array_split(df["Cluster_Number"].unique(), no_of_files)
    for i, group in enumerate(clusters_split):
        df_split = df[
            df["Cluster_Number"].isin(list(group))
        ]
        df_split.to_csv(
            CLERICAL_PATH + file_name + "_" + str(i + 1) + ".csv",
            header=True,
            index=False,
        )
