import jellyfish
import pandas as pd


def age_diff_filter(df, age_1, age_2):
    """
    Filters a set of matched records to keep only records within certain age tolerances.
    Age tolerances increase slightly as age increases.

    Parameters
    ----------
    df: pandas.DataFrame
        The dataframe to which the function is applied.
    age_1: str
        Name of age column (integer type) from first dataset
    age_2: str
        Name of age column (integer type) from second dataset

    Returns
    -------
    pandas.DataFrame
        Filtered pandas dataframe which only includes records that
        meet the age tolerance criteria.

    See Also
    --------
    age_tolerance
        Function that returns True or False depending on whether two
        integer ages are within certain tolerances.

    Example
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame({'age_1': [5, 15, 25, 50, 99],
    ...                    'age_2': [5, 20, 22, 52, 90]})
    >>> df.head(n=6)
       age_1  age_2
    0      5      5
    1     15     20
    2     25     22
    3     50     52
    4     99     90
    >>> df = age_diff_filter(df, 'age_1', 'age_2')
    >>> df.head(n=5)
       age_1  age_2
    0      5      5
    1     25     22
    2     50     52
    """
    df["Age_Diff"] = df[[age_1, age_2]].apply(
        lambda x: age_tolerance((x[0]), (x[1])), axis=1
    )
    df = df[df.Age_Diff].drop(["Age_Diff"], axis=1)
    df.reset_index(drop=True, inplace=True)
    return df


def age_tolerance(val1, val2):
    """
    Function that returns True or False depending on whether two integer
    ages are within certain tolerances. Used in the age_diff_filter
    filtering function.

    Parameters
    ----------
    val1: int
        First age value
    val2: int
        Second age value

    Returns
    -------
    bool
        The return value is True for cases that meet the age tolerance rules,
        False otherwise.

    See Also
    --------
    age_diff_filter
        Filters a set of matched records to keep only records within certain
        age tolerances. Age tolerances increase slightly as age increases.

    Example
    --------
    >>> age_tolerance(5,5)
    True
    >>> age_tolerance(5,8)
    False
    >>> age_tolerance(45,49)
    True
    >>> age_tolerance(45,50)
    False
    """
    if (abs(val1 - val2) < 2) & ((0 <= val1 <= 10) | (0 <= val2 <= 10)):
        return True
    if (abs(val1 - val2) < 3) & ((11 <= val1 <= 20) | (11 <= val2 <= 20)):
        return True
    if (abs(val1 - val2) < 4) & ((21 <= val1 <= 40) | (21 <= val2 <= 40)):
        return True
    if (abs(val1 - val2) < 5) & ((val1 > 40) | (val2 > 40)):
        return True
    return False


