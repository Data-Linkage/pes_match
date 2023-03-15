import pandas as pd
from library.crow import *
from matchkeys.stage_1_matchkeys import *

# Cleaned data, dtypes read in from config
CEN = pd.read_csv(DATA_PATH + 'cen_cleaned_CT.csv', index_col=False)
PES = pd.read_csv(DATA_PATH + 'pes_cleaned_CT.csv', index_col=False)

# Run matchkeys at chosen level
matches = run_matchkeys(CEN, PES, level='Eaid')

# Save unique matches
collect_uniques(matches, file_name='Stage_1_Unique_Matches', match_type='Stage_1_Matchkeys')

# If CROW = True then save the non-unique matches, otherwise discard them
resolve_clusters(matches, crow=True, file_name='Stage_1_CROW_Conflicts', no_of_files=4)
