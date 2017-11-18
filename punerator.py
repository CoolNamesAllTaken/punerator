from nltk.corpus import wordnet as wn
# if the above command doesn't work, run:
#	import nltk
#	nltk.download()

import wordCostUtil as wc

import shell, util, collections, copy

'''
TODO:
- decide which definition of the word the user means (probably the first, but maybe use machine learning?)
- homophones: expand the defintion of pun to be both meaning and sounds like (more like a traditional puns)
	. list of words that sounds similar and compare based on sound instead of definition. output both.
- heterophones? 
'''

def subs(sentence):
	words = sentence.split()
	print(words)
	for word in words:
		print("word={}, substitutions={}".format(word, util.synonyms(word)))

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
	theme_synset = wn.synsets(theme)[0] # TODO: figure out which synset to use
	print(theme_synset)
	def compare_words(word, theme_synset):
		word_synset = wn.synsets(word)[0] # TODO: make not first synset
		print("word={} score={}".format(word, word_synset.wup_similarity(theme_synset)))
		return word_synset.wup_similarity(theme_synset) # score is wu-palmer similarity between swapped word and theme word
	swaps.sort(key=lambda swap: compare_words(swap[0], theme_synset), reverse=True) # sort swaps by similarity of swapped word to theme word
	print("sorted swaps={}".format(swaps))

	best_swaps = swaps[1:5]
	for curr_swap in best_swaps:
		words_copy = copy.deepcopy(words)
		words_copy[curr_swap[1]] = curr_swap[0]
		print(' '.join(words_copy))

############################################################
# Actual attempt at AI

class PunnificationProblem(util.SearchProblem):
	def __init__(self, queryTheme, querySentence, bigramCost, possibleSwaps):
		self.queryTheme = queryTheme
		self.querySentence = querySentence
		self.bigramCost = bigramCost
		self.possibleSwaps = possibleSwaps

	def startState(self):
		return (wc.SENTENCE_BEGIN, 0)
	def isEnd(self, state):
		return state[1] >= len(self.querySentence)

	def succAndCost(self, state):
		edges = []
		# print("state={}".format(state[0]))
		swaps = self.possibleSwaps(self.querySentence[state[1]])
		# print("  possibleFills={}".format(fills))
		if (len(swaps) == 0): # no valid swaps, just append current string and move on
			swap = self.querySentence[state[1]]
			action = swap
			newState = (swap, state[1] + 1)
			cost = self.bigramCost(state[0], newState[0])
			edges.append((action, newState, cost))
			return edges
		for swap in swaps: # found valid fills, step through them and create edges
			action = swap
			newState = (swap, state[1] + 1)
			cost = self.bigramCost(state[0], newState[0])
			# print("    action={} newState={} cost={}".format(action, newState, cost))
			edges.append((action, newState, cost))

		return edges

def punnify_ai(queryTheme, querySentence):
	if len(querySentence) == 0:
		print('QUERY SENTENCE HAS NO WORDS')
		return ''
		
	_, bigramCost = wc.fetchCosts()
	possibleSwaps = util.synonyms

	ucs = util.UniformCostSearch(verbose=1)
	ucs.solve(PunnificationProblem(queryTheme, querySentence, bigramCost, possibleSwaps))

	if (ucs.actions == None):
		print("NO SUBSTITUTIONS FOUND")
		return querySentence

	return ' '.join(ucs.actions)

if __name__ == '__main__':
	shell.main()