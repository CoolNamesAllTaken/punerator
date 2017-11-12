from nltk.corpus import wordnet as wn
# if the above command doesn't work, run:
#	import nltk
#	nltk.download()

import shell
import util
import collections
import copy

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

def pun(theme, sentence):
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
		return word_synset.wup_similarity(theme_synset)
	swaps.sort(key=lambda swap: compare_words(swap[0], theme_synset), reverse=True)
	print("sorted swaps={}".format(swaps))


	best_swaps = swaps[1:5]
	for curr_swap in best_swaps:
		words_copy = copy.deepcopy(words)
		words_copy[curr_swap[1]] = curr_swap[0]
		print(' '.join(words_copy))

	

if __name__ == '__main__':
	shell.main()