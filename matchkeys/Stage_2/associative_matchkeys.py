import pandas as pd
from library.matching import run_single_matchkey


def run_matchkeys(cen, pes, level):
    """Function to define and run Stage 2 Associative Matchkeys"""

    mk1 = run_single_matchkey(df1=cen, df2=pes, suffix_1="_cen", suffix_2="_pes", hh_id="hid", level=level, matchkey=1, variables=["forename_tri", "year"])

    matchkey_list = [mk1]

    df = pd.DataFrame()

    for i, matches in enumerate(matchkey_list):
        matches["MK"] = i + 1
        df = pd.concat([df, matches], axis=0)
        df["Min_MK"] = df.groupby(["puid_cen", "puid_pes"])["MK"].transform("min")
        df = df[df.Min_MK == df.MK].drop(["Min_MK"], axis=1)
    return df
