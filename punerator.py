from vocabulary.vocabulary import Vocabulary as vb
import json

import shell
import collections

def subs(sentence):
	words = sentence.split()
	print(words)
	for word in words:
		synonym_json = vb.synonym(word)
		# print(synonym_json)
		if not synonym_json:
			print("unrecognized word {}".format(word))
			continue
		synonyms = json.loads(synonym_json) # vocabulary returns JSON object
		substitutions = []
		for synonym in synonyms:
			substitutions.append(synonym[u'text']) # JSON object keys are unicode strings
		substitutions = [str(s) for s in substitutions] # fails if chars outside of ascii range
		print("word={}, substitutions={}".format(word, substitutions))

if __name__ == '__main__':
	shell.main()