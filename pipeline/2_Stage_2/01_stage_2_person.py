from library.crow import *
from library.matching import *
from library.parameters import *
from matchkeys.Stage_2.main_matchkeys import run_matchkeys

# Cleaned data
CEN = pd.read_csv(CEN_CLEAN_DATA, dtype=cen_variable_types, index_col=False)
PES = pd.read_csv(PES_CLEAN_DATA, dtype=pes_variable_types, index_col=False)

# Matches from previous stage
prev_matches = pd.read_csv(OUTPUT_PATH + 'Stage_1_All_Matches.csv', index_col=False)

# Get residuals
CEN = get_residuals(all_records=CEN, matched_records=prev_matches, id_column='puid_cen')
PES = get_residuals(all_records=PES, matched_records=prev_matches, id_column='puid_pes')

# Run matchkeys at chosen level
matches = run_matchkeys(CEN, PES, level='Eaid')

# Collect and save unique matches
unique_matches = collect_uniques(matches, id_1='puid_cen', id_2='puid_pes', match_type='Stage_2_Matchkeys')
unique_matches.to_csv(CHECKPOINT_PATH + 'Stage_2_Matchkey_Unique_Matches.csv', header=True, index=False)

# Collect non-unique matches and send to CROW
non_unique_matches = collect_conflicts(matches, id_1='puid_cen', id_2='puid_pes')
save_for_crow(non_unique_matches, id_column='puid', suffix_1='_cen', suffix_2='_pes',
              file_name='Stage_2_Matchkey_CROW_Conflicts', no_of_files=1)
