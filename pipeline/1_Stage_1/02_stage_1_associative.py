import pandas as pd
from library.crow import combine_crow_results, crow_output_updater, collect_uniques
from library.matching import get_assoc_candidates
from matchkeys.Stage_1.associative_matchkeys import run_matchkeys
from library.parameters import (CEN_CLEAN_DATA, PES_CLEAN_DATA,
                                cen_variable_types, pes_variable_types,
                                CHECKPOINT_PATH, OUTPUT_VARIABLES,
                                CLERICAL_VARIABLES)

# Cleaned data
CEN = pd.read_csv(
    CEN_CLEAN_DATA, dtype=cen_variable_types, iterator=False, index_col=False
)
PES = pd.read_csv(
    PES_CLEAN_DATA, dtype=pes_variable_types, iterator=False, index_col=False
)

# Read in unique matches
unique_matches = pd.read_csv(
    CHECKPOINT_PATH + "Stage_1_Matchkey_Unique_Matches.csv", index_col=False
)

# Combine matches made in CROW into single dataset
crow_matches = combine_crow_results(stage="Stage_1")

# Update format of matches and add flags
crow_matches = crow_output_updater(
    output_df=crow_matches,
    id_column="puid",
    source_column="Source_Dataset",
    df1_name="_cen",
    df2_name="_pes",
    match_type="Stage_1_Conflicts",
)

# Save clerical matches
crow_matches.to_csv(
    CHECKPOINT_PATH + "Stage_1_Matchkey_Conflict_Matches.csv", header=True, index=False
)

# Combine auto matches with clerical matches
all_matches = pd.concat(
    [unique_matches[OUTPUT_VARIABLES], crow_matches[OUTPUT_VARIABLES]]
)

# Get associative candidates
CEN, PES = get_assoc_candidates(
    CEN,
    PES,
    suffix_1="_cen",
    suffix_2="_pes",
    matches=all_matches,
    person_id="puid",
    hh_id="hid",
)

# Run associative matchkeys
assoc_matches = run_matchkeys(CEN, PES, level="associative")
assoc_matches = assoc_matches[[x + "_cen" for x in CLERICAL_VARIABLES] +
                              [x + "_pes" for x in CLERICAL_VARIABLES] +
                              ["MK"]]

# Collect and save unique matches
assoc_uniques = collect_uniques(
    assoc_matches, id_1="puid_cen", id_2="puid_pes", match_type="Stage_1_Associative"
)
assoc_uniques.to_csv(
    CHECKPOINT_PATH + "Stage_1_Associative_Unique_Matches.csv", header=True, index=False
)
