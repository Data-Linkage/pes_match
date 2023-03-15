import networkx as nx
import pandas as pd


# Cluster Number function
def cluster_number(df, id_column='puid', suffix_1="_cen", suffix_2="_pes"):
    # Columns
    id_1 = id_column + suffix_1
    id_2 = id_column + suffix_2
    df_cluster = df[[id_1, id_2]].copy()

    g = nx.from_edgelist(df_cluster.to_numpy().tolist())

    results = []
    for i, item in enumerate(list(nx.connected_components(g))):
        for ids in item:
            results.append([ids, i + 1])

    results_df = pd.DataFrame(results, columns=[id_column, "Cluster_Number"])
    df_merged = df.merge(results_df, how="inner", left_on=id_1, right_on=id_column)

    return df_merged

# ## test code
# df = pd.DataFrame({"id_1":["C1","C2","C3","C4","C5","C6","C7","C8","C9","C10","C1"],
#                    "id_2":["P1","P1","P2","P1","P3","P5","P3","P8","P9","P8", "P11"]})
#
#
# output = cluster_number(df = df, id_column='id', suffix_1="_1", suffix_2="_2")
# print(output)
