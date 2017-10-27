import argparse
import sys

import punerator

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

        print ''

        if cmd == 'help':
            print('Usage: <command> [arg1, arg2, ...]')
            print('')
            print('Commands:')
            print('\n'.join(a + '\t\t' + b for a, b in [
                ('punnify', 'Punnifies a given string'),
                ('cmd2', 'Description'),
            ]))
            print('')
            print('Enter empty line to quit')
        elif cmd == 'punnify':
            print('TIME TO PUNNIFY')
            print(line)
            punerator.punnify(line)
        else:
            print 'Unrecognized command:', cmd

        print ''

def main():
    args = parseArgs()
    repl(command=args.command)

