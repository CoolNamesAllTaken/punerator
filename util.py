from nltk.corpus import wordnet as wn
# if the above command doesn't work, run:
#	import nltk
#	nltk.download()

from thesaurus_api.thesaurus import Word # https://github.com/Manwholikespie/thesaurus-api requires requests, beautifulsoup4
import heapq, collections, re, sys, time, os, random # CS221 library imports


def synonyms(word):
	"""
	Returns the set of synonyms of a word.  Uses NLTK.
	"""
	synonyms = []
	syns = wn.synsets(word)
	for synset in syns:
		for lemma in synset.lemmas():
			synonyms.append(lemma.name())
	print("word={} synonyms={}".format(word, synonyms))
	return set(synonyms)

def syn_hyperhypo(word):
	"""
	Returns a set of related, on-theme words by adding the lemmas, hypernyms, and hyponyms
	for each definition of the word.  Uses NLTK.
	"""
	related = set()
	syns = wn.synsets(word)
	for synset in syns:
		print("word={} lemmas={}".format(word, synset.lemmas()))
		print("word={} hypernyms={}".format(word, synset.hypernyms()))
		print("word={} hyponyms={}".format(word, synset.hyponyms()))
		print("word={} member_holonyms={}".format(word, synset.member_holonyms()))
		for lemma in synset.lemmas():
			related.add(lemma.name())
		for hypernym in synset.hypernyms():
			related.add(hypernym.name())
		for hyponym in synset.hyponyms():
			related.add(hyponym.name())
		for holonym in synset.member_holonyms():
			related.add(holonym.name())
	related.add(word)
	return related

def syn_thesaurus(word):
	"""
	Returns a set of synonyms pulled from the Thesaurus.com API
	"""
	related = set()
	for synset in Word(word).synonyms('all'):
		for lemma in synset:
			related.add(lemma)
			# print("word={} related={}".format(word, related))
	related.add(word) # add in the original word
	return related

def wup_similarity(word1, word2):
	word1_synsets = wn.synsets(word1) # TODO: figure out which synset to use
	word2_synsets = wn.synsets(word2)
	# print("word1_synsets={} word2_synsets={}".format(word1_synsets, word2_synsets))
	if not word1_synsets or not word2_synsets: return float('inf') # word has no synonyms
	# print("wup_similarity word1={} word2={}".format(word1, word2))
	similarity = word1_synsets[0].wup_similarity(word2_synsets[0]) # score is wu-palmer similarity between swapped word and theme word
	# print('similarity={}'.format(similarity))
	if similarity == None: return float('inf')
	# print('returning it anyways!')
	return similarity

def synset_names(synset):
	"""
	Returns the names of the lemmas in a synset
	"""
	names = []
	for lemma in synset.lemmas():
		names.append(lemma.name())
	return set(names)

############################################################
# Data structure for supporting uniform cost search. (Stolen from CS221)
class PriorityQueue:
	def  __init__(self):
		self.DONE = -100000
		self.heap = []
		self.priorities = {}  # Map from state to priority

	# Insert |state| into the heap with priority |newPriority| if
	# |state| isn't in the heap or |newPriority| is smaller than the existing
	# priority.
	# Return whether the priority queue was updated.
	def update(self, state, newPriority):
		oldPriority = self.priorities.get(state)
		if oldPriority == None or newPriority < oldPriority:
			self.priorities[state] = newPriority
			heapq.heappush(self.heap, (newPriority, state))
			return True
		return False

	# Returns (state with minimum priority, priority)
	# or (None, None) if the priority queue is empty.
	def removeMin(self):
		while len(self.heap) > 0:
			priority, state = heapq.heappop(self.heap)
			if self.priorities[state] == self.DONE: continue  # Outdated priority, skip
			self.priorities[state] = self.DONE
			return (state, priority)
		return (None, None) # Nothing left...

############################################################
# Abstract interfaces for search problems and search algorithms. (Stolen from CS221)

class SearchProblem:
	# Return the start state.
	def startState(self): raise NotImplementedError("Override me")

	# Return whether |state| is an end state or not.
	def isEnd(self, state): raise NotImplementedError("Override me")

	# Return a list of (action, newState, cost) tuples corresponding to edges
	# coming out of |state|.
	def succAndCost(self, state): raise NotImplementedError("Override me")

class SearchAlgorithm:
	# First, call solve on the desired SearchProblem |problem|.
	# Then it should set two things:
	# - self.actions: list of actions that takes one from the start state to an end
	#                 state; if no action sequence exists, set it to None.
	# - self.totalCost: the sum of the costs along the path or None if no valid
	#                   action sequence exists.
	def solve(self, problem): raise NotImplementedError("Override me")

############################################################
# Uniform cost search algorithm (Dijkstra's algorithm).

