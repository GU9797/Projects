from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib
matplotlib.use('agg')
import pylab as plt
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns
import pandas as pd
import sys
import os

print("Reading dataset")
data = pd.read_csv('data1.csv', sep='\t')
data1 = data.fillna(0)
print(data1.shape)
print("Splitting Dataset")
base_info = data1.iloc[:, :4]
cat_vec = data1.iloc[:, 4:]
print(cat_vec.shape)
print("normalizing dataset")
catvec_std = StandardScaler().fit_transform(cat_vec)

plt.figure()
f, ax = plt.subplots(figsize=(12,10))
plt.title('Pearson Correlation of Features')
sns.heatmap(pd.DataFrame(catvec_std).astype(float).corr(), linewidths=0.25, vmax=1.0, square=True,
           cmap="YlGnBu", linecolor='black', annot=True)
plt.savefig("cat_feature_correlation_test")

print("finished saving fig")

'''
(Used for calculating optimal number of clusters)

Sum_of_squared_distances = []
K = range(1,15)
for k in K:
    km = KMeans(n_clusters=k)
    km = km.fit(clf_fit)
    Sum_of_squared_distances.append(km.inertia_)

plt.figure()
plt.plot(K, Sum_of_squared_distances, 'bx-')
plt.xlabel('k')
plt.ylabel('Sum_of_squared_distances')
plt.title('Elbow Method For Optimal k')
plt.show()
'''

'''
(Used for visualizing correlation between top 3 categories)

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
xs = cat_vec.iloc[:, 0]
ys = cat_vec.iloc[:, 1]
zs = cat_vec.iloc[:, 2]
for i in range(xs):

    ax.scatter(xs[i], ys[i], zs[i], c=c, marker=m)

ax.scatter(xs, ys, zs)

ax.set_xlabel('womensclothing')
ax.set_ylabel('womensaccesories')
ax.set_zlabel('beauty')

plt.show()
'''
kmeans = KMeans(n_clusters = 6)

#Compute cluster centers and predict cluster indices
X_clustered = kmeans.fit_predict(catvec_std)
print("making cluster dict")
cluster_index_map = {0: [], 1: [], 2: [], 3: [], 4: [], 5: []}
i = 0
for cluster in X_clustered:
    cluster_index_map[cluster].append(i)
    i += 1
print("making cluster csvs")
for cluster in cluster_index_map:
    cluster_pd = data1.iloc[cluster_index_map[cluster], :]
    cluster_pd.to_csv("./cluster_csvs_test/{}_cluster.csv".format(cluster), index=False)

print("cluster centers:", kmeans.cluster_centers_)

print("Done")
