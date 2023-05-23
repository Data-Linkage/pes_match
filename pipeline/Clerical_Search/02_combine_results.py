import os
import warnings

import pandas as pd

from pes_match.parameters import (
    CEN_CLEAN_DATA,
    CLERICAL_PATH,
    OUTPUT_PATH,
    OUTPUT_VARIABLES,
    PES_CLEAN_DATA,
    cen_variable_types,
    pes_variable_types,
)

if not os.path.exists(CLERICAL_PATH + "CLERICAL_SEARCH_RESULTS/"):
    os.makedirs(CLERICAL_PATH + "CLERICAL_SEARCH_RESULTS/")

# Cleaned data
CEN = pd.read_csv(
    CEN_CLEAN_DATA, dtype=cen_variable_types, iterator=False, index_col=False
)
PES = pd.read_csv(
    PES_CLEAN_DATA, dtype=pes_variable_types, iterator=False, index_col=False
)

# Read in all matches up to clerical search
file_path = "Enter_file_name_of_all_matches.csv"
prev_matches = pd.read_csv(OUTPUT_PATH + file_path, iterator=False, index_col=False)

# Collect unique PES EAs to loop over
PES_EA_list = PES["Eaid_pes"].drop_duplicates().tolist()

# DataFrame to append results to
all_ea_results = pd.DataFrame()

# Loop through EAs and combine all clerical results from EA
for EA in PES_EA_list:
    # Only loop through EAs where at least one match was made
    if os.path.exists(
        CLERICAL_PATH + f"CLERICAL_SEARCH_RESULTS/Clerical_Search_{str(EA)}_RESULTS.csv"
    ):
        # Read in results from an EA
        ea_results = pd.read_csv(
            CLERICAL_PATH
            + f"CLERICAL_SEARCH_RESULTS/Clerical_Search_{str(EA)}_RESULTS.csv",
            iterator=False,
            index_col=False,
        )

        # Combine
        all_ea_results = all_ea_results.append(ea_results[["puid_cen", "puid_pes"]])

    else:
        warnings.warn(f"No clerical search matches made from EA {str(EA)}")

if len(all_ea_results) < 1:
    warnings.warn("No clerical search matches made from any EA!")
    all_ea_results[["puid_cen", "puid_pes"]] = None, None

# Add Indicators so that previous matches will concat with new matches
all_ea_results["Match_Type"] = "Clerical_Search"
all_ea_results["CLERICAL"] = 1
all_ea_results["MK"] = 0

# Join on and select required variables
all_ea_results = all_ea_results.merge(CEN, on="puid_cen", how="left")
all_ea_results = all_ea_results.merge(PES, on="puid_pes", how="left")
all_ea_results = all_ea_results[OUTPUT_VARIABLES]

# Combine above clerical results with all previous matches
df = pd.concat([prev_matches, all_ea_results])

# Save
df.to_csv(OUTPUT_PATH + "Final_Set_of_Matches.csv", header=True, index=False)
