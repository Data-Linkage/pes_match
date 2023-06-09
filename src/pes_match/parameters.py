import numpy as np

# Folder paths
DATA_PATH = "Data/"
CHECKPOINT_PATH = DATA_PATH + "Checkpoints/"
CLERICAL_PATH = DATA_PATH + "Clerical/"
OUTPUT_PATH = DATA_PATH + "Outputs/"

# Cleaned data paths
CEN_CLEAN_DATA = DATA_PATH + "cen_cleaned_CT.csv"
PES_CLEAN_DATA = DATA_PATH + "pes_cleaned_CT.csv"

# Variables to save in crow outputs & final outputs
CLERICAL_VARIABLES = [
    "puid",
    "hid",
    "fullname",
    "full_dob",
    "relationship",
    "HoH",
    "sex",
    "marstat",
    "telephone",
    "forename_list",
    "Eaid",
]
OUTPUT_VARIABLES = ["puid_cen", "puid_pes", "MK", "Match_Type", "CLERICAL"]

# Variable types for cleaned data
variable_types = {
    "hid": str,
    "puid": str,
    "month": str,
    "year": str,
    "age": np.int64,
    "marstat": np.int64,
    "relationship": np.int64,
    "sex": str,
    "telephone": np.int64,
    "Eaid": str,
}
cen_variable_types = {key + "_cen": val for key, val in variable_types.items()}
pes_variable_types = {key + "_pes": val for key, val in variable_types.items()}
