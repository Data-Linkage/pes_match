import pandas as pd

from pes_match.parameters import (
    CEN_CLEAN_DATA,
    CLERICAL_PATH,
    OUTPUT_PATH,
    PES_CLEAN_DATA,
    cen_variable_types,
    pes_variable_types,
)

# Cleaned data
CEN = pd.read_csv(
    CEN_CLEAN_DATA, dtype=cen_variable_types, iterator=False, index_col=False
)
PES = pd.read_csv(
    PES_CLEAN_DATA, dtype=pes_variable_types, iterator=False, index_col=False
)

# Add Matched Flag to all records
matched_cen = pd.read_csv(OUTPUT_PATH + "Stage_1_All_Matches.csv")[
    ["puid_cen"]
].drop_duplicates()
matched_pes = pd.read_csv(OUTPUT_PATH + "Stage_1_All_Matches.csv")[
    ["puid_pes"]
].drop_duplicates()
matched_cen[["matched_cen"]] = 1
matched_pes[["matched_pes"]] = 1
CEN = CEN.merge(matched_cen, on="puid_cen", how="left")
PES = PES.merge(matched_pes, on="puid_pes", how="left")

# Vars to view
variables = [
    "puid",
    "hid",
    "telephone",
    "fullname",
    "full_dob",
    "relationship",
    "sex",
    "marstat",
    "Eaid",
    "matched",
]
variables_cen = [var + "_cen" for var in variables]
variables_pes = [var + "_pes" for var in variables]

# Select one or more EAs to view:
for EA_ in ["BIRAMBOGITWA"]:
    df1 = PES[PES.Eaid_pes == EA_][variables_pes]
    df2 = CEN[CEN.Eaid_cen == EA_][variables_cen]

    # Spaces between each HH
    df1 = df1.reset_index(drop=True)
    mask1 = df1["hid_pes"].ne(df1["hid_pes"].shift(-1))
    all_records1 = pd.DataFrame("", index=mask1.index[mask1] + 0.5, columns=df1.columns)
    df1 = pd.concat([df1, all_records1]).sort_index().reset_index(drop=True).iloc[:-1]

    df2 = df2.reset_index(drop=True)
    mask2 = df2["hid_cen"].ne(df2["hid_cen"].shift(-1))
    all_records2 = pd.DataFrame("", index=mask2.index[mask2] + 0.5, columns=df2.columns)
    df2 = pd.concat([df2, all_records2]).sort_index().reset_index(drop=True).iloc[:-1]

    df1.to_csv(
        CLERICAL_PATH + "pes_EA_clerical_{}.csv".format(EA_), header=True, index=0
    )
    df2.to_csv(
        CLERICAL_PATH + "cen_EA_clerical_{}.csv".format(EA_), header=True, index=0
    )
