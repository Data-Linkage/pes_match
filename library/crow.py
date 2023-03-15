from library.parameters import *


def collect_uniques(df, file_name, match_type):
    import numpy as np
    import pandas as pd
    pd.options.mode.chained_assignment = None
    df['ID_count_1'] = df.groupby(['puid_cen'])['puid_pes'].transform('count')
    df['ID_count_2'] = df.groupby(['puid_pes'])['puid_cen'].transform('count')
    df['CLERICAL'] = np.where(((df['ID_count_1'] > 1) | (df['ID_count_2'] > 1)), 1, 0)
    df = df[df['CLERICAL'] == 0]
    df['Match_Type'] = match_type
    df.to_csv(CHECKPOINT_PATH + file_name + '.csv', header=True, index=False)


def crow_output_updater(output_df, id_column, source_column, df1_name, df2_name, match_type):
    """
    Returns the outputs of CROW in a pairwise linked format

    Parameters
    ----------
    output_df: dataframe
        pandas dataframe containing CROW matched output
    id_column: string
        name of record_id column in CROW matched output
    source_column: string
        name of column in CROW matched output identifying which
        data source the record is from
    df1_name: string
        name of the first data source
    df2_name: string
        name of the second data source
    match_type: string
        indicator to say which stage matches were made at

    Return
    -------
    df: dataframe
    
    Example
    -------
    
    > CROW_output_updater(output_df = matches, id_column = 'puid', source_column = 'Source_Dataset',
    df1_name = 'CEN', df2_name = 'PES', match_type = 'Stage_1')
    
    >   puid_CEN	puid_PES    Match_Type  CLERICAL    MK
    0	A2	        ABC1        Stage_1     1           0
    1	A3	        ABC1        Stage_1     1           0
    2	ABC1	    A2          Stage_1     1           0
    3	A3	        A2          Stage_1     1           0
    4	ABC1	    A3          Stage_1     1           0
    5	A2	        A3          Stage_1     1           0
    6	AC12	    A9          Stage_1     1           0
    7	C11	        ABC10       Stage_1     1           0
    8	ABC10	    C11         Stage_1     1           0
    9	A9	        AC12        Stage_1     1           0
    """
    import pandas as pd
    import numpy as np

    # CROW Output
    df = output_df

    # Select required columns and only keep clusters containing matches
    df = df[df['Match'] != 'No match in cluster'][[id_column, source_column, 'Match']]
    df = df.rename(columns={id_column: 'Record_1', source_column: 'Source_Dataset_1'})

    # Create lookup of ID to Source Dataset to use later
    lookup = df[['Record_1', 'Source_Dataset_1']]
    lookup = lookup.rename(columns={'Record_1': 'Record_2', 'Source_Dataset_1': 'Source_Dataset_2'})

    # Remove trailing commas and convert to lists
    df['Match'] = df['Match'].str.rstrip(',')
    df['Record_2'] = df['Match'].str.split(',')
    df.drop(['Match'], axis=1, inplace=True)

    # Explode to get all combinations of matched pairs
    df = df.explode('Record_2')

    # Types
    df['Record_1'] = df['Record_1'].astype('str')
    df['Record_2'] = df['Record_2'].astype('str')
    lookup['Record_2'] = lookup['Record_2'].astype('str')

    # Join on Source Dataset for Record_2
    df = pd.merge(df, lookup, on='Record_2', how='left')

    # Reorder ID columns to identify all duplicates (including cross duplicates)
    df['Record_1_FINAL'] = np.where(df['Source_Dataset_1'] == df1_name, df['Record_1'], df['Record_2'])
    df['Record_2_FINAL'] = np.where(df['Source_Dataset_2'] == df2_name, df['Record_2'], df['Record_1'])

    # Remove duplicate (df1 to df1 and/or df2 to df2) matches
    df = df[~(df.Source_Dataset_1 == df.Source_Dataset_2)]
    df.drop(['Source_Dataset_1', 'Source_Dataset_2', 'Record_1', 'Record_2'], axis=1, inplace=True)

    # Remove all duplicates
    df = df.drop_duplicates(['Record_1_FINAL', 'Record_2_FINAL'])

    # Rename columns and save
    df = df[['Record_1_FINAL', 'Record_2_FINAL']]
    df = df.rename(columns={'Record_1_FINAL': f'puid_{df1_name}', 'Record_2_FINAL': f'puid_{df2_name}'})
    df.reset_index(drop=True, inplace=True)

    # Extra Flags
    df['Match_Type'] = match_type
    df['CLERICAL'] = 1
    df['MK'] = 0

    return df


def combine_crow_results(stage):
    import pandas as pd
    import glob
    import os

    all_files = glob.glob(os.path.join(CLERICAL_PATH, "*.csv"))
    li = []

    for filename in all_files:
        if stage in filename:
            df = pd.read_csv(filename, index_col=None, header=0)
            li.append(df)

    df = pd.concat(li, axis=0, ignore_index=True)
    return df


def resolve_clusters(df, crow, file_name, no_of_files=1):
    import pandas as pd
    import numpy as np
    from library.cluster import cluster_number
    from library.parameters import CLERICAL_VARIABLES

    df['ID_count_1'] = df.groupby(['puid_cen'])['puid_pes'].transform('count')
    df['ID_count_2'] = df.groupby(['puid_pes'])['puid_cen'].transform('count')
    df['CLERICAL'] = np.where(((df['ID_count_1'] > 1) | (df['ID_count_2'] > 1)), 1, 0)

    if crow:

        df = df[df['CLERICAL'] == 1]

        # Add cluster number to records
        df = cluster_number(df, id_column='puid', suffix_1="_cen", suffix_2="_pes")

        # Filter out large clusters as they will not fit on CROW screen
        df['Size'] = df.groupby(['Cluster_Number'])['Cluster_Number'].transform('count')
        df = df[df.Size <= 12].drop(['Size'], axis=1)

        # Save records for clerical in the correct format for CROW
        crow_variables = CLERICAL_VARIABLES
        crow_records_1 = df[[var + "_cen" for var in crow_variables] + ['Cluster_Number']].drop_duplicates()
        crow_records_2 = df[[var + "_pes" for var in crow_variables] + ['Cluster_Number']].drop_duplicates()
        crow_records_1.columns = crow_records_1.columns.str.replace(r'_cen$', '', regex=True)
        crow_records_2.columns = crow_records_2.columns.str.replace(r'_pes$', '', regex=True)
        crow_records_1['Source_Dataset'] = 'cen'
        crow_records_2['Source_Dataset'] = 'pes'
        crow_input = pd.concat([crow_records_1, crow_records_2], axis=0).sort_values(
            ['Cluster_Number', 'Source_Dataset'])

        # Split clusters into groups
        clusters_split = np.array_split(crow_input['Cluster_Number'].unique(), no_of_files)
        for i, group in enumerate(clusters_split):
            crow_input_split = crow_input[crow_input['Cluster_Number'].isin(list(clusters_split[i]))]
            crow_input_split.to_csv(CLERICAL_PATH + file_name + '_' + str(i + 1) + '.csv', header=True, index=False)
    if not crow:
        pass
