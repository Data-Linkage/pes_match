import pandas as pd
from library.crow import *
from matchkeys.stage_1_matchkeys import *

# Cleaned data, dtypes read in from config
CEN = pd.read_csv(DATA_PATH + 'cen_cleaned_CT.csv', index_col=False)
PES = pd.read_csv(DATA_PATH + 'pes_cleaned_CT.csv', index_col=False)

# Run matchkeys at chosen level
matches = run_matchkeys(CEN, PES, level='Eaid')

# Collect and save unique matches
unique_matches = collect_uniques(matches, id_1='puid_cen', id_2='puid_pes', match_type='Stage_1_Matchkeys')
unique_matches.to_csv(CHECKPOINT_PATH + 'Stage_1_Matchkey_Unique_Matches.csv', header=True, index=False)

# Collect non-unique matches and send to CROW
non_unique_matches = collect_conflicts(matches, id_1='puid_cen', id_2='puid_pes')
save_for_crow(non_unique_matches, id_column='puid', suffix_1='_cen', suffix_2='_pes',
              file_name='Stage_1_Matchkey_CROW_Conflicts', no_of_files=1)
