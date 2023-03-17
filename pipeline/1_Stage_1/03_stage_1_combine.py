import pandas as pd
from library.parameters import *

# File names
matchkey_unique = 'Stage_1_Matchkey_Unique_Matches'
matchkey_nonunique = 'Stage_1_Matchkey_Conflict_Matches'
associative = 'Stage_1_Associative_Unique_Matches'

# Read in and combine
df1 = pd.read_csv(CHECKPOINT_PATH + matchkey_unique + '.csv', index_col=False)[OUTPUT_VARIABLES]
df2 = pd.read_csv(CHECKPOINT_PATH + matchkey_nonunique + '.csv', index_col=False)[OUTPUT_VARIABLES]
df3 = pd.read_csv(CHECKPOINT_PATH + associative + '.csv', index_col=False)[OUTPUT_VARIABLES]
all_matches = pd.concat([df1, df2, df3])

# Save to output folder
all_matches.to_csv(OUTPUT_PATH + 'Stage_1_All_Matches.csv', header=True, index=False)
