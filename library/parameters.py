import os

# this mess of path finding should always set the working directory to the parent (project) folder so
# all file paths work correctly (and dynamically!) regardless of file used
os.chdir(os.path.join(os.path.join(__file__, os.pardir), os.pardir))

SYS_PATH = "C:/Users/tomlic/PES_MATCH/"

ROOT_DIR = os.getcwd()

DATA_PATH = "Data/"

LIB_PATH = "lib/"

CHECKPOINT_PATH = DATA_PATH + "Checkpoints/"

CLERICAL_PATH = DATA_PATH + "Clerical/"

OUTPUT_PATH = DATA_PATH + "Outputs/"

CLERICAL_VARIABLES = ['puid', 'hid', 'fullname', 'full_dob', 'relationship', 'sex', 'marstat', 'telephone', 'Eaid']

OUTPUT_VARIABLES = ['puid_cen', 'puid_pes', 'MK', 'Match_Type', 'CLERICAL']