class UniformCostSearch(SearchAlgorithm):
	def __init__(self, verbose=0):
		self.verbose = verbose

	def solve(self, problem):
		# If a path exists, set |actions| and |totalCost| accordingly.
		# Otherwise, leave them as None.
		self.actions = None
		self.totalCost = None
		self.numStatesExplored = 0

		# Initialize data structures
		frontier = PriorityQueue()  # Explored states are maintained by the frontier.
		backpointers = {}  # map state to (action, previous state)

		# Add the start state
		startState = problem.startState()
		frontier.update(startState, 0)

		while True:
			# Remove the state from the queue with the lowest pastCost
			# (priority).
			state, pastCost = frontier.removeMin()
			if state == None: break
			self.numStatesExplored += 1
			if self.verbose >= 2:
				print "Exploring %s with pastCost %s" % (state, pastCost)

			# Check if we've reached an end state; if so, extract solution.
			if problem.isEnd(state):
				self.actions = []
				while state != startState:
					action, prevState = backpointers[state]
					self.actions.append(action)
					state = prevState
				self.actions.reverse()
				self.totalCost = pastCost
				if self.verbose >= 1:
					print "numStatesExplored = %d" % self.numStatesExplored
					print "totalCost = %s" % self.totalCost
					print "actions = %s" % self.actions
				return

			# Expand from |state| to new successor states,
			# updating the frontier with each newState.
			for action, newState, cost in problem.succAndCost(state):
				if self.verbose >= 3:
					print "  Action %s => %s with cost %s + %s" % (action, newState, pastCost, cost)
				if frontier.update(newState, pastCost + cost):
					# Found better way to go to |newState|, update backpointer.
					backpointers[newState] = (action, state)
		if self.verbose >= 1:
			print "No path found"

class BacktrackingSearch(SearchAlgorithm):
	def __init__(self, verbose=0):
		self.verbose = verbose
		self.solutions = []

	def pruneSolution(self):
		"""
		Removes all instances of the highest cost present in the solutions set.
		Note: sorts in reverse order and sets the highest cost element to be the first element of solutions.
		"""
		self.solutions.sort(key=lambda x: x[1], reverse=True)
		maximum_cost = self.solutions[0][1]
		self.solutions = [x for x in self.solutions if x[1] != maximum_cost]

	def solve(self, problem): # fullPhrase, possibleSwaps, bigramCost
		# TODO: re-implement
		costCache = collections.defaultdict(float) #{(prevWord, subWord) : bigramCost(prevWord, subWord)}

		self.numIterations = 0

		def backtrack(state, path, totalCost):
			self.numIterations += 1
			if problem.isEnd(state): # found solution
				self.solutions.append((path, totalCost))
			else: # extend path
				for action, newState, actionCost in problem.succAndCost(state):
					newPath = list(path) # copy old path (pass by value)
					newPath.append(action) # extend path
					newTotalCost = totalCost + actionCost
					#STILL BROKEN. MULTIPLYING THEM ALL TOGETHER GOES TO 0
					backtrack(newState, newPath, newTotalCost)
			if self.verbose: print("numIterations={}".format(numIterations))

		backtrack(problem.startState(), [], 0)
		self.solutions.sort(key=lambda x: x[1]) # sort solutions with lowest cost first
		minCostSolution = self.solutions[0]

		# set SearchAlgorithm things
		self.actions = minCostSolution[0]
		self.totalCost = minCostSolution[1]
		self.numStatesExplored = self.numIterations

class BacktrackingSearchProblem():
	def __init__(self):
		self.solutions = []

	def pruneSolution(self):
		"""
		Removes all instances of the highest cost present in the solutions set.
		Note: sorts in reverse order and sets the highest cost element to be the first element of solutions.
		"""
		self.solutions.sort(key=lambda x: x[1], reverse=True)
		maximum_cost = self.solutions[0][1]
		self.solutions = [x for x in self.solutions if x[1] != maximum_cost]

	def solve(self, fullPhrase, possibleSwaps, bigramCost):
		costCache = collections.defaultdict(float) #{(prevWord, subWord) : bigramCost(prevWord, subWord)}
		
		self.phrase = fullPhrase
		self.lenphrase = len(fullPhrase)
		self.substitutions = possibleSwaps
		self.bigramCost = bigramCost

		self.numIterations = 0
		
		def backtrack(totalPath, totalCost, prevWord, index):
			self.numIterations += 1
			if index == self.lenphrase:
				self.solutions.append((totalPath, totalCost))
			else:
				currWord = self.phrase[index]
				for subWord in self.substitutions(currWord):
					newPath = totalPath+" "+subWord
					incrimentalCost = 0
					if (prevWord, subWord) in costCache: 
						incrimentalCost = costCache[(prevWord, subWord)]
					else:
						incrimentalCost = self.bigramCost(prevWord, subWord)
						costCache[(prevWord, subWord)] = incrimentalCost
					#print("prevWord: {}, curWord: {}, cost: {}".format(prevWord, subWord, incrimentalCost))
					
					#still working on pruning during iteration
					# if incrimentalCost >= BIGRAM_MAX: #index != 0 and 
					# 	return
					newCost = totalCost+incrimentalCost
					backtrack(newPath, newCost, currWord, index+1)

		backtrack("", 0, '-BEGIN-', 0)

		print("NUM RECURSIVE ITERATIONS: {}".format(self.numIterations))

		#self.pruneSolution()