import pandas as pd

from pes_match.cluster import cluster_number
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

# Read in matches to sample from (e.g., from stage 1, stage 2 etc.)
df = pd.read_csv(
    OUTPUT_PATH + "Stage_1_All_Matches.csv", iterator=False, index_col=False
)[["puid_pes", "puid_cen", "Match_Type", "MK"]]

# Join on required variables
df = df.merge(CEN, on="puid_cen", how="left")
df = df.merge(PES, on="puid_pes", how="left")

# Example: View stage 1 associative matches
df = df[df.Match_Type == "Stage_1_Associative"]

# Take sample of 20 from each MK
for MK in df.MK.drop_duplicates():
    sample_size = len(df[df.MK == MK])

    if sample_size < 20:
        sample_MK = df[df.MK == MK].sample(sample_size)
    else:
        sample_MK = df[df.MK == MK].sample(20)
    if MK == 1:
        sample = sample_MK
    else:
        sample = pd.concat([sample, sample_MK])

# Add cluster number to records
CROW_records = cluster_number(
    df=sample, id_column="puid", suffix_1="_cen", suffix_2="_pes"
)  # Add cluster ID

# Save records for clerical in the correct format for CROW
CROW_variables = [
    "puid",
    "hid",
    "fullname",
    "full_dob",
    "relationship",
    "sex",
    "marstat",
    "HoH",
    "Eaid",
    "forename_list",
    "telephone",
]
CROW_records_1 = CROW_records[
    [var + "_cen" for var in CROW_variables] + ["Cluster_Number", "MK"]
].drop_duplicates()
CROW_records_2 = CROW_records[
    [var + "_pes" for var in CROW_variables] + ["Cluster_Number", "MK"]
].drop_duplicates()
CROW_records_1.columns = CROW_records_1.columns.str.replace(r"_cen$", "", regex=True)
CROW_records_2.columns = CROW_records_2.columns.str.replace(r"_pes$", "", regex=True)
CROW_records_1["Source_Dataset"] = "cen"  # Dataset indicator
CROW_records_2["Source_Dataset"] = "pes"  # Dataset indicator
CROW_records_final = pd.concat([CROW_records_1, CROW_records_2], axis=0).sort_values(
    ["Cluster_Number", "Source_Dataset"]
)  # Combine two datasets together

# Save
CROW_records_final.to_csv(
    CLERICAL_PATH + "Stage_1_EA_Associative_MK_QA.csv", header=True, index=False
)
