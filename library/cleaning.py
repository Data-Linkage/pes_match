import numpy as np
import jellyfish
import re


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
    df[input_col + '_cleaned'] = [re.sub(r'[^A-Za-z]+', '', s) for s in df[input_col]]
    df[output_col] = [''.join(sorted(x.upper())) for x in df[input_col + '_cleaned']]
    df = df.drop([input_col + '_cleaned'], axis=1)
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
    types: str
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
    if type(input_cols) != list:
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
    andas.DataFramep
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
    df[name_column] = df[name_column].replace(np.nan, '')
    df[name_column + '_clean' + suffix] = [' '.join(x.upper().split()) for x in df[name_column]]
    df[name_column + '_clean' + suffix] = [re.sub(r'[^A-Za-z ]+', '', s) for s in df[name_column + '_clean' + suffix]]
    df[name_column + '_clean' + suffix] = df[name_column + '_clean' + suffix].replace('', np.nan)
    df[name_column] = df[name_column].replace('', np.nan)
    return df


def concat(df, columns, output_col, sep=' '):
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
    df = replace_vals(df, dic={'': np.NaN}, subset=columns)
    df[output_col] = df[columns].agg(sep.join, axis=1)
    df[output_col] = [' '.join(x.split()) for x in df[output_col]]
    df = replace_vals(df, dic={np.NaN: ''}, subset=columns)
    return df


def derive_list(df, partition_var, list_var, output_col):
    """
    Collects values from chosen column into a list after partitioning by
    another column. Lists are then stored in a new column
    
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
    >>> df = derive_list(df, partition_var='Household', list_var='Forename', output_col='Forename_List')
    >>> df.head(n=4)
      Forename  Household     Forename_List
    0     John          1     [John, Steve]
    1    Steve          1     [John, Steve]
    2  Charlie          2  [Charlie, James]
    3    James          2  [Charlie, James]
    """
    values_in_partition = df.groupby(partition_var)[list_var].agg(list).reset_index()
    values_in_partition.columns = [partition_var, output_col]
    df = df.merge(values_in_partition, on=partition_var, how='left')
    return df


def derive_names(df, clean_fullname_column, suffix=""):
    """
    Derives first, middle and last names from
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
        for first, middle (second) and last names.

    Example
    -------
    >>> import pandas as pd
    >>> df = pd.DataFrame({'Clean_Name': ['John William Smith']})
    >>> df.head(n=1)
               Clean_Name
    0  John William Smith
    >>> df = derive_names(df, clean_fullname_column='Clean_Name', suffix="")
    >>> df.head(n=1)
               Clean_Name forename middle_name last_name
    0  John William Smith     John     William     Smith
    """
    df['forename' + suffix] = df[clean_fullname_column].str.split().str.get(0)
    df['middle_name' + suffix] = df[clean_fullname_column].str.split().str.get(1)
    df['last_name' + suffix] = df[clean_fullname_column].str.split().str.get(-1)
    return df


def n_gram(df, input_col, output_col, missing_value, n):
    """
    Generates the upper case n-gram sequence for all strings in a column.

    Parameters
    ----------
    df: pandas dataframe
    input_col: string
      name of column to apply n_gram to
    output_col: string
      name of column to be output
    missing_value: 
      value that is used for missingness in input_col
      will also be used for missingness in output_col
    n: Chosen n-gram
      
    Returns
    -------
    a pandas dataframe with output_col appended
    
    Example
    --------
    
    > df['forename'].head(1)
    'Charlie'
    > df = n_gram(df, 'forename', 'forename_2_gram', '-9', 2)
    > df = n_gram(df, 'forename', 'forename_-2_gram', '-9', -2)
    > df['forename_2_gram'].head(1)
    'CH'
    > df['forename_-2_gram'].head(1)
    'IE'    
    """
    df[input_col] = df[input_col].replace(missing_value, '')
    if n < 0:
        df[output_col] = [x.upper()[n:] for x in df[input_col]]
    else:
        df[output_col] = [x.upper()[:n] for x in df[input_col]]
    df[input_col] = df[input_col].replace('', missing_value)
    df[output_col] = df[output_col].replace('', missing_value)
    return df


def pad_column(df, input_col, output_col, length):
    """
    Pads a column (int or string type) with leading zeros.

    Parameters
    ----------
    df: pandas dataframe
    input_col: string
      name of column to apply pad_column to
    output_col: string
      name of column to be output
    length: Chosen length of strings in column AFTER padding with zeros
      
    Returns
    -------
    a pandas dataframe with output_col appended
    
    Example
    --------
    
    > df['HH_ID'].head(1)
    123
    > df = pad_column(df, 'HH_ID', 'HH_ID', 5).head(1)
    > df['HH_ID'].head(1)
    00123
    """
    df[output_col] = [x.zfill(length) for x in df[input_col].astype('str')]
    return df


def replace_vals(df, subset=None, dic=None):
    """
    Uses regular expressions to replace values within dataframe columns.
    
    Parameters
    ----------
    df : pandas dataframe
      The dataframe to which the function is applied.
    dic : dictionary
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
    pandas dataframe
      replace_vals returns the dataframe with the column values
      changed appropriately.
      
    Example
    --------
    
    > df['sex'].head(1)
    'M'
    > df = replace_vals(df, dic={'MALE':'M'}, subset='sex')
    > df['sex'].head(1)
    'MALE'
      
    Raises
    -------
    None at present.
    """
    if dic is None:
        dic = {}
    if subset is None:
        subset = df.columns

    if type(subset) != list:
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
    df : pandas dataframe
      The dataframe to which the function is applied.
    columns : string or list of strings, default = None
      This argument can be entered as a list of column headers
      that are the columns to be selected. If a single string
      that is a name of a column is entered, it will select
      only that column.
 
      
    Returns
    -------
    pandas dataframe
      Dataframe with only selected columns included

    Example
    --------
      
    Raises
    -------
    None at present.
    """
    if type(columns) != list:
        columns = [columns]
    df = df[columns]
    return df


def soundex(df, input_col, output_col, missing_value):
    """
    Generates the soundex phonetic encoding for all strings in a column.

    Parameters
    ----------
    df: pandas dataframe
    input_col: string
      name of column to apply soundex to
    output_col: string
      name of column to be output
    missing_value: 
      value that is used for missing value in input_col
      will also be used for missing value in output_col
      
    Returns
    -------
    a pandas dataframe with output_col appended
    
    Example
    --------
    
    > df['forename'].head(1)
    'Charlie'
    > df = soundex(df, 'forename', 'sdx_forename')
    > df['sdx_forename'].head(1)
    'C640'
    """
    df[output_col] = [jellyfish.soundex(x) for x in df[input_col].astype('str')]
    df[output_col] = df[output_col].replace(jellyfish.soundex(missing_value), missing_value)
    return df
