from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
# if the above command doesn't work, run:
#	import nltk
#	nltk.download()
#	nltk.download(stopwords

import wordCostUtil as wc
import shell, util, collections, copy, math

'''
TODO:
- decide which definition of the word the user means (probably the first, but maybe use machine learning?)
- homophones: expand the defintion of pun to be both meaning and sounds like (more like a traditional puns)
	. list of words that sounds similar and compare based on sound instead of definition. output both.
- heterophones? 
'''

def substitutions(sentence):
	"""
	Lists the possible substitutions for each word in a sentence.  A good way to test the thesaurus.
	"""
	words = sentence.split()
	print(words)
	for word in words:
		print('word={}, substitutions={}'.format(word, util.syn_thesaurus(word)))

def similarity(word1, word2, word2vecModel):
	"""
	Calculates the similarity between two words.  A good way to test the word2vec model.
	"""
	if word1 not in word2vecModel.wv.vocab or word2 not in word2vecModel.wv.vocab:
		print('Word not contained in word vector model') # word not contained in word vector model, prune
		return
	print('word1={}, word2={}, similarity={}'.format(word1, word2, word2vecModel.similarity(word1, word2)))
############################################################

# Dumb baseline that probabaly works

def punnify_baseline(theme, sentence):
	"""Punnify a sentence using a particular theme
	Inputs:
		theme - string representing pun theme
		sentence - words to punnify
	Outputs:
	"""	
	words = sentence.split()
	swaps = []
	for word_index, word in enumerate(words):
		for synonym in util.synonyms(word):
			swaps.append((synonym, word_index))
	print("unsorted swaps={}".format(swaps))
	theme_synset = wn.synsets(theme)[0] # Assuming the first synset is the definition we are looking for
	print(theme_synset)
	def compare_words(word, theme_synset):
		word_synset = wn.synsets(word)[0] #Assuming the first synset is what we are looking for
		print("word={} score={}".format(word, word_synset.wup_similarity(theme_synset)))
		return word_synset.wup_similarity(theme_synset) # score is wu-palmer similarity between swapped word and theme word
	swaps.sort(key=lambda swap: compare_words(swap[0], theme_synset), reverse=True) # sort swaps by similarity of swapped word to theme word
	print("sorted swaps={}".format(swaps))

	best_swaps = swaps[0:5]
	for curr_swap in best_swaps:
		words_copy = copy.deepcopy(words)
		words_copy[curr_swap[1]] = curr_swap[0]
		print(' '.join(words_copy))

############################################################
# Actual attempt at AI

class PunnificationProblem(util.SearchProblem):
	def __init__(self, queryTheme, queryWords, costFunc, possibleSwaps):
		# print("New PunnificationProblem: queryWords={} bigramCost={}".format(queryWords, bigramCost))
		self.queryTheme = queryTheme
		self.queryWords = queryWords
		self.costFunc = costFunc
		self.possibleSwaps = possibleSwaps

		self.possibleSwapsDict = collections.defaultdict(list) # cache swaps for faster performance

	def startState(self):
		return (wc.SENTENCE_BEGIN, 0) # state is (currWord, queryWords index)
	def isEnd(self, state):
		return state[1] >= len(self.queryWords)

	def succAndCost(self, state):
		edges = []
		# print("state={}".format(state[0]))
		lastWord = self.queryWords[state[1]]
		if (lastWord in self.possibleSwapsDict): # swaps have been cached
			swaps = self.possibleSwapsDict[lastWord]
		else: # add swaps to cache
			swaps = self.possibleSwaps(lastWord)
			self.possibleSwapsDict[lastWord] = swaps
		# print("  word={} possibleSwaps={}".format(lastWord, swaps))
		edges.append((lastWord, (lastWord, state[1] + 1), 0)) # swap in existing word = 0 cost
		for swap in swaps: # found valid fills, step through them and create edges
			action = swap
			newState = (swap, state[1] + 1)
			cost = self.costFunc(self.queryTheme, state[0], swap)
			# print("    action={} newState={} cost={}".format(action, newState, cost))
			edges.append((action, newState, cost))
		return edges

def punnify_ai(queryTheme, querySentence, bigramCost, word2vecModel, includeBigram):
	queryWords = querySentence.split()

	for word in queryWords:
		if word not in word2vecModel.wv.vocab and word not in stopwords.words('english'):
			print('ERROR: query sentence contains non-stopwords that are not contained in word2vec model.')
			return ''

	if len(queryWords) == 0:
		print('ERROR: query sentence has no words.')
		return ''
		
	def possibleSwaps(queryWord):
		if queryWord in stopwords.words('english'):
			return [queryWord] # word is a stopword (not interesting), no valid synonyms
		else:
			return util.syn_thesaurus(queryWord) # word can be replaced with synonyms
	def costFunc(queryTheme, prevWord, swap):
		if swap in stopwords.words('english') or swap == prevWord: # word is in stopwords, not an actual substitution
			return 0
		elif swap not in word2vecModel.wv.vocab: # word not in word vector model
			# print("{} not in word2vec model".format(swap))
			return float('inf') # prune
		similarity = word2vecModel.similarity(queryTheme, swap) # -1 to 1, 1 is most similar
		if similarity < 0:
			# print("{} - {} similarity is negative".format(queryTheme, swap))
			return float('inf') # word has an opposite meaning from theme, prune
		if includeBigram: return bigramCost(prevWord, swap) / similarity
		else: return 1 / similarity

	back = util.BacktrackingSearch(verbose=1)
	back.solve(PunnificationProblem(queryTheme, queryWords, costFunc, possibleSwaps))

	if (back.actions == None):
		print('ERROR: no substitutions found.')
		return queryWords

	# print back.solutions[0:5]
	
	for pun, cost in back.solutions[0:5]:
	 	print(' '.join(list(pun)))

	return ' '.join(back.solutions[0][0])

if __name__ == '__main__':
	shell.main()
