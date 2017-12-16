Punerator - CS 221 Fall 2017

John McNelly, Davy Ragland, Anna Verwillow

## Overview
Punerator is a program that enables the user to generate synonym puns of an input phrase or sentence based on a theme word.  This program makes use of a number of Python libraries and pre-trained models, including Wordnet NLTK, Google word2vec (via Gensim), and a Thesaurus.com API written by github user [Manwholikespie](https://github.com/Manwholikespie); please see the sections below for instructions on importing model data and setting up dependencies.

## Usage
Once dependencies are satisfied, Punerator is can be launched by navigating to the punerator/ directory and typing `python punerator.py` into the Terminal window.  This should launch the Punerator shell.  Shell commands and their functionality are listed below.  Note that multi-word phrases are input as space-separated words with no punctuation.

### Primary Functionality
`pun_tb <theme> <phrase>` Creates a punnified phrase on the given theme utilizing Thesaurus.com synonyms, word2vec word similarity (for pun desirability) and bigram cost (for sentence fluency)

Example usage:
```
>> pun_tb fruit he is a jokester
AI Punnify!  Theme: fruit Sentence: he is a jokester
TOTAL ITERATIONS: 207
num solutions: 23
he is a banana
he is a gagster
he is a card
he is a funster
he is a comic
```

`pun_t2 <theme> <phrase>` Creates a punnified phrase on the given theme utilizing Thesaurus.com synonyms and word2vec word similarity but no fluency metric
`pun_bs <theme> <phrase>` Creates a punnified phrase using the baseline NLTK functionality that was implemented first (substitutes using NLTK wordnet synonyms and evaluates similarity with NLTK Wu-Palmer similarity)

`train` Retrains the bigram and unigram models on the english corpus specified by CORPUS_PATH in shell.py
`help` Lists all shell commands with instructions

### Debugging Functions
`subs <words>` Lists substitutions (synonyms) for each word in words
`sim <word1> <word2>` Prints word2vec word similarity for two words

## corpora/
Add EnglishText.txt to the corpora folder for bigram retraining.  Not required for running the program if bigram cost has already been trained (bigram and unigram cost functions are saved in models/).  Corpora can be downloaded [here](https://drive.google.com/drive/folders/1-M4lIEzhLOQlofToD6S7KpCwlVTBR7xu?usp=sharing)

## models/
Add the GoogleNews pre-trained word2vec binary to the models/ folder.  The file can be found [here](https://drive.google.com/file/d/0B7XkCwpI5KDYNlNUTTlSS21pQmM/edit?usp=sharing).  Make sure to uncompress the file before adding it to the folder (extension should be .bin, not .bin.gz).  Alternatively, if you do not want to train the bigram and unigram cost models, download the files from [this link](https://drive.google.com/drive/folders/1OwQlf4jGrl4hz_o0JclpfT3Mlp0BJLWX?usp=sharing) and move them into the models/ folder. 

## Dependencies
`pip install --upgrade gensim` (used as a word2vec interface)
`pip install cython` (used to parallelize word2vec learning)
`pip install dill` (used to store learned models)
`pip install beautifulsoup4` (used by Thesaurus API for web scraping)
`pip install nltk` (used for wordnet, corpus)
From python terminal, run:
	`import nltk`
	`nltk.download()`
	NLTK may throw an error on the first run, follow the terminal instructions for arguments in nltk.download to resolve.
`pip install scipy` (used by gensim)
`pip install numpy` (used by gensim)
may require `pip_install smart_open` on Windows