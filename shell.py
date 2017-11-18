import argparse
import sys

import punerator
import wordCostUtil as wc

def parseArgs():
    p = argparse.ArgumentParser()
    p.add_argument('--command', help='Always use this model')
    return p.parse_args()

def repl(command=None):
    '''REPL: read, evaluate, print, loop'''

    while True:
        sys.stdout.write(">> ")
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
            print('\n'.join(a + '\t\t' + b for a, b in [
                ('subs', 'List synonyms for each word in string'),
                ('pun_bs', 'Punnifies a string using the baseline algorithm'),
                ('pun_ai', 'Punnifies a string using a sooper dooper fancy AI algorithm'),
                ('cmd2', 'Description'),
            ]))
            print('')
            print('Enter empty line to quit')
        elif cmd == 'subs':
            print('Finding substitutions for {}'.format(line))
            punerator.subs(line)
        elif cmd == 'pun_bs':
            if (len(line) < 2):
                'Not enough inputs: Expected input of the form \'pun_base <theme> <sentence>\''
            theme_and_sentence = line.split(None, 1)
            theme, sentence = theme_and_sentence[0], ' '.join(theme_and_sentence[1:])
            print('Baseline Punnify!  Theme: {} Sentence: {}'.format(theme, sentence))
            punerator.punnify_baseline(theme, sentence)
        elif cmd == 'pun_ai':
            if (len(line) < 2):
                'Not enough inputs: Expected input of the form \'pun <theme> <sentence>\''
            theme_and_sentence = line.split(None, 1)
            theme, sentence = theme_and_sentence[0], ' '.join(theme_and_sentence[1:])
            print('AI Punnify!  Theme: {} Sentence: {}'.format(theme, sentence))
            punerator.punnify_ai(theme, sentence)
        elif cmd == 'train':
            print('Training bigram/unigram cost functions on corpus...')
            wc.calculateCosts()
            print('Done!')
        else:
            print('Unrecognized command:', cmd)

def main():
    args = parseArgs()
    repl(command=args.command)