def combine(matchkeys, person_id, suffix_1, suffix_2, keep):
    """
    Takes results from a set of matchkeys and combines into a
    single deduplicated dataframe. If duplicate matches are made
    across matchkeys, the version with the lowest matchkey
    number is retained.

    Parameters
    ----------
    matchkeys: list of pandas.DataFrame
        List of dataframes containing matches made from
        each matchkey
    person_id: str
        Name of person id used in both datasets (without suffix)
    suffix_1: str
        Suffix used for columns in the first dataframe
    suffix_2: str
        Suffix used for columns in the second dataframe
    keep: list of str
        List of variables to retain. Suffixes not required.
        New matchkey column "MK" will also be retained

    See Also
    --------
    run_single_matchkey
        Function to collect matches from a chosen matchkey

    Returns
    --------
    df: pandas.DataFrame
        Combined dataset containing all matches made across matchkeys.

    Example
    --------
    >>> import pandas as pd
    >>> mk1 = pd.DataFrame({'puid_1': [1, 2, 3, 4, 5],
    ...                     'puid_2': [21, 22, 23, 24, 25],
    ...                     'name_1': ['CHARLIE', 'JOHN', 'STEVE', 'SAM', 'PAUL'],
    ...                     'name_2': ['CHARLES', 'JON', 'STEPHEN', 'SAMM', 'PAUL']})
    >>> mk1.head(n=5)
       puid_1  puid_2   name_1   name_2
    0       1      21  CHARLIE  CHARLES
    1       2      22     JOHN      JON
    2       3      23    STEVE  STEPHEN
    3       4      24      SAM     SAMM
    4       5      25     PAUL     PAUL
    >>> mk2 = pd.DataFrame({'puid_1': [1, 2, 3, 6, 7],
    ...                     'puid_2': [21, 22, 30, 31, 32],
    ...                     'name_1': ['CHARLIE', 'JOHN', 'STEVE', 'MARK', 'DAVE'],
    ...                     'name_2': ['CHARLES', 'JON', 'STEUE', 'MARL', 'DAVE']})
    >>> mk2.head(n=5)
       puid_1  puid_2   name_1   name_2
    0       1      21  CHARLIE  CHARLES
    1       2      22     JOHN      JON
    2       3      30    STEVE    STEUE
    3       6      31     MARK     MARL
    4       7      32     DAVE     DAVE
    >>> matches = combine(matchkeys=[mk1, mk2], suffix_1="_1", suffix_2="_2",
    ...                   person_id="puid", keep=['puid', 'name'])
    >>> matches.head(n=8)
       puid_1   name_1  puid_2   name_2  MK
    0       1  CHARLIE      21  CHARLES   1
    1       2     JOHN      22      JON   1
    2       3    STEVE      23  STEPHEN   1
    3       4      SAM      24     SAMM   1
    4       5     PAUL      25     PAUL   1
    5       3    STEVE      30    STEUE   2
    6       6     MARK      31     MARL   2
    7       7     DAVE      32     DAVE   2
    """
    df = pd.DataFrame()
    for i, matches in enumerate(matchkeys):
        matches["MK"] = i + 1
        df = pd.concat([df, matches], axis=0)
        df["Min_MK"] = df.groupby([person_id + suffix_1, person_id + suffix_2])[
            "MK"
        ].transform("min")
        df = df[df.Min_MK == df.MK].drop(["Min_MK"], axis=1)
        df = df[[x + suffix_1 for x in keep] + [x + suffix_2 for x in keep] + ["MK"]]
        df = df.reset_index(drop=True)
    return df


def generate_matchkey(
    suffix_1,
    suffix_2,
    hh_id,
    level,
    variables,
    swap_variables=None,
):
    """
    Function to generate a single matchkey for matching
    two dataframes together. 'swap_variables' enables different
    variables to be used across dataframes e.g. require agreement
    between forename (on dataframe 1) and surname (on dataframe 2).

    Parameters
    ----------
    suffix_1: str
        Suffix used for columns in the first dataframe to match
    suffix_2: str
        Suffix used for columns in the second dataframe to match
    hh_id: str
        Name of household ID column in dataframes to match (without suffixes)
        Required when level='associative'.
    level: str
        Level of geography to include in the matchkey
        e.g. household, enumeration area etc.
        If level = 'associative' then an associative matchkey is applied instead.
    variables: list of str
        List of variables to use in matchkey rule (exluding level of geography)
    swap_variables: list of tuple, optional
        Use if you want to match a variable from one dataframe to a
        different variable on the other dataframe.
        For example, to match forename on dataframe 1 to surname on dataframe 2,
        swap_variables = [('forename_1', 'surname_2')]

    Returns
    -------
    df1_link_vars: list
        Variables to match on, suffixed with suffix_1
    df2_link_vars: list
        Variables to match on, suffixed with suffix_2

    See Also
    --------
    run_single_matchkey

    Example
    --------
    >>> mk = generate_matchkey(
    ...     suffix_1="_cen",
    ...     suffix_2="_pes",
    ...     hh_id="hid",
    ...     level="Eaid",
    ...     variables=["forename", "dob", "sex"],
    ...     swap_variables=[("middlename_cen", "surname_pes")])
    >>> mk[0]
    ['forename_cen', 'dob_cen', 'sex_cen', 'Eaid_cen', 'middlename_cen']
    >>> mk[1]
    ['forename_pes', 'dob_pes', 'sex_pes', 'Eaid_pes', 'surname_pes']
    """
    if level != "associative":
        df1_link_vars = [var + suffix_1 for var in variables] + [level + suffix_1]
        df2_link_vars = [var + suffix_2 for var in variables] + [level + suffix_2]
    else:
        df1_link_vars = [var + suffix_1 for var in variables] + [
            hh_id + suffix_1,
            hh_id + suffix_2,
        ]
        df2_link_vars = [var + suffix_2 for var in variables] + [
            hh_id + suffix_1,
            hh_id + suffix_2,
        ]
    if swap_variables:
        for i in swap_variables:
            for j in i:
                if j.endswith(suffix_2):
                    df2_link_vars.append(j)
                if j.endswith(suffix_1):
                    df1_link_vars.append(j)
    return df1_link_vars, df2_link_vars


