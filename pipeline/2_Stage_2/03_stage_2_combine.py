import pandas as pd
from library.parameters import CHECKPOINT_PATH, OUTPUT_PATH, OUTPUT_VARIABLES

# Stage 2 File names
matchkey_unique = "Stage_2_Matchkey_Unique_Matches"
matchkey_nonunique = "Stage_2_Matchkey_Conflict_Matches"
associative = "Stage_2_Associative_Unique_Matches"

# Read in and combine
df1 = pd.read_csv(
    CHECKPOINT_PATH + matchkey_unique + ".csv", iterator=False, index_col=False
)[OUTPUT_VARIABLES]
df2 = pd.read_csv(
    CHECKPOINT_PATH + matchkey_nonunique + ".csv", iterator=False, index_col=False
)[OUTPUT_VARIABLES]
df3 = pd.read_csv(
    CHECKPOINT_PATH + associative + ".csv", iterator=False, index_col=False
)[OUTPUT_VARIABLES]
Stage_2_matches = pd.concat([df1, df2, df3])

# Combine with Stage 1 matches
Stage_1_matches = pd.read_csv(
    OUTPUT_PATH + "Stage_1_All_Matches.csv", iterator=False, index_col=False
)[OUTPUT_VARIABLES]
all_matches = pd.concat([Stage_1_matches, Stage_2_matches])

# Save to output folder
all_matches.to_csv(OUTPUT_PATH + "Stage_2_All_Matches.csv", header=True, index=False)
