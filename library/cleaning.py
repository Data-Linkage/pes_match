import re
import numpy as np
import jellyfish


def alpha_name(df, input_col, output_col):
    """
    Orders string columns alphabetically, after removing whitespace/special
    characters and setting strings to upper case.

    Parameters
    ----------
    df: pandas.DataFrame
        The dataframe to which the function is applied.
    input_col: str
        Name of column to be sorted alphabetically
    output_col: str
        Name of column to be output

    Returns
    -------
    pandas.DataFrame
        Pandas dataframe with output_col appended

    Example
    --------
    >>> import pandas as pd
    >>> import re
    >>> df = pd.DataFrame({'forename': ['Charlie']})
    >>> df['forename'].head(n=1)
    0    Charlie
    Name: forename, dtype: object
    >>> df = alpha_name(df, input_col='forename', output_col='alphaname')
    >>> df['alphaname'].head(n=1)
    0    ACEHILR
    Name: alphaname, dtype: object
    """
    df[input_col + "_cleaned"] = [re.sub(r"[^A-Za-z]+", "", s) for s in df[input_col]]
    df[output_col] = ["".join(sorted(x.upper())) for x in df[input_col + "_cleaned"]]
    df = df.drop([input_col + "_cleaned"], axis=1)
    return df


def change_types(df, input_cols, types):
    """
    Casts specific dataframe columns to a specified type.
    The function can either take a single column or a list of columns.

    Parameters
    ----------
    df : pandas.DataFrame
        The dataframe to which the function is applied.
    input_cols: str or list of str
        The subset of columns that are having their datatypes converted.
    types:
        The datatype that the column values will be converted into.

    Returns
    -------
    pandas.DataFrame
        Returns the complete dataframe with changes to the datatypes on specified
        columns.

    Example
    -------
    >>> import pandas as pd
    >>> df = pd.DataFrame({'number': [1]})
    >>> df.dtypes[0]
    dtype('int64')
    >>> df = change_types(df, input_cols='number', types='str')
    >>> df.dtypes[0]
    dtype('O')
    """
    if not isinstance(input_cols, list):
        input_cols = [input_cols]
    for col in input_cols:
        df[col] = df[col].astype(types)
    return df


def clean_name(df, name_column, suffix=""):
    """
    Derives a cleaned version of a column contained in a pandas dataframe.

    Parameters
    ----------
    df : pandas.DataFrame
        Input dataframe with name_column present
    name_column : str
        Name of column containing name as string type
    suffix : str, default = ""
        Optional suffix to append to name component column names

    Returns
    -------
    pandas.DataFrame
        clean_name returns the dataframe with a cleaned version of name_column.

    Example
    -------
    >>> import pandas as pd
    >>> import numpy as np
    >>> import re
    >>> df = pd.DataFrame({'Name': ['Charlie!']})
    >>> df.head(n=1)
           Name
    0  Charlie!
    >>> df = clean_name(df, name_column='Name', suffix='_cen')
    >>> df.head(n=1)
           Name Name_clean_cen
    0  Charlie!        CHARLIE
    """
    df[name_column] = df[name_column].replace(np.nan, "")
    df[name_column + "_clean" + suffix] = [
        " ".join(x.upper().split()) for x in df[name_column]
    ]
    df[name_column + "_clean" + suffix] = [
        re.sub(r"[^A-Za-z ]+", "", s) for s in df[name_column + "_clean" + suffix]
    ]
    df[name_column + "_clean" + suffix] = df[name_column + "_clean" + suffix].replace(
        "", np.nan
    )
    df[name_column] = df[name_column].replace("", np.nan)
    return df


def concat(df, columns, output_col, sep=" "):
    """
    Concatenates strings from specified columns into a single string and stores
    the new string value in a new column.

    Parameters
    ----------
    df: pandas.DataFrame
        Dataframe to which the function is applied.
    columns : list of strings, default = []
        The list of columns being concatenated into
        one string
    output_col : str
        The name, in string format, of the
        output column for the new concatenated
        strings to be stored in.
    sep : str, default = ' '
        This is the value used to separate the
        strings in the different columns when
        combining them into a single string.

    Returns
    -------
    pandas.DataFrame
        Returns dataframe with 'output_col' column
        containing the concatenated string.

    See Also
    --------
    replace_vals
        Uses regular expressions to replace values within dataframe columns.

    Example
    -------
    >>> import pandas as pd
    >>> import numpy as np
    >>> df = pd.DataFrame({'Forename': ['John'],
    ...                    'Surname': ['Smith']})
    >>> df.head(n=1)
      Forename Surname
    0     John   Smith
    >>> df = concat(df, columns=['Forename', 'Surname'], output_col='Fullname', sep=' ')
    >>> df.head(n=1)
      Forename Surname    Fullname
    0     John   Smith  John Smith
    """
    if columns is None:
        columns = []
    df = replace_vals(df, dic={"": np.NaN}, subset=columns)
    df[output_col] = df[columns].agg(sep.join, axis=1)
    df[output_col] = [" ".join(x.split(sep)) for x in df[output_col].str.strip()]
    df[output_col] = [sep.join(x.split()) for x in df[output_col]]
    df = replace_vals(df, dic={np.NaN: ""}, subset=columns)
    return df


