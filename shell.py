import argparse
import sys

import punerator
import wordCostUtil as wc
import gensimUtil as gs

# corpus for training bigram and unigram cost functions (used to re-train unigram, bigram cost)
CORPUS_PATH = "corpora/EnglishText.txt"

# load pre-trained unigram and bigram cost functions (used for sentence fluency)
print('Loading Bigram Cost model...')
UNIGRAM_PATH = 'models/uni'
BIGRAM_PATH = 'models/bi'
_, BIGRAM_COST = wc.loadCosts(UNIGRAM_PATH, BIGRAM_PATH) # (UNIGRAM_PATH, BIGRAM_PATH)

# load pre-trained word vector model in Google word2vec binary format (used for word similarity)
print('Loading word2vec model...')
WORD2VEC_MODEL = gs.loadWord2VecModel('./models/GoogleNews-vectors-negative300.bin') # (WORD2VEC_MODEL_PATH)

def parseArgs():
	p = argparse.ArgumentParser()
	p.add_argument('--command', help='Always use this model')
	return p.parse_args()

def parse_pun_cmd(cmd, line):
	"""
	Parses a pun command with a line in the form <theme> <sentence>
	Inputs:
		cmd - punnification command
		line - line to punnify, in the form <theme> <sentence>
	Outputs:
		theme -	theme word
		sentence - sentence to punnify
	"""
	if (len(line) < 2):
		print('Not enough inputs: Expected input of the form \'{} <theme> <sentence>\''.format(cmd))
		return None, None
	theme_and_sentence = line.split(None, 1)
	theme, sentence = theme_and_sentence[0], ' '.join(theme_and_sentence[1:])
	print('AI Punnify!  Theme: {} Sentence: {}'.format(theme, sentence))
	return theme, sentence

def repl(command=None):
	'''REPL: read, evaluate, print, loop'''

	while True:
		sys.stdout.write('>> ')
		line = sys.stdin.readline().strip()
		if not line:
			break

		if command is None:
			cmdAndLine = line.split(None, 1)
			cmd, line = cmdAndLine[0], ' '.join(cmdAndLine[1:])
		else:
			cmd = command
			line = line

		print('')

		if cmd == 'help':
			print('Usage: <command> [arg1, arg2, ...]')
			print('')
			print('Commands:')
			print('\n'.join(a + '\t' + b for a, b in [
				('subs\t', 'List synonyms for each word in string'),
				('sim\t', 'Calculate similarity between two words'),
				('pun_bs\t', 'Punnifies a string using the baseline algorithm, wordnet synonyms and wup similarity'),
				('pun_tb\t', 'Punnifies a string using Thesaurus API, BigramCost, and Word2Vec similarity'),
				('pun_t2\t', 'Punnifies a string using Thesaurus API and Word2Vec similarity'),
				('pun_ai\t', 'Punnifies a string using a sooper dooper fancy AI algorithm (AI baseline)'),
				('pun_meaning', 'Creates meaning puns (uses synonyms, hypernyms, hyponyms)'),
				('pun_sound', 'Creates sound puns (uses homophones)'),
				('train\t', 'Trains unigram/bigram costs on the text corpus'),
			]))
			print('')
			print('Enter empty line to quit')
		elif cmd == 'subs':
			print('Finding substitutions for {}'.format(line))
			punerator.substitutions(line)
		elif cmd == 'sim':
			words = line.split(None, 1)
			print('Finding similarity between {} and {}'.format(words[0], words[1]))
			punerator.similarity(words[0], words[1], WORD2VEC_MODEL)
		elif cmd == 'bgc':
			words = line.split(None, 1)
			print("Finding bigram cost for '{} {}'".format(words[0], words[1]))
			print(BIGRAM_COST(words[0], words[1]))
		
		elif cmd == 'pun_bs':
			theme, sentence = parse_pun_cmd(cmd, line)
			if not theme and not sentence: continue
			punerator.punnify_baseline(theme, sentence)
		elif cmd == 'pun_tb':
			theme, sentence = parse_pun_cmd(cmd, line)
			if not theme and not sentence: continue
			punerator.punnify_ai(theme, sentence, BIGRAM_COST, WORD2VEC_MODEL, True) 
		elif cmd == 'pun_t2':
			theme, sentence = parse_pun_cmd(cmd, line)
			if not theme and not sentence: continue
			punerator.punnify_ai(theme, sentence, BIGRAM_COST, WORD2VEC_MODEL, False)
		
		elif cmd == 'pun_ai':
			theme, sentence = parse_pun_cmd(cmd, line)
			if not theme and not sentence: continue # not enough inputs
			punerator.punnify_ai(theme, sentence, BIGRAM_COST, WORD2VEC_MODEL)
		elif cmd == 'pun_meaning':
			theme, sentence = parse_pun_cmd(cmd, line)
			if not theme and not sentence: continue # not enough inputs
			punerator.punnify_meaning(theme, sentence, BIGRAM_COST, WORD2VEC_MODEL)
		elif cmd == 'pun_sound':
			theme, sentence = parse_pun_cmd(cmd, line)
			if not theme and not sentence: continue # not enough inputs
			punerator.punnify_meaning(theme, sentence, BIGRAM_COST, WORD2VEC_MODEL)
		elif cmd == 'train':
			print('Training bigram/unigram cost functions on corpus...')
			wc.createCosts(CORPUS_PATH, UNIGRAM_PATH, BIGRAM_PATH)
			print('Done!')
		else:
			print('Unrecognized command:', cmd)

def main():
	args = parseArgs()

	repl(command=args.command)