def get_assoc_candidates(df1, df2, suffix_1, suffix_2, matches, person_id, hh_id):
    """
    Associative Matching Function. Takes all person matches made between two
    datasets and collects their unique household pairs. Unmatched person
    records from these household pairs are then grouped together (associatively).
    This is done by merging on the household ID pair to each unmatched record.

    Parameters
    ----------
    df1: pandas.DataFrame
        The first dataframe being matched - must contain a person_id and hh_id
    df2: pandas.DataFrame
        The second dataframe being matched - must contain a person_id and hh_id
    suffix_1: str
        Suffix used for columns in the first dataframe
    suffix_2: str
        Suffix used for columns in the second dataframe
    matches: pandas.DataFrame
        All unique person matches that will be used to make additional
        associative matches. This DataFrame should contain two person
        ID columns only
    person_id: str
        Name of person ID column (without suffixes)
    hh_id: str
        Name of household ID column (without suffixes)

    Returns
    -------
    df1: pandas.DataFrame
        Unmatched person records from df1 with additional household ID column from df2
    df2: pandas.DataFrame
        Unmatched person records from df2 with additional household ID column from df1

    See Also
    --------
    get_residuals
        Function for collecting person records not yet matched

    Example
    --------
    >>> import pandas as pd
    >>> df1 = pd.DataFrame({'puid_1': [1, 2, 3, 4, 5],
    ...                     'hhid_1': [1, 1, 1, 1, 1],
    ...                     'name_1': ['CHARLIE', 'JOHN', 'STEVE',
    ...                                'SAM', 'PAUL']})
    >>> df2 = pd.DataFrame({'puid_2': [21, 22, 23, 24, 25],
    ...                     'hhid_2': [2, 2, 2, 2, 2],
    ...                     'name_2': ['CHARLES', 'JON',
    ...                                'STEPHEN', 'SAMANTHA', 'PAUL']})
    >>> matches = pd.DataFrame({'puid_1': [1, 5],
    ...                         'puid_2': [21, 25]})
    >>> df1, df2 = get_assoc_candidates(df1, df2, suffix_1='_1', suffix_2='_2',
    ...                                 matches=matches,person_id='puid',
    ...                                 hh_id='hhid')
    >>> df1.head(n=5)
       puid_1  hhid_1 name_1  hhid_2
    0       2       1   JOHN       2
    1       3       1  STEVE       2
    2       4       1    SAM       2
    >>> df2.head(n=5)
       puid_2  hhid_2    name_2  hhid_1
    0      22       2       JON       1
    1      23       2   STEPHEN       1
    2      24       2  SAMANTHA       1

    Additional column added to each DataFrame of residuals, which has associated
    households 1 and 2 together, using the existing matches between
    persons 1 and 21 and persons 5 and 25.
    """
    matches = matches.merge(
        df1[[person_id + suffix_1, hh_id + suffix_1]],
        on=person_id + suffix_1,
        how="left",
    )
    matches = matches.merge(
        df2[[person_id + suffix_2, hh_id + suffix_2]],
        on=person_id + suffix_2,
        how="left",
    )
    df1 = get_residuals(
        all_records=df1, matched_records=matches, id_column=person_id + suffix_1
    ).drop_duplicates([person_id + suffix_1])
    df2 = get_residuals(
        all_records=df2, matched_records=matches, id_column=person_id + suffix_2
    ).drop_duplicates([person_id + suffix_2])
    hh_pairs = matches[[hh_id + suffix_1, hh_id + suffix_2]].drop_duplicates()
    df1 = df1.merge(hh_pairs, on=hh_id + suffix_1, how="inner")
    df2 = df2.merge(hh_pairs, on=hh_id + suffix_2, how="inner")
    return df1, df2