def derive_list(df, partition_var, list_var, output_col):
    """
    Aggregate function: Collects list of values from one column after partitioning by
    another column. Results stored in a new column

    Parameters
    ----------
    df : pandas.DataFrame
        Input dataframe with partition_var and list_var present
    partition_var : str
        Name of column to partition on e.g. household ID
    list_var : str
        Variable to collect list of values over chosen partition e.g. names
    output_col: str
        Name of list column to be output

    Returns
    -------
    pandas.DataFrame
        derive_list returns the dataframe with additional column output_col

    Example
    -------
    >>> import pandas as pd
    >>> df = pd.DataFrame({'Forename': ['John', 'Steve', 'Charlie', 'James'],
    ...                    'Household': [1, 1, 2, 2]})
    >>> df.head(n=4)
      Forename  Household
    0     John          1
    1    Steve          1
    2  Charlie          2
    3    James          2
    >>> df = derive_list(df, partition_var='Household', list_var='Forename',
    ...                  output_col='Forename_List')
    >>> df.head(n=4)
      Forename  Household     Forename_List
    0     John          1     [John, Steve]
    1    Steve          1     [John, Steve]
    2  Charlie          2  [Charlie, James]
    3    James          2  [Charlie, James]
    """
    values_in_partition = df.groupby(partition_var)[list_var].agg(list).reset_index()
    values_in_partition.columns = [partition_var, output_col]
    df = df.merge(values_in_partition, on=partition_var, how="left")
    return df


def derive_names(df, clean_fullname_column, suffix=""):
    """
    Derives first name, middle name(s) and last name from
    a pandas dataframe column containing a cleaned fullname column.

    Parameters
    ----------
    df : pandas.DataFrame
        Input dataframe with clean_fullname_column present
    clean_fullname_column : str
        Name of column containing fullname as string type
    suffix : str, default = ""
        Optional suffix to append to name component column names

    Returns
    -------
    pandas.DataFrame
        derive_names returns the dataframe with additional columns
        for first name, middle name(s) and last name.

    Example
    -------
    >>> import pandas as pd
    >>> df = pd.DataFrame({'Clean_Name': ['John Paul William Smith']})
    >>> df.head(1)
                    Clean_Name
    0  John Paul William Smith
    >>> df = derive_names(df, clean_fullname_column='Clean_Name', suffix="")
    >>> df.head(n=1)
                    Clean_Name forename   middle_name last_name
    0  John Paul William Smith     John  Paul William     Smith
    """
    df[clean_fullname_column] = df[clean_fullname_column].str.replace("-", " ")
    df["Name_count"] = [len(x.split()) for x in df[clean_fullname_column]]
    df["forename" + suffix] = np.where(
        df["Name_count"] > 0, df[clean_fullname_column].str.split().str.get(0), np.NaN
    )
    df["middle_name" + suffix] = [" ".join(x.split()[1:-1]) for x in df[clean_fullname_column]]
    df["last_name" + suffix] = np.where(
        df["Name_count"] > 1, df[clean_fullname_column].str.split().str.get(-1), np.NaN
    )
    df = replace_vals(df, dic={np.NaN: ''}, subset=["forename" + suffix,
                                                    "middle_name" + suffix,
                                                    "last_name" + suffix])
    return df.drop(["Name_count"], axis=1)


def n_gram(df, input_col, output_col, missing_value, n):
    """
    Generates the upper case n-gram sequence for all strings in a column.

    Parameters
    ----------
    df: pandas.DataFrame
        Input dataframe with input_col present
    input_col: str
        name of column to apply n_gram to
    output_col: str
        name of column to be output
    missing_value:
        value that is used for missingness in input_col
        will also be used for missingness in output_col
    n: int
        Chosen n-gram

    Returns
    -------
    pandas.DataFrame
        n_gram returns the dataframe with additional column output_col

    Example
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame({'Forename': ['Jonathon', np.nan]})
    >>> df.head(n=2)
       Forename
    0  Jonathon
    1       NaN
    >>> df = n_gram(df, input_col='Forename', output_col='First_Two', missing_value=np.nan, n=2)
    >>> df = n_gram(df, input_col='Forename', output_col='Last_Two', missing_value=np.nan, n=-2)
    >>> df.head(n=2)
       Forename First_Two Last_Two
    0  Jonathon        JO       ON
    1       NaN       NaN      NaN
    """
    df[input_col] = df[input_col].replace(missing_value, "")
    if n < 0:
        df[output_col] = [x.upper()[n:] for x in df[input_col]]
    else:
        df[output_col] = [x.upper()[:n] for x in df[input_col]]
    df[input_col] = df[input_col].replace("", missing_value)
    df[output_col] = df[output_col].replace("", missing_value)
    return df


