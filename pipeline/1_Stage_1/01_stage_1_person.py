import os

import pandas as pd

from pes_match.crow import collect_conflicts, collect_uniques, save_for_crow
from pes_match.matching import combine, run_single_matchkey
from pes_match.parameters import (
    CEN_CLEAN_DATA,
    CHECKPOINT_PATH,
    CLERICAL_PATH,
    CLERICAL_VARIABLES,
    PES_CLEAN_DATA,
    cen_variable_types,
    pes_variable_types,
)

if not os.path.exists(CHECKPOINT_PATH):
    os.makedirs(CHECKPOINT_PATH)
if not os.path.exists(CLERICAL_PATH):
    os.makedirs(CLERICAL_PATH)

# Cleaned data
CEN = pd.read_csv(
    CEN_CLEAN_DATA, dtype=cen_variable_types, iterator=False, index_col=False
)
PES = pd.read_csv(
    PES_CLEAN_DATA, dtype=pes_variable_types, iterator=False, index_col=False
)

# MATCHKEY PARAMS
mk_params = {
    "df1": CEN,
    "df2": PES,
    "suffix_1": "_cen",
    "suffix_2": "_pes",
    "hh_id": "hid",
    "level": "hid",
}

# ---------- RUN MATCHKEYS ---------- #
mk1 = run_single_matchkey(
    **mk_params, variables=["forename_clean", "last_name_clean", "full_dob"]
)
mk2 = run_single_matchkey(**mk_params, variables=["telephone", "full_dob"])

# Combine
matches = combine(
    matchkeys=[mk1, mk2],
    suffix_1="_cen",
    suffix_2="_pes",
    person_id="puid",
    keep=CLERICAL_VARIABLES,
)

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
    output_folder=CLERICAL_PATH + "Stage_1_CROW_Files",
    file_name="Stage_1_Matchkey_CROW_Conflicts",
    no_of_files=1,
)
