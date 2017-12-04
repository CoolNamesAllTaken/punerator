import gensim
from gensim import corpora

# set up logging
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

### Dependencies
	# gensim must be installed (pip install --upgrade gensim) https://radimrehurek.com/gensim/install.html
	# Cython must be installed (pip install cython) for trainModel to parallelize (run fast)
	# Pickle must be installed for trainModel to save models

### Usage
	# model.similarity('word1', 'word2')

### Code adapted from https://rare-technologies.com/word2vec-tutorial/

class SentencesIterable(object):
	"""
	Iterable class that iterates through the lines in a file to reduce memory pressure when learning a corpus
	with word2vec.  Extends object.
	"""
	def __init__(self, path):
		self.path = path
 
	def __iter__(self):
		for line in open(self.path): # read file line by line
			yield line.split() # iterable = list of words in each sentence

def trainModel(path, savePath=None):
	"""
	Learns a word2vec model from a corpus, indicated by a path.
	Good training data links: https://code.google.com/archive/p/word2vec/
	Inputs:
		path -	path to the corpus txt file, which stores sentences (1 per line) for the model to train on
	Returns:
		model -	word2vec model
	"""
	sentences = SentencesIterable(path)
	model = gensim.models.Word2Vec(sentences, workers=4) # learn model with 4 processes (parallel - REQUIRES CYTHON)
	if savePath:
		model.save(savePath) # save model if save directory specified
	return model

def loadModel(path):
	"""
	Loads a gensim format model.
	Inputs:
		path -	path to the model
	Returns:
		model -	model that was loaded
	"""
	model = gensim.models.KeyedVectors.load(path)
	return model

def loadWord2VecModel(path):
	"""
	Load a pre-trained model in Google's C word2vec format from a binary file.
	Inputs:
		path -	path to the pre-trained model binary (e.g. the pre-trained Google News model
				'./models/GoogleNews-vectors-negative300.bin')
	Returns:
		model -	word2vec format model
	"""
	model = gensim.models.KeyedVectors.load_word2vec_format(path, binary=True)
	return model

# if __name__ == '__main__':
# 	print(list(SentencesIterable('corpora/test.txt')))
# 	print('Loading model...')
# 	model = loadWord2VecModel('./models/GoogleNews-vectors-negative300.bin')
# 	print('Model Loaded')
	