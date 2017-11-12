from nltk.corpus import wordnet as wn
# if the above command doesn't work, run:
#	import nltk
#	nltk.download()

def synonyms(word):
	"""
	"""
	synonyms = []
	syns = wn.synsets(word)
	for synset in syns:
		for lemma in synset.lemmas():
			synonyms.append(lemma.name())
	return set(synonyms)

def synset_names(synset):
	names = []
	for lemma in synset.lemmas():
		names.append(lemma.name())
	return set(names)