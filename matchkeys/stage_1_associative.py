def run_matchkeys(cen, pes, level):
    import pandas as pd
    from library.matching import run_single_matchkey

    "Stage 1 Associative list"
    mk1 = run_single_matchkey(cen, pes, level=level, matchkey=1, variables=['forename_clean'])
    mk2 = run_single_matchkey(cen, pes, level=level, matchkey=2, variables=['full_dob'])

    matchkey_list = [mk1, mk2]

    df = pd.DataFrame()

    for i, matches in enumerate(matchkey_list):
        matches['MK'] = i + 1

        df = pd.concat([df, matches], axis=0)

        df['Min_MK'] = df.groupby(['puid_cen', 'puid_pes'])['MK'].transform('min')

        df = df[df.Min_MK == df.MK].drop(['Min_MK'], axis=1)

    return df
