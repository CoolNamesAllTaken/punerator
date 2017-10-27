from PyDictionary import PyDictionary
dictionary=PyDictionary()

import shell
import collections

def punnify(sentence):
	words = sentence.split()
	print(words)
	for word in words:
		print("word={}, substitutions={}".format(word, dictionary.synonym(word)))

if __name__ == '__main__':
	shell.main()