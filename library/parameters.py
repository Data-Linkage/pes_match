import os

# This path should always set the working directory to the parent (project) folder so
# all file paths work correctly (and dynamically!) regardless of file used
os.chdir(os.path.join(os.path.join(__file__, os.pardir), os.pardir))

ROOT_DIR = os.getcwd()

SYS_PATH = "C:/Users/tomlic/PES_MATCH/"

DATA_PATH = "Data/"

LIB_PATH = "library/"

CHECKPOINT_PATH = DATA_PATH + "Checkpoints/"

CLERICAL_PATH = DATA_PATH + "Clerical/"

OUTPUT_PATH = DATA_PATH + "Outputs/"

CEN_CLEAN_DATA = DATA_PATH + "cen_cleaned_CT.csv"
PES_CLEAN_DATA = DATA_PATH + "pes_cleaned_CT.csv"

CLERICAL_VARIABLES = ['puid', 'hid', 'fullname', 'full_dob', 'relationship', 'sex', 'marstat', 'telephone', 'Eaid']

OUTPUT_VARIABLES = ['puid_cen', 'puid_pes', 'MK', 'Match_Type', 'CLERICAL']

variable_types = {'hid': str, 'puid': str, 'month': str, 'year': str, 'age': str, 'marstat': float,
                  'relationship': float, 'sex': str, 'telephone': float, 'Eaid': str}
cen_variable_types = {key + '_cen': val for key, val in variable_types.items()}
pes_variable_types = {key + '_pes': val for key, val in variable_types.items()}