def get_residuals(all_records, matched_records, id_column):
    """
    Filters a set of matched records to keep only records within
    certain age tolerances. Age tolerances increase slightly as age increases.

    Parameters
    ----------
    all_records: pandas.DataFrame
        The dataframe containing all person records.
    matched_records: pandas.DataFrame
        The dataframe containing all matched person records
    id_column: str
        Name of person ID column (including suffixes)

    Returns
    -------
    pandas.DataFrame
        Matched records removed, leaving only the residuals.

    Example
    --------
    >>> import pandas as pd
    >>> all_records = pd.DataFrame({'puid_1': [1, 2, 3, 4, 5]})
    >>> all_records.head(n=5)
       puid_1
    0       1
    1       2
    2       3
    3       4
    4       5
    >>> matched_records = pd.DataFrame({'puid_1': [1, 2, 3],
    ...                                 'puid_2': [21, 22, 23]})
    >>> matched_records.head(n=5)
       puid_1  puid_2
    0       1      21
    1       2      22
    2       3      23
    >>> residuals = get_residuals(all_records=all_records,
    ...                           matched_records=matched_records,
    ...                           id_column='puid_1')
    >>> residuals.head(n=5)
       puid_1
    0       4
    1       5
    """

    assert (
        matched_records[id_column].dtype == all_records[id_column].dtype
    ), "id_column types do not match between matched_records and all_records"

    df = all_records.merge(
        matched_records[[id_column]].drop_duplicates(),
        on=id_column,
        how="left",
        indicator=True,
    )
    df = df[df["_merge"] == "left_only"].drop("_merge", axis=1)
    df.reset_index(drop=True, inplace=True)
    return df


def mult_match(df, hh_id_1, hh_id_2):
    """
    Filters a set of matched records by retaining only those where 2 or
    more matches have been made across a pair of households.

    Parameters
    ----------
    df: pandas.DataFrame
        dataframe to filter containing all person matches / candidates.
    hh_id_1: str
        Name of household ID column in first dataset (including suffix)
    hh_id_2: str
        Name of household ID column in second dataset (including suffix)

    Returns
    -------
    pandas.DataFrame
        Retains cases where mutliple matches have been made between two households.
        Other cases are discarded.
    """
    counts = pd.DataFrame(df[[hh_id_1, hh_id_2]].value_counts()).reset_index()
    counts.columns = [hh_id_1, hh_id_2, "count"]
    df = df.merge(counts, on=[hh_id_1, hh_id_2], how="left")
    df = df[df["count"] > 1].drop(["count"], axis=1)
    df.reset_index(drop=True, inplace=True)
    return df


