import pandas as pd
import sys
import os

data1 = pd.read_csv('./cluster_csvs/5_cluster.csv', sep=',')
percent_df = pd.DataFrame(columns=data1.columns.values[4:], index=list(range(6)))

for i in range(6):
    print("{}_Cluster".format(i))
    print("---------------------------------")
    data = pd.read_csv('./cluster_csvs/{}_cluster.csv'.format(i), sep=',')
    data['womensclothing'] = data['womensclothing'] * (56867475 / 10000000)
    data['womensaccesories'] = data['womensaccesories'] * (19135465 / 10000000)
    data['beauty'] = data['beauty'] * (19130684 / 10000000)
    data['kids'] = data['kids'] * (11657964 / 10000000)
    data['womensbags'] = data['womensbags'] * (11372703 / 10000000)
    data['womensshoes'] = data['womensshoes'] * (10794722 / 10000000)
    data['cellphonesdigital'] = data['cellphonesdigital'] * (9974967 / 10000000)
    data['mensclothing'] = data['mensclothing'] * (11138937 / 10000000)
    data['decor'] = data['decor'] * (6539236 / 10000000)
    data['other'] = data['other'] * (26179238 / 10000000)
    summ = data.iloc[:, 4:].values.sum()
    for column in data.columns.values[4:]:
        total = sum(data[column])
        print("avg # {} orders:".format(column), total / len(data[column]))
        percent_df[column].loc[i] = total / summ
    print("---------------------------------")
    print("total # orders:", summ)
    print("---------------------------------")

print(percent_df)
percent_df.to_csv("cluster_ratio.csv", sep='\t', index=False)
print("Done")
