import argparse
import sys

import punerator
import wordCostUtil as wc

CORPUS_PATH = "EnglishText.txt" # corpus for training bigram and unigram cost functions
_, BIGRAM_COST = wc.fetchCosts()

def parseArgs():
	p = argparse.ArgumentParser()
	p.add_argument('--command', help='Always use this model')
	return p.parse_args()

def parse_pun_cmd(cmd, line):
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
				('pun_bs\t', 'Punnifies a string using the baseline algorithm'),
				('pun_ai\t', 'Punnifies a string using a sooper dooper fancy AI algorithm (AI baseline)'),
				('pun_meaning', 'Creates meaning puns (uses synonyms, hypernyms, hyponyms)'),
				('pun_sound', 'Creates sound puns (uses homophones)'),
				('train\t', 'Trains unigram/bigram costs on the text corpus'),
			]))
			print('')
			print('Enter empty line to quit')
		elif cmd == 'subs':
			print('Finding substitutions for {}'.format(line))
			punerator.subs(line)
		elif cmd == 'pun_bs':
			theme, sentence = parse_pun_cmd(cmd, line)
			if not theme and not sentence: continue # not enough inputs
			punerator.punnify_baseline(theme, sentence)
		elif cmd == 'pun_ai':
			theme, sentence = parse_pun_cmd(cmd, line)
			if not theme and not sentence: continue # not enough inputs
			punerator.punnify_ai(theme, sentence, BIGRAM_COST)
		elif cmd == 'pun_meaning':
			theme, sentence = parse_pun_cmd(cmd, line)
			if not theme and not sentence: continue # not enough inputs
			punerator.punnify_meaning(theme, sentence, BIGRAM_COST)
		elif cmd == 'pun_sound':
			theme, sentence = parse_pun_cmd(cmd, line)
			if not theme and not sentence: continue # not enough inputs
			punerator.punnify_meaning(theme, sentence, BIGRAM_COST)
		elif cmd == 'train':
			print('Training bigram/unigram cost functions on corpus...')
			wc.createCosts(CORPUS_PATH)
			print('Done!')
		else:
			print('Unrecognized command:', cmd)

def main():
	args = parseArgs()

	# print("Fetching Bigram Cost...")
	# _, BIGRAM_COST = wc.fetchCosts()
	# print("bigramCost={}".format(BIGRAM_COST))
	# print("Done!")

	repl(command=args.command)

