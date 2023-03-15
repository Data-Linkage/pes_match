import pandas as pd
from library.parameters import *
from library.cleaning import *

# Raw data
df = pd.read_csv(DATA_PATH + 'Mock_Data_Census.csv', index_col=False)

# Derive clean names
for var in ['forename', 'middlenm', 'last_name']:
    df = clean_name(df, var)

# Derive full name
df = concat(df, 'fullname', sep=' ', columns=['forename_clean', 'middlenm_clean', 'last_name_clean'])

# Derive Alphaname
df = alpha_name(df, 'fullname', 'alpha_name')

# Replace nulls
df = replace_vals(df, dic={'-9': np.NaN},
                  subset=['forename_clean', 'middlenm_clean', 'last_name_clean', 'fullname', 'alpha_name'])

# Collect list of clean forenames in each household
df = derive_list(df, 'hid', 'forename_clean', 'forename_list')

# Forename Trigrams
df = n_gram(df, 'forename_clean', 'forename_tri', '-9', 3)

# Soundex of forename
df = soundex(df, 'forename_clean', 'forename_sdx', '-9')

# Clean Day, Month, Age & Derive full_dob
df = replace_vals(df, dic={99: np.NaN}, subset=['month', 'age'])
df = replace_vals(df, dic={9999: np.NaN}, subset=['year'])
df = change_types(change_types(df, ['year', 'month', 'age'], 'int'), ['year', 'month', 'age'], 'str')
df = pad_column(df, 'month', 'month', 2)
df = concat(df, 'full_dob', sep='/', columns=['month', 'year'])

# Selected columns
df = select(df, columns=['hid', 'puid', 'month', 'year', 'age',
                         'HoH', 'marstat', 'relationship', 'sex',
                         'telephone', 'Eaid', 'forename_clean',
                         'middlenm_clean', 'last_name_clean',
                         'fullname', 'alpha_name',
                         'forename_list', 'forename_tri',
                         'forename_sdx', 'full_dob'])

# Suffixes
df = df.add_suffix('_cen')

# Save
df.to_csv(DATA_PATH + 'cen_cleaned_CT.csv', header=True, index=0)
