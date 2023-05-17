import numpy as np
import pandas as pd

from pes_match.cleaning import (
    alpha_name,
    change_types,
    clean_name,
    concat,
    derive_list,
    n_gram,
    pad_column,
    replace_vals,
    select,
    soundex,
)
from pes_match.parameters import DATA_PATH, PES_CLEAN_DATA

# Raw data
df = pd.read_csv(DATA_PATH + "Mock_Data_Pes.csv", iterator=False, index_col=False)

# Derive clean names
for var in ["forename", "middlenm", "last_name"]:
    df = clean_name(df, var)

# Derive full name
df = concat(
    df,
    output_col="fullname",
    sep=" ",
    columns=["forename_clean", "middlenm_clean", "last_name_clean"],
)

# Derive Alphaname
df = alpha_name(df, input_col="fullname", output_col="alpha_name")

# Replace nulls
df = replace_vals(
    df,
    dic={"-8": np.NaN},
    subset=[
        "forename_clean",
        "middlenm_clean",
        "last_name_clean",
        "fullname",
        "alpha_name",
    ],
)

# Collect list of clean forenames in each household
df = derive_list(
    df, partition_var="hid", list_var="forename_clean", output_col="forename_list"
)

# Initials
df = n_gram(
    df, input_col="forename_clean", output_col="forename_init", missing_value="-8", n=1
)
df = n_gram(
    df,
    input_col="last_name_clean",
    output_col="last_name_init",
    missing_value="-8",
    n=1,
)

# Trigrams
df = n_gram(
    df, input_col="forename_clean", output_col="forename_tri", missing_value="-8", n=3
)
df = n_gram(
    df, input_col="last_name_clean", output_col="last_name_tri", missing_value="-8", n=3
)

# Soundex
df = soundex(
    df, input_col="forename_clean", output_col="forename_sdx", missing_value="-8"
)
df = soundex(
    df, input_col="last_name_clean", output_col="last_name_sdx", missing_value="-8"
)

# Clean Day, Month, Age & Derive full_dob
df = replace_vals(df, dic={88: np.NaN}, subset=["month", "age"])
df = replace_vals(df, dic={8888: np.NaN}, subset=["year"])
df = change_types(
    change_types(df, input_cols=["year", "month", "age"], types="int"),
    input_cols=["year", "month", "age"],
    types="str",
)
df = pad_column(df, input_col="month", output_col="month", length=2)
df = concat(df, output_col="full_dob", sep="/", columns=["month", "year"])

# Clean other matching variables
df = change_types(
    replace_vals(df, dic={88: np.NaN}, subset=["marstat"]),
    input_cols="marstat",
    types=np.int64,
)
df = change_types(
    replace_vals(df, dic={88: np.NaN}, subset=["relationship"]),
    input_cols="relationship",
    types=np.int64,
)
df = change_types(
    replace_vals(df, dic={88: np.NaN}, subset=["telephone"]),
    input_cols="telephone",
    types=np.int64,
)

# Selected columns
df = select(
    df,
    columns=[
        "hid",
        "puid",
        "month",
        "year",
        "age",
        "HoH",
        "marstat",
        "relationship",
        "sex",
        "telephone",
        "Eaid",
        "forename_clean",
        "middlenm_clean",
        "last_name_clean",
        "fullname",
        "alpha_name",
        "forename_init",
        "last_name_init",
        "forename_tri",
        "last_name_tri",
        "forename_sdx",
        "last_name_sdx",
        "full_dob",
        "forename_list",
    ],
)

# Suffixes
df = df.add_suffix("_pes")

# Save
df.to_csv(PES_CLEAN_DATA, header=True, index=False)
