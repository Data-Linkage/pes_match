import pandas as pd
from library.crow import collect_uniques, collect_conflicts, save_for_crow
from library.matching import get_residuals, run_single_matchkey, combine
from library.parameters import (CEN_CLEAN_DATA, PES_CLEAN_DATA,
                                cen_variable_types, pes_variable_types,
                                CHECKPOINT_PATH, OUTPUT_PATH,
                                CLERICAL_VARIABLES)

# Cleaned data
CEN = pd.read_csv(
    CEN_CLEAN_DATA, dtype=cen_variable_types, iterator=False, index_col=False
)
PES = pd.read_csv(
    PES_CLEAN_DATA, dtype=pes_variable_types, iterator=False, index_col=False
)

# Matches from previous stage
prev_matches = pd.read_csv(OUTPUT_PATH + "Stage_1_All_Matches.csv", iterator=False, index_col=False)

# Get residuals
CEN = get_residuals(all_records=CEN, matched_records=prev_matches, id_column="puid_cen")
PES = get_residuals(all_records=PES, matched_records=prev_matches, id_column="puid_pes")

# MATCHKEY PARAMS
mk_params = {'df1': CEN, 'df2': PES, 'suffix_1': "_cen", 'suffix_2': "_pes", 'hh_id': "hid", 'level': "Eaid"}

# ---------- RUN MATCHKEYS ---------- #
mk1 = run_single_matchkey(**mk_params, variables=["forename_clean", "middlenm_clean", "full_dob"])

# Combine
matches = combine(matchkeys=[mk1], suffix_1="_cen", suffix_2="_pes",
                  person_id="puid", keep=CLERICAL_VARIABLES)

# Collect and save unique matches
unique_matches = collect_uniques(
    matches, id_1="puid_cen", id_2="puid_pes", match_type="Stage_2_Matchkeys"
)
unique_matches.to_csv(
    CHECKPOINT_PATH + "Stage_2_Matchkey_Unique_Matches.csv", header=True, index=False
)

# Collect non-unique matches and send to CROW
non_unique_matches = collect_conflicts(matches, id_1="puid_cen", id_2="puid_pes")
save_for_crow(
    non_unique_matches,
    id_column="puid",
    suffix_1="_cen",
    suffix_2="_pes",
    file_name="Stage_2_Matchkey_CROW_Conflicts",
    no_of_files=1,
)
