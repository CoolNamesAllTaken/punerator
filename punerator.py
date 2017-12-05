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
		print("  word={} possibleSwaps={}".format(self.queryWords[state[1]], swaps))
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

def punnify_ai(queryTheme, querySentence, bigramCost, word2vecModel):
	queryWords = querySentence.split()

	for word in queryWords:
		if word not in word2vecModel.wv.vocab:
			print('ERROR: query sentence contains words not contained in word2vec model.')
			return ''

	if len(queryWords) == 0:
		print('ERROR: query sentence has no words.')
		return ''
		
	possibleSwaps = util.syn_thesaurus
	def swapCost(queryTheme, queryWord, swap):
		# return math.log(bigramCost(queryWord, swap)**2 * word2vecModel.similarity(queryTheme, swap))
		if swap not in word2vecModel.wv.vocab:
			return float('inf') # word not contained in word vector model, prune
		similarity = word2vecModel.similarity(queryTheme, swap) # -1 to 1, 1 is most similar
		if similarity < 0:
			return float('inf') # word has an opposite meaning from theme, prune
		return bigramCost(queryWord, swap) / similarity

	ucs = util.UniformCostSearch(verbose=1)
	ucs.solve(PunnificationProblem(queryTheme, queryWords, swapCost, possibleSwaps))

	if (ucs.actions == None):
		print('ERROR: no substitutions found.')
		return queryWords

	return ' '.join(ucs.actions)

def punnify_meaning(queryTheme, querySentence, bigramCost, word2vecModel):
	BIGRAM_MAX = 13 #experimentaly defined inf value for bigram missing word from testing

	queryWords = querySentence.split()

	for word in queryWords:
		if word not in word2vecModel.wv.vocab:
			print('ERROR: query sentence contains words not contained in word2vec model.')
			return ''

	if len(queryWords) == 0:
		print('ERROR: query sentence has no words.')
		return ''

	possibleSwaps = util.syn_thesaurus
	# possibleSwaps = util.synonyms

	back = util.BacktrackingSearch()
	back.solve(queryWords, possibleSwaps, bigramCost)

	print("WEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE")
	for path in back.solutions:
		print(path)
	print("WEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE")
	
	#now take the non-infinite solutions and check pun cost and swap cost
	def w2vCost(queryWord, swapWord):
		if swapWord not in word2vecModel.wv.vocab:
			return float('inf') # word not contained in word vector model, prune
		similarity = word2vecModel.similarity(queryTheme, swapWord) # -1 to 1, 1 is most similar
		if similarity < 0:
			return float('inf') # word has an opposite meaning from theme, prune
		return similarity

	lenPhrase = len(queryWords)
	for lineNum, lineTuple in enumerate(back.solutions):
		phrase, cost = lineTuple
		words = phrase.split(' ')
		words = words[1:] #bc the first character is a ' ' in the phrase, so '' as first word
		print("words: {}".format(words))
		similarityCost = 0
		numSwaps = 1.0 #bc multiplying to default value is 1 not 0
		infinity = False
		
		for i in range(lenPhrase):
			queryWord = queryWords[i]
			swapWord = words[i]
			if queryWord != swapWord: 
				numSwaps += 1
			else:
				print("what")
			print("qWord: {}, cWord: {}".format(queryWord, swapWord))
			simCost = w2vCost(queryWord, swapWord)
			if simCost == float('inf'):
				infinity = True
				break
			similarityCost += 2 - simCost #bc 1 is best similarity but minimzing cost
		
		updatedTuple = [phrase,cost]

		print("phrase: {}, query: {}".format(phrase.strip(), queryWords))

		if infinity or (words == queryWords): updatedTuple[1] = float('inf')
		else: updatedTuple[1] *= similarityCost * numSwaps
		back.solutions[lineNum] = tuple(updatedTuple)
	
	back.pruneSolution()
	print("NEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEW")
	for path in back.solutions:
		print(path)
	print("NEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEW")
	

	# def swapCost(queryTheme, queryWord, swap):
	# 	swapPenality = 1
	# 	if queryWord == swap:
	# 		#de-incentivize a large number of swaps
	# 		if queryWord != swap: swapPenality = 10
	# 	# return math.log(bigramCost(queryWord, swap)**2 * util.wup_similarity(queryTheme, swap)) * swapPenality
	# 	return util.wup_similarity(queryTheme, swap)

	# ucs = util.UniformCostSearch(verbose=1)
	# ucs.solve(PunnificationProblem(queryTheme, queryWords, swapCost, possibleSwaps))

	# if (ucs.actions == None):
	# 	print("NO SUBSTITUTIONS FOUND")
	# 	return queryWords

	# return ' '.join(ucs.actions)

def punnify_sound(queryTheme, querySentence, bigramCost, word2vecModel):
	queryWords = querySentence.split()

	if len(queryWords) == 0:
		print('QUERY SENTENCE HAS NO WORDS')
		return ''

	print('punnify_sound not implemented! queryTheme={} querySentence={}'.format(queryTheme, querySentence))

if __name__ == '__main__':
	shell.main()