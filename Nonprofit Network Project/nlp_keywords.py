
import collections
import csv
import nltk
import os
import re
import string
import urllib3
import progressbar
import operator
from stemming.porter2 import stem
import pandas as pd

def write_original_file():
	col_names = ["name", "address", "desc", "active","latest","info_year","revenue", "expenses", "assets", "liabilites","cont_rev", "other_rev"]
	df = pd.read_csv("nonprofits.csv", sep="|", names=col_names, index_col=False)
	storage = collections.defaultdict(list)
	with open("descriptions.txt", "w") as f:
		for tup in df.itertuples():
			writing = str(tup[1]) + " "
			if str(tup[3]) != "nan":
				writing += str(tup[3])
			f.write(writing + "\n")

write_original_file()

def get_stemmed_stops():
	http = urllib3.PoolManager()
	r = http.request('GET', 'http://www.ai.mit.edu/projects/jmlr/papers/volume5/lewis04a/a11-smart-stop-list/english.stop')
	cleaned_stops = str(r.data).replace('\\n', ' ').split(' ')
	stemmed_stops = set()
	cleaned_stops += []
	for word in cleaned_stops:
		stemmed_stops.add(stem(word))
	return stemmed_stops

STOP_WORDS = get_stemmed_stops()

def chop_text(text):
	unigrams = get_unigrams(text)
	trigrams = list(nltk.trigrams(unigrams))
	return unigrams, trigrams

def get_unigrams(text):
    '''
    Removes punctuation, makes lowercase and tokenizes the text.
    '''
    depunctuator = str.maketrans('', '', string.punctuation)
    text = text.lower().translate(depunctuator)
    text_tokenized = nltk.tokenize.word_tokenize(text)
    unigrams = []
    for word in text_tokenized:
        stemmed = stem(word)
        if stemmed not in STOP_WORDS and re.search("[a-z]", stemmed):
        	unigrams.append(stemmed)
    return unigrams

def get_all_unis_tris(l):
	uni_set = set()
	tri_set = set()
	for uni, tri in l:
		for u in uni:
			uni_set.add(u)
		for t in tri:
			tri_set.add(t)
	return uni_set, tri_set

def count_uni_tri_grams(corpus):
	u_counts = collections.defaultdict(int)
	t_counts = collections.defaultdict(int)
	for doc in corpus:
		for u in doc[0]:
			u_counts[u] += 1
		for t in doc[1]:
			t_counts[t] += 1
	return u_counts, t_counts

def find_most_frequent(u_counts, t_counts):
	u_freq = sorted(u_counts.items(), reverse=True, key=operator.itemgetter(1))
	t_freq = sorted(t_counts.items(), reverse=True, key=operator.itemgetter(1))
	top_1k_u = [x[0] for x in u_freq[:1000]]
	top_500_t = [x[0] for x in t_freq[:500]]
	return top_1k_u, top_500_t

def write_dtm(uni_tri_list, u_freq, t_freq):
	tri_strings = ['.'.join(t) for t in t_freq]
	columns = u_freq + tri_strings
	with open('dtm.csv', 'w', newline='') as csvfile:
		spamwriter = csv.writer(csvfile)
		spamwriter.writerow(columns)
		bar = progressbar.ProgressBar()
		for doc in bar(uni_tri_list):
			working = []
			for u in u_freq:
				working.append(doc[0].count(u))
			for t in t_freq:
				working.append(doc[1].count(t))
			spamwriter.writerow(working)

###

with open("descriptions.txt", "r") as f:
	docs = f.readlines()
uni_tri_list = []
for doc in docs:
	uni, tri = chop_text(doc)
	uni_tri_list.append([uni,tri])
u_set, t_set = get_all_unis_tris(uni_tri_list)
u_count, t_count = count_uni_tri_grams(uni_tri_list)
u_freq, t_freq = find_most_frequent(u_count, t_count)
write_dtm(uni_tri_list, u_freq, t_freq)
