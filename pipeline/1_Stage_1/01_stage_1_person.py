import pandas as pd
from library.crow import collect_uniques, collect_conflicts, save_for_crow
from matchkeys.Stage_1.main_matchkeys import run_matchkeys
from library.parameters import (CEN_CLEAN_DATA, PES_CLEAN_DATA,
                                cen_variable_types, pes_variable_types,
                                CHECKPOINT_PATH)

# Cleaned data
CEN = pd.read_csv(
    CEN_CLEAN_DATA, dtype=cen_variable_types, iterator=False, index_col=False
)
PES = pd.read_csv(
    PES_CLEAN_DATA, dtype=pes_variable_types, iterator=False, index_col=False
)

# Run matchkeys at chosen level
matches = run_matchkeys(CEN, PES, level="hid")

# Collect and save unique matches
unique_matches = collect_uniques(
    matches, id_1="puid_cen", id_2="puid_pes", match_type="Stage_1_Matchkeys"
)
unique_matches.to_csv(
    CHECKPOINT_PATH + "Stage_1_Matchkey_Unique_Matches.csv", header=True, index=False
)

# Collect non-unique matches and send to CROW
non_unique_matches = collect_conflicts(matches, id_1="puid_cen", id_2="puid_pes")
save_for_crow(
    non_unique_matches,
    id_column="puid",
    suffix_1="_cen",
    suffix_2="_pes",
    file_name="Stage_1_Matchkey_CROW_Conflicts",
    no_of_files=1,
)
