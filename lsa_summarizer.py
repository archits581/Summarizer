from __future__ import absolute_import;
from __future__ import division, print_function, unicode_literals

import nltk;
import numpy;
import math;
from nltk.corpus import stopwords;
from nltk.tokenize import sent_tokenize, word_tokenize;
from numpy.linalg import svd as single_value_decomposition;

from operator import attrgetter
from collections import namedtuple, Counter;
# from utils import ItemsCount;

SentenceInfo = namedtuple("SentenceInfo", ("sentence", "order", "rating",))
stop_words = stopwords.words("english");

summ_length = 0.4;
min_dimensions = 3;
reduction_ratio = 1/1;

nltk.download("punkt");
nltk.download("stopwords");

def lsa_summarize(text):
	# Creating dictionary of words
	dictionary = create_dictionary(text);

	#Tokenize sentences
	sentences = sent_tokenize(text);
	print("Text Length: {}".format(len(sentences)));
	sentence_count = int(len(sentences) * summ_length); 

	matrix = create_matrix(text, dictionary);
	matrix = calculate_term_frequency(matrix);
	u, sigma, v_matrix = single_value_decomposition(matrix, full_matrices = False);
	ranks = iter(calculate_ranks(sigma, v_matrix));
	return get_important_sentences(sentences, sentence_count, lambda s: next(ranks));

def create_dictionary(text):
	words = word_tokenize(text);
	words = tuple(words);
	words = map(normalize_word, words)
	unique_words = frozenset(word for word in words if word not in stop_words);
	return dict((word, i) for i, word in enumerate(unique_words));

def create_matrix(text, dictionary):
	sentences = sent_tokenize(text);
	word_count = len(dictionary);
	sentence_count = len(sentences);
	if(word_count < sentence_count):
		print("Word count is less than sentence count. LSA algorithm may fail");

	matrix = numpy.zeros((word_count, sentence_count));
	for col, sentence in enumerate(sentences):
		words = word_tokenize(sentence);
		for word in words:
			if(word in dictionary):
				row = dictionary[word];
				matrix[row, col] += 1;
	return matrix;

def calculate_term_frequency(matrix, smooth=0.4):
	max_word_frequencies = numpy.max(matrix, axis = 0);
	rows, cols = matrix.shape
	for i in range(rows):
		for j in range(cols):
			max_word_frequency = max_word_frequencies[j];
			if(max_word_frequency != 0):
				frequency = matrix[i, j]/max_word_frequency;
				matrix[i, j] = smooth + (1.0 - smooth)* frequency;
	return matrix;

def calculate_ranks(sigma, v_matrix):
	dimensions = max(min_dimensions, int(len(sigma) * reduction_ratio));
	powered_sigma = tuple(s**2 if i < dimensions else 0.0 for i, s in enumerate(sigma));

	ranks = [];
	for i in v_matrix.T:
		rank = sum(s* v**2 for s, v in zip(powered_sigma, i));
		ranks.append(math.sqrt(rank));

	return ranks;

def get_important_sentences(sentences, count, rating):
	rate = rating
	if(isinstance(rating, dict)):
		assert not args and not kwargs;
		rate = lambda s: rating[s];

	infos = (SentenceInfo(s, o, rate(s,)) for o, s in enumerate(sentences));

	infos = sorted(infos, key = attrgetter("rating"), reverse=True);
	# if(not isinstance(count, ItemsCount)):
	# 	count = ItemsCount(count);
	# infos = count(infos);
	infos = Counter(infos);
	infos = sorted(infos, key = attrgetter("order"))[:count];
	return tuple(i.sentence for i in infos);

def normalize_word(word):
	return word.lower();