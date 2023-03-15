def age_diff_filter(df, age_1, age_2):
    df['Age_Diff'] = df[[age_1, age_2]].apply(lambda x: age_tolerance((x[0]), (x[1])), axis=1)
    df = df[df.Age_Diff == True].drop(['Age_Diff'], axis=1)
    return df


def age_tolerance(column1, column2):
    import numpy as np

    if (abs(column1 - column2) < 2) & (np.maximum(column1, column2) < 10):
        return True

    if (abs(column1 - column2) < 3) & (11 <= column1 <= 20) & (11 <= column2 <= 20):
        return True

    if (abs(column1 - column2) < 4) & (21 <= column1 <= 40) & (21 <= column2 <= 40):
        return True

    if (abs(column1 - column2) < 5) & (column1 > 40) & (column2 > 40):
        return True

    else:
        return False


# levenshtein edit distance
def edit_distance(string1, string2):
    import jellyfish

    # Score = None if strings are None
    if string1 is None or string2 is None:
        return None

    # Calculate score if strings are not None
    else:
        lev = jellyfish.levenshtein_distance(string1, string2)
    return lev


def get_assoc_candidates(cen, pes, matches, person_id, hh_id):

    # Join on hh_id to matches
    matches = matches.merge(cen[[person_id+'_cen', hh_id+'_cen']], on=person_id+'_cen', how='left')
    matches = matches.merge(pes[[person_id+'_pes', hh_id+'_pes']], on=person_id+'_pes', how='left')

    # Get residuals
    cen = get_residuals(all_records=cen, matched_records=matches, id_=person_id+'_cen').drop_duplicates([person_id+'_cen'])
    pes = get_residuals(all_records=pes, matched_records=matches, id_=person_id+'_pes').drop_duplicates([person_id+'_pes'])

    # Join on household matches to unmatched records
    hh_pairs = matches[[hh_id + '_cen', hh_id + '_pes']].drop_duplicates()
    cen = cen.merge(hh_pairs, on=hh_id+'_cen', how='inner')
    pes = pes.merge(hh_pairs, on=hh_id+'_pes', how='inner')
    return cen, pes


def get_residuals(all_records, matched_records, id_):
    df = all_records.merge(matched_records[[id_]].drop_duplicates(), on=id_, how='left', indicator=True)
    df = df[df['_merge'] == 'left_only'].drop('_merge', axis=1)
    return df


def mult_match(df):
    import pandas as pd
    counts = pd.DataFrame(df[['hid_pes', 'hid_cen']].value_counts()).reset_index()
    counts.columns = ['hid_pes', 'hid_cen', 'count']
    df = df.merge(counts, on=['hid_pes', 'hid_cen'], how='left')
    df = df[df['count'] > 1].drop(['count'], axis=1)
    return df


def run_single_matchkey(cen,
                        pes,
                        level,
                        matchkey,
                        variables,
                        swap_variables=None,
                        lev_variables=None,
                        age_threshold=None):
    import pandas as pd
    from library.parameters import CLERICAL_VARIABLES

    if level != 'associative':
        pes_link_vars = [var + '_pes' for var in variables] + [level + '_pes']
        cen_link_vars = [var + '_cen' for var in variables] + [level + '_cen']
    else:
        pes_link_vars = [var + '_pes' for var in variables] + ['hid_pes', 'hid_cen']
        cen_link_vars = [var + '_cen' for var in variables] + ['hid_pes', 'hid_cen']

    if swap_variables:
        for i in swap_variables:
            for j in i:
                if j[-3:] == 'pes':
                    pes_link_vars.append(j)
                if j[-3:] == 'cen':
                    cen_link_vars.append(j)

    matches = pd.merge(left=cen,
                       right=pes,
                       how="inner",
                       left_on=cen_link_vars,
                       right_on=pes_link_vars)

    if lev_variables:
        for i in lev_variables:
            matches = std_lev_filter(matches, i[0], i[1], i[2])

    if age_threshold:
        matches = age_diff_filter(matches, 'age_cen', 'age_pes')

    matches['MK'] = matchkey

    variables = [x + '_cen' for x in CLERICAL_VARIABLES] + [x + '_pes' for x in CLERICAL_VARIABLES]
    matches = matches[variables + ['MK']]

    return matches


# standardised levenshtein function
def std_lev(string1, string2):
    import jellyfish

    # Score = None if strings are None
    if string1 is None or string2 is None:
        return None

    # Calculate score if strings are not None
    else:
        # String lengths
        length1, length2 = len(string1), len(string2)

        # Max length
        max_length = max(length1, length2)

        # Edit Distance
        lev = jellyfish.levenshtein_distance(string1, string2)

        # Standardsed Edit Distance
        std_lev_score = 1 - (lev / max_length)

        return std_lev_score


def std_lev_filter(df, variable_cen, variable_pes, threshold):
    df['EDIT'] = df[[variable_cen, variable_pes]].apply(lambda x: std_lev(str(x[0]), str(x[1])), axis=1)
    df = df[df.EDIT >= threshold].drop(['EDIT'], axis=1)
    return df
