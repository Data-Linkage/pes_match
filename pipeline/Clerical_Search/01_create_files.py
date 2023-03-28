import warnings
import os
import pandas as pd
from library.parameters import (CEN_CLEAN_DATA, PES_CLEAN_DATA, cen_variable_types,
                                pes_variable_types, OUTPUT_PATH, CLERICAL_PATH)

if not os.path.exists(CLERICAL_PATH + "CLERICAL_SEARCH_DATA/"):
    os.makedirs(CLERICAL_PATH + "CLERICAL_SEARCH_DATA/")

# Cleaned data
CEN = pd.read_csv(
    CEN_CLEAN_DATA, dtype=cen_variable_types, iterator=False, index_col=False
)
PES = pd.read_csv(
    PES_CLEAN_DATA, dtype=pes_variable_types, iterator=False, index_col=False
)

# Collect unique PES EAs to loop over
PES_EA_list = PES["Eaid_pes"].drop_duplicates().tolist()

# Add matched flag to all CEN & PES records
matches = "Enter_file_name_of_all_matches.csv"
matched_cen = pd.read_csv(OUTPUT_PATH + matches, iterator=False, index_col=False)[
    ["puid_cen"]
].drop_duplicates()
matched_pes = pd.read_csv(OUTPUT_PATH + matches, iterator=False, index_col=False)[
    ["puid_pes"]
].drop_duplicates()
matched_cen[["matched_cen"]] = 1
matched_pes[["matched_pes"]] = 1
CEN = CEN.merge(matched_cen, on="puid_cen", how="left")
PES = PES.merge(matched_pes, on="puid_pes", how="left")

# Variables to view in Excel
variables = [
    "puid",
    "hid",
    "fullname",
    "full_dob",
    "telephone",
    "relationship",
    "sex",
    "marstat",
    "Eaid",
]
variables_cen = [var + "_cen" for var in variables + ["matched"]]
variables_pes = [var + "_pes" for var in variables + ["matched"]]

# Save data for every EA
for EA in PES_EA_list:
    df1 = PES[PES.Eaid_pes == EA][variables_pes]
    df2 = CEN[CEN.Eaid_cen == EA][variables_cen]

    # Warning if there are no CEN/PES residuals from an EA
    if len(df1) == 0:
        warnings.warn("No PES residuals in EA {}".format(str(EA)))

    if len(df1) == 0:
        warnings.warn("No census residuals in EA {}".format(str(EA)))

    # Spaces between each HH
    df1 = df1.reset_index(drop=True)
    mask1 = df1["hid_pes"].ne(df1["hid_pes"].shift(-1))
    all_records1 = pd.DataFrame("", index=mask1.index[mask1] + 0.5, columns=df1.columns)
    df1 = pd.concat([df1, all_records1]).sort_index().reset_index(drop=True).iloc[:-1]

    df2 = df2.reset_index(drop=True)
    mask2 = df2["hid_cen"].ne(df2["hid_cen"].shift(-1))
    all_records2 = pd.DataFrame("", index=mask2.index[mask2] + 0.5, columns=df2.columns)
    df2 = pd.concat([df2, all_records2]).sort_index().reset_index(drop=True).iloc[:-1]

    df1 = df1.drop(["hid_pes", "Eaid_pes"], axis=1)
    df2 = df2.drop(["hid_cen", "Eaid_cen"], axis=1)

    # Save
    df1.to_csv(
        CLERICAL_PATH
        + "CLERICAL_SEARCH_DATA/"
        + "Clerical_Search_{}_PES_Records.csv".format(EA),
        header=True,
        index=False,
    )
    df2.to_csv(
        CLERICAL_PATH
        + "CLERICAL_SEARCH_DATA/"
        + "Clerical_Search_{}_CEN_Records.csv".format(EA),
        header=True,
        index=False,
    )
