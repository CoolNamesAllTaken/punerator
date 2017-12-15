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
		if swap in stopwords.words('english'): # word is in stopwords, not an actual substitution
			return 0
		if swap not in word2vecModel.wv.vocab: # word not in word vector model
			# print("{} not in word2vec model".format(swap))
			return float('inf') # prune
		similarity = word2vecModel.similarity(queryTheme, swap) # -1 to 1, 1 is most similar
		if similarity < 0:
			# print("{} - {} similarity is negative".format(queryTheme, swap))
			return float('inf') # word has an opposite meaning from theme, prune
		# print("1/similarity={}".format(1/similarity))
		if includeBigram: return bigramCost(prevWord, swap) / similarity
		else: return 1 / similarity

	back = util.BacktrackingSearch()
	back.solve(PunnificationProblem(queryTheme, queryWords, costFunc, possibleSwaps))

	if (back.actions == None):
		print('ERROR: no substitutions found.')
		return queryWords

	print back.solutions[0:5]
	
	for pun, cost in back.solutions[0:5]:
	 	print(' '.join(list(pun)))

	return ' '.join(back.solutions[0][0])

def punnify_meaning(queryTheme, querySentence, bigramCost, word2vecModel):
	BIGRAM_MAX = 13 #experimentaly defined inf value for bigram missing word from testing

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

	back = util.BacktrackingSearchProblem()
	back.solve(queryWords, possibleSwaps, bigramCost)

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
		#print("words: {}".format(words))
		similarityCost = 0
		numSwaps = 1.0 #bc multiplying to default value is 1 not 0
		infinity = False
		
		for i in range(lenPhrase):
			queryWord = queryWords[i]
			swapWord = words[i]

			if swapWord in stopwords.words('english'): continue

			if queryWord != swapWord: 
				numSwaps += 1
			simCost = w2vCost(queryWord, swapWord)
			if simCost == float('inf'):
				infinity = True
				break
			similarityCost += 2 - simCost #bc 1 is best similarity but minimzing cost
		
		updatedTuple = [phrase,cost]

		#print("phrase: {}, query: {}".format(phrase.strip(), queryWords))

		if infinity or (words == queryWords): updatedTuple[1] = float('inf')
		else: updatedTuple[1] *= similarityCost * numSwaps
		back.solutions[lineNum] = tuple(updatedTuple)
	
	back.pruneSolution()
	print("NEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEW")
	for path in back.solutions:
		print(path)
	print("NEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEW")
	

	# def costFunc(queryTheme, queryWord, swap):
	# 	swapPenality = 1
	# 	if queryWord == swap:
	# 		#de-incentivize a large number of swaps
	# 		if queryWord != swap: swapPenality = 10
	# 	# return math.log(bigramCost(queryWord, swap)**2 * util.wup_similarity(queryTheme, swap)) * swapPenality
	# 	return util.wup_similarity(queryTheme, swap)

	# ucs = util.UniformCostSearch(verbose=1)
	# ucs.solve(PunnificationProblem(queryTheme, queryWords, costFunc, possibleSwaps))

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
