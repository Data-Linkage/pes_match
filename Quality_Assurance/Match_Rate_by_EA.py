import pandas as pd

from pes_match.parameters import (
    CEN_CLEAN_DATA,
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

# Read in matches made so far (e.g., from stage 1, stage 2 etc.)
matches = pd.read_csv(
    OUTPUT_PATH + "Stage_1_All_Matches.csv", iterator=False, index_col=False
).drop_duplicates(["puid_pes"])

# Join on required variables
matches = matches.merge(CEN, on="puid_cen", how="left")
matches = matches.merge(PES, on="puid_pes", how="left")

# Total PES records in each EA
Total = PES.groupby(["Eaid_pes"]).size()
Total = pd.DataFrame({"Eaid_pes": Total.index, "TOTAL_PES": Total.values})

# Total matched PES in each EA
Matched = matches.drop_duplicates(["puid_pes"]).groupby(["Eaid_pes"]).size()
Matched = pd.DataFrame({"Eaid_pes": Matched.index, "MATCHED_PES": Matched.values})

# Total CEN records in each EA
Total2 = CEN.groupby(["Eaid_cen"]).size()
Total2 = pd.DataFrame({"Eaid_cen": Total2.index, "TOTAL_CEN": Total2.values})

# Combine
df = Total.merge(Matched, on="Eaid_pes", how="left")
df = df.merge(Total2, left_on="Eaid_pes", right_on="Eaid_cen", how="left")

# Percentage
df["Percentage_Matched_PES"] = df["MATCHED_PES"] / df["TOTAL_PES"] * 100
