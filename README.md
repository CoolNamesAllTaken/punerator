## corpora/
Add EnglishText.txt to the corpora folder for bigram retraining.  Not required for running the program if bigram cost has already been trained (bigram and unigram cost functions are saved in models/)

## models/
Add the GoogleNews pre-trained word2vec binary to the models/ folder.  The file can be found here: https://drive.google.com/file/d/0B7XkCwpI5KDYNlNUTTlSS21pQmM/edit?usp=sharing  Make sure to uncompress the file before adding it to the folder (extension should be .bin, not .bin.gz)

## Dependencies
`pip install --upgrade gensim` (used as a word2vec interface)
`pip install cython` (used to parallelize word2vec learning)
`pip install dill` (used to store learned models)
`pip install beautifulsoup4` (used by Thesaurus API for web scraping)
`pip install nltk` (used for wordnet, corpus)
From python terminal, run:
	`import nltk`
	`nltk.download()`
`pip install scipy` (used by gensim)
`pip install numpy` (used by gensim)
may require `pip_install smart_open` on Windows