from nltk.corpus import wordnet as wn
# if the above command doesn't work, run:
#	import nltk
#	nltk.download()

import wordCostUtil as wc

import shell, util, collections, copy, math

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
	def __init__(self, queryTheme, queryWords, swapCost, possibleSwaps):
		# print("New PunnificationProblem: queryWords={} bigramCost={}".format(queryWords, bigramCost))
		self.queryTheme = queryTheme
		self.queryWords = queryWords
		self.swapCost = swapCost
		self.possibleSwaps = possibleSwaps

	def startState(self):
		return (wc.SENTENCE_BEGIN, 0) # state is (currWord, queryWords index)
	def isEnd(self, state):
		return state[1] >= len(self.queryWords)

	def succAndCost(self, state):
		edges = []
		# print("state={}".format(state[0]))
		swaps = self.possibleSwaps(self.queryWords[state[1]])
		# print("  possibleFills={}".format(fills))
		if (len(swaps) == 0): # no valid swaps, just append current string and move on
			swap = self.queryWords[state[1]]
			action = swap
			newState = (swap, state[1] + 1)
			cost = self.swapCost(self.queryTheme, state[0], swap)
			edges.append((action, newState, cost))
			return edges
		for swap in swaps: # found valid fills, step through them and create edges
			action = swap
			newState = (swap, state[1] + 1)
			cost = self.swapCost(self.queryTheme, state[0], swap)
			# print("    action={} newState={} cost={}".format(action, newState, cost))
			edges.append((action, newState, cost))

		return edges

def punnify_ai(queryTheme, querySentence, bigramCost):
	queryWords = querySentence.split()

	if len(queryWords) == 0:
		print('QUERY SENTENCE HAS NO WORDS')
		return ''
		
	possibleSwaps = util.synonyms
	def swapCost(queryTheme, queryWord, swap):
		return math.log(bigramCost(queryWord, swap)**2 * util.wup_similarity(queryTheme, swap))

	ucs = util.UniformCostSearch(verbose=1)
	ucs.solve(PunnificationProblem(queryTheme, queryWords, swapCost, possibleSwaps))

	if (ucs.actions == None):
		print("NO SUBSTITUTIONS FOUND")
		return queryWords

	return ' '.join(ucs.actions)

def punnify_meaning(queryTheme, querySentence, bigramCost):
	queryWords = querySentence.split()

	if len(queryWords) == 0:
		print('QUERY SENTENCE HAS NO WORDS')
		return ''

	print('punnify_meaning not implemented! queryTheme={} querySentence={}'.format(queryTheme, querySentence))

def punnify_sound(queryTheme, querySentence, bigramCost):
	queryWords = querySentence.split()

	if len(queryWords) == 0:
		print('QUERY SENTENCE HAS NO WORDS')
		return ''

	print('punnify_sound not implemented! queryTheme={} querySentence={}'.format(queryTheme, querySentence))

if __name__ == '__main__':
	shell.main()