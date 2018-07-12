import pandas as pd
import numpy as np
import collections
import matplotlib.pyplot as plt
import networkx as nx 
import progressbar
import itertools
#from nxviz import CircosPlot
'''
G = nx.Graph()
orgs = []
#for letter1, letter2 in itertools.combinations("abcdefgh", 2):
#    G.add_edge(letter1, letter2) 
#G.add_node("health")
for letter in "abcdefgh":
	G.add_edge(letter, "health", weight = 4)
for letter1,letter2 in itertools.combinations("abc", 2):
	G.add_edge(letter1, letter2, weight = 2)

#OK SO WE'RE GOING TO DO SOMETHING CLEVER FROM THE CENTER...

G.add_node("zip")
for letter in "abcd":
	G.add_edge(letter, "zip")
G.add_node("size")
for letter in ("cdef"):
	G.add_edge("size", letter)
G.add_node("USER")
for alpha in ["health", "zip", "size"]:
	G.add_edge("USER", alpha)

print(nx.degree_centrality(G))
print(nx.dispersion(G, "health"))
print(nx.pagerank(G))
'''
#nx.draw(G)
#plt.show()

#127 there are a bunch under approximation that find fast lower bound on number of unique paths from one to the other
#177 degree centrality - percentage of all nodes that you're connected to...
#279 DISPERSION - checks how connected the mutual ties of U & V are... significant computational costs
#<3 344 PAGERANK - ranks based on number of links with weights! we need to rethink this a bit but... gets results and is efficientish 
#407 SIMPLE PATHS? sounds good but like not 
#408 STRUCTURAL HOLES - effective size, constraint, local constraints etc. 

col_names = ["name", "address", "desc", "active","latest","info_year","revenue", "expenses", "assets", "liabilites","cont_rev", "other_rev"]
df = pd.read_csv("nonprofits.csv", sep="|", names=col_names, index_col=False)
storage = collections.defaultdict(list)
print(len(df.loc[(df['active'] == True) & (df['desc']) & (df['revenue'])]))
for tup in df.itertuples():
	storage[tup[3]] = storage[tup[3]] + [tuple(tup)]

#storage["Cancer Diseases Disorders Medical Disciplines"]))
#3500 is the largest we've gotten it to
bar = progressbar.ProgressBar()
G = nx.Graph()
for key, value in bar(storage.items()):
	if len(value) > 1 and len(value) < 50:
		for a, b in itertools.combinations(value, 2):
			G.add_edge(tuple(a), tuple(b), weight = 0.01)
	#else:
		#for c in value:
			#G.add_node(c)
G.add_node("user")
bar = progressbar.ProgressBar()
for node in bar(G.nodes()):
	if len(node) > 3 and node[3] == "Baseball Softball Recreation Sports Leisure Athletics":
	    G.add_edge("user", node, weight = 2)
	else:	
		G.add_edge("user", node, weight = 1)
alpha = nx.pagerank(G)
for w in sorted(alpha, key = alpha.get, reverse = True)[1:5]:
	print(w)
	print(alpha[w])

'''
bravo = list(G.nodes())[1:50]
charlie = []
bar = progressbar.ProgressBar()
for b in bar(bravo): 
	alpha = nx.dispersion(G, "user", b)
	charlie.append(alpha)
for a in charlie:
	print(a)
'''
#c = CircosPlot(G)
#c.draw()

#nx.draw(G)

#plt.show()

def combo_gen(l):
	done_set = set()
	for a in l:
		for b in l:
			if a != b and (a,b) not in done_set and (b,a) not in done_set:
				done_set.add((a,b))
				yield (a,b)