def run_single_matchkey(
    df1,
    df2,
    suffix_1,
    suffix_2,
    hh_id,
    level,
    variables,
    swap_variables=None,
    lev_variables=None,
    age_threshold=None,
):
    """
    Function to collect matches from a chosen matchkey.
    Partial agreement can be included using std_lev_filter,
    and age filters can be applied using age_threshold.
    Use swap_variables to match across different variables e.g.
    forename = surname.

    Parameters
    ----------
    df1: pandas.DataFrame
        The first dataframe being matched
    df2: pandas.DataFrame
        The second dataframe being matched
    suffix_1: str
        Suffix used for columns in the first dataframe
    suffix_2: str
        Suffix used for columns in the second dataframe
    hh_id: str
        Name of household ID column in df1 and df2 (without suffixes)
        Required when level='associative'.
    level: str
        Level of geography to include in the matchkey e.g. household, EA etc.
        If level = 'associative' then an associative matchkey is applied instead.
    variables: list of str
        List of variables to use in matchkey rule (exluding level of geography)
    swap_variables: list of tuple, optional
        Use if you want to match a variable from one dataset to a
        different variable on the other dataset.
        For example, to match forename on df1 to surname on df2,
        swap_variables = [('forename_1', 'surname_2')]
    lev_variables: list of tuple, optional
        Use if you want to apply the std_lev_filter function within the matchkey.
        For example, to apply to forenames (threshold = 0.80):
        lev_variables = [('forename_1', 'forename_2', 0.80)]
    age_threshold: bool, optional
        Use if you want to apply the age_diff_filter function within the matchkey.
        To apply, simply set age_threshold = True

    Returns
    -------
    matches: pandas.DataFrame
        All matches made from chosen matchkey (non-unique matches included)

    See Also
    --------
    generate_matchkey
    std_lev_filter
    age_diff_filter
    """
    link_vars = generate_matchkey(
        suffix_1=suffix_1,
        suffix_2=suffix_2,
        hh_id=hh_id,
        level=level,
        variables=variables,
        swap_variables=swap_variables,
    )
    df1_link_vars = link_vars[0]
    df2_link_vars = link_vars[1]
    matches = pd.merge(
        left=df1, right=df2, how="inner", left_on=df1_link_vars, right_on=df2_link_vars
    )
    if lev_variables:
        for i in lev_variables:
            matches = std_lev_filter(matches, i[0], i[1], i[2])
    if age_threshold:
        matches = age_diff_filter(matches, "age" + suffix_1, "age" + suffix_2)
    return matches


def std_lev(string1, string2):
    """
    Function that compares two strings (usually names) and returns
    the standardised levenstein edit distance score, between 0 and 1.
    Used in the std_lev_filter filtering function.

    Parameters
    ----------
    string1: str or None
        First string for comparison
    string2: str or None
        Second string for comparison

    Returns
    -------
    float
        Score between 0 and 1.
        The closer to 1, the stronger the similarity between the two strings
        (1 = full agreeement / exact matches).

    See Also
    --------
    std_lev_filter
        Filters a set of matched records to keep only records where names
        have a similarity greater than a chosen threshold.

    Example
    --------
    >>> std_lev('CHARLIE','CHARLIE')
    1.0
    >>> std_lev('CHARLIE','CHARLES')
    0.7142857142857143
    >>> std_lev('CHARLIE',None)

    """
    if string1 is None or string2 is None:
        return None

    length1, length2 = len(string1), len(string2)
    max_length = max(length1, length2)
    lev = jellyfish.levenshtein_distance(string1, string2)
    return 1 - (lev / max_length)


def std_lev_filter(df, column1, column2, threshold):
    """
    Filters a set of matched records to keep only records where names
    have a similarity greater than a chosen threshold.

    Parameters
    ----------
    df: pandas.DataFrame
        The dataframe to which the function is applied.
    column1: str
        Name column (string type) from first dataset
    column2: str
        Name column (string type) from second dataset
    threshold: float
        Record pairs with a std levenstein edit distance
        Below this threshold will be discarded

    Returns
    -------
    pandas.DataFrame
        Filtered pandas dataframe which only includes records that
        meet the edit distance filter criteria.

    See Also
    --------
    std_lev
        Function that compares two strings (usually names) and returns
        the standardised levenstein edit distance score, between 0 and 1.

    Example
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame({'name_1': ['CHARLES', None, 'C', 'CHRLEI', 'CH4RL1E'],
    ...                    'name_2': ['CHARLIE', 'CHARLIE', 'CHARLIE', 'CHARLIE',
    ...                               'CHARLIE']})
    >>> df.head(n=5)
        name_1   name_2
    0  CHARLES  CHARLIE
    1     None  CHARLIE
    2        C  CHARLIE
    3   CHRLEI  CHARLIE
    4  CH4RL1E  CHARLIE
    >>> df = std_lev_filter(df, column1='name_1', column2='name_2', threshold=0.60)
    >>> df.head(n=5)
        name_1   name_2
    0  CHARLES  CHARLIE
    1  CH4RL1E  CHARLIE
    """
    df["EDIT"] = df[[column1, column2]].apply(
        lambda x: std_lev(str(x[0]), str(x[1])), axis=1
    )
    df = df[df.EDIT >= threshold].drop(["EDIT"], axis=1)
    df.reset_index(drop=True, inplace=True)
    return df