def pad_column(df, input_col, output_col, length):
    """
    Pads a column (int or string type) with leading zeros.
    Values in input_col that are longer than the chosen pad
    length will not be padded and will remain unchanged.

    Parameters
    ----------
    df: pandas.DataFrame
        Input dataframe with input_col present
    input_col: str or int
        name of column to apply pad_column to
    output_col: str
        name of column to be output
    length: int
        Chosen length of strings in column AFTER padding with zeros

    Returns
    -------
    pandas.DataFrame
        pad_column returns the dataframe with additional column output_col

    Example
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame({'Age': [2, 5, 100]})
    >>> df.head(n=3)
       Age
    0    2
    1    5
    2  100
    >>> df = pad_column(df, 'Age', 'Age_Padded', 3)
    >>> df.head(n=3)
       Age Age_Padded
    0    2        002
    1    5        005
    2  100        100
    """
    df[output_col] = [x.zfill(length) for x in df[input_col].astype("str")]
    return df


def replace_vals(df, subset=None, dic=None):
    """
    Uses regular expressions to replace values within dataframe columns.

    Parameters
    ----------
    df : pandas.DataFrame
        The dataframe to which the function is applied.
    dic : dict, default = None
        The values of the dictionary are the substrings
        that are being replaced within the subset columns.
        These must either be regex statements in the form of a
        string, or numpy nan values. The key is the replacement.
        The value is the regex to be replaced.
    subset : str or list of str, default = None
        The subset is the list of columns in the dataframe
        on which replace_vals is performing its actions.
        If no subset is entered the None default makes sure
        that all columns in the dataframe are in the subset.

    Returns
    -------
    pandas.DataFrame
        replace_vals returns the dataframe with the column values
        changed appropriately.

    Example
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame({'Sex': ['M', 'F']})
    >>> df.head(n=2)
      Sex
    0   M
    1   F
    >>> df = replace_vals(df, dic={'MALE':'M', 'FEMALE':'F'}, subset='Sex')

    >>> df.head(n=3)
          Sex
    0    MALE
    1  FEMALE
    """
    if dic is None:
        dic = {}
    if subset is None:
        subset = df.columns
    if not isinstance(subset, list):
        subset = [subset]
    if subset is not None:
        for col in subset:
            for key, val in dic.items():
                df[col] = df[col].replace(val, key)
    return df


def select(df, columns):
    """
    Retains only specified list of columns.

    Parameters
    ----------
    df : pandas.DataFrame
        The dataframe to which the function is applied.
    columns : str or list of str, default = None
        This argument can be entered as a list of column headers
        that are the columns to be selected. If a single string
        that is a name of a column is entered, it will select
        only that column.

    Returns
    -------
    pandas.DataFrame
        Dataframe with only selected columns included

    Example
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame({'Sex': ['M', 'F'],
    ...                    'Age': [10, 29]})
    >>> df.head(n=2)
      Sex  Age
    0   M   10
    1   F   29
    >>> df = select(df, columns = 'Sex')
    >>> df.head(n=2)
      Sex
    0   M
    1   F
    """
    if not isinstance(columns, list):
        columns = [columns]
    df = df[columns]
    return df


def soundex(df, input_col, output_col, missing_value):
    """
    Generates the soundex phonetic encoding for all strings in a column.

    Parameters
    ----------
    df: pandas.DataFrame
        The dataframe to which the function is applied.
    input_col: str
        name of column to apply soundex to
    output_col: str
        name of column to be output
    missing_value:
        value that is used for missing value in input_col
        will also be used for missing value in output_col

    Returns
    -------
    pandas.DataFrame
        soundex returns the dataframe with additional column output_col

    Example
    --------
    >>> import pandas as pd
    >>> import jellyfish
    >>> df = pd.DataFrame({'Forename': ['Charlie', 'Rachel', '-9']})
    >>> df.head(n=3)
      Forename
    0  Charlie
    1   Rachel
    2       -9
    >>> df = soundex(df, input_col='Forename', output_col='sdx_Forename', missing_value='-9')
    >>> df.head(n=3)
      Forename sdx_Forename
    0  Charlie         C640
    1   Rachel         R240
    2       -9           -9
    """
    df[output_col] = [jellyfish.soundex(x) for x in df[input_col].astype("str")]
    df[output_col] = df[output_col].replace(
        jellyfish.soundex(missing_value), missing_value
    )
    return df
