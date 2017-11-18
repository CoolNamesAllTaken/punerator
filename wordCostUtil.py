import dill as pickle
# import time
import collections
import math

UNIGRAM_FILENAME = 'uni'
BIGRAM_FILENAME = 'bi'

SENTENCE_BEGIN = '-BEGIN-'

#Code from CS221 Reconstruct assignment, specifically wordsegUtil.py (CA:Yang Yuan)
def calculateCosts(path):
	unigramCounts = collections.Counter()
	totalCounts = 0
	bigramCounts = collections.Counter()
	bitotalCounts = collections.Counter()
	VOCAB_SIZE = 600000
	LONG_WORD_THRESHOLD = 5
	LENGTH_DISCOUNT = 0.15

	def cleanLine(l):
		s = l.strip().lower()
		s = s.replace('-', ' ')
		return filter(lambda c: c.isalpha() or c == ' ', s)

	def sliding(xs, windowSize):
		for i in xrange(1, len(xs) + 1):
			yield xs[max(0, i - windowSize):i]

	def bigramWindow(win):
		assert len(win) in [1, 2]
		if len(win) == 1:
			return (SENTENCE_BEGIN, win[0])
		else:
			return tuple(win)

	with open(path, 'r') as f:
		for l in f:
			ws = cleanLine(l).split()
			unigrams = [x[0] for x in sliding(ws, 1)]
			bigrams = [bigramWindow(x) for x in sliding(ws, 2)]
			totalCounts += len(unigrams)
			unigramCounts.update(unigrams)
			bigramCounts.update(bigrams)
			bitotalCounts.update([x[0] for x in bigrams])

	def unigramCost(x):
		if x not in unigramCounts:
			length = max(LONG_WORD_THRESHOLD, len(x))
			return -(length * math.log(LENGTH_DISCOUNT) + math.log(1.0) - math.log(VOCAB_SIZE))
		else:
			return math.log(totalCounts) - math.log(unigramCounts[x])

	def bigramModel(a, b):
		return math.log(bitotalCounts[a] + VOCAB_SIZE) - math.log(bigramCounts[(a, b)] + 1)

	return unigramCost, bigramModel

def createCosts(path):
	unigramCost, bigramCost = calculateCosts(path)
	pickle.dump(unigramCost, open(UNIGRAM_FILENAME, "wb"))
	pickle.dump(bigramCost, open(BIGRAM_FILENAME, "wb"))

def fetchCosts():
	unigramCost = pickle.load(open(UNIGRAM_FILENAME, "rb"))
	bigramCost = pickle.load(open(BIGRAM_FILENAME, "rb"))
	return unigramCost, bigramCost
#*********************************************************************************
#Usage Example
#*********************************************************************************

# CORPUS = 'text.txt'
# t0 = time.time()

# #if generating file
# unigramCost, bigramCost = calculateCosts(CORPUS)
# pickle.dump(unigramCost, open("uni", "wb"))
# pickle.dump(bigramCost, open("bi", "wb"))

# #if reading file
# unigramCost = pickle.load(open("uni", "rb"))
# bigramCost = pickle.load(open("bi", "rb"))


# print("unigram cost of 'and': " + str(unigramCost("and")))
# print("unigram cost of 'he': " + str(unigramCost("he")))
# print("unigram cost of 'fuck': " + str(unigramCost("fuck")))
# print("bigram cost of 'and' and 'he': " + str(bigramCost("and", "he")))
# print("bigram cost of 'and' and 'fuck': " + str(bigramCost("and", "fuck")))
# print("\n")
# print("function ran in this many seconds: " + str(time.time() - t0))