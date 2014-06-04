import threading

class SegmentedMemory:
	
	def __init__(self):
		self.metaData = {}
		self.exact = {}
		self.sameArgs = {}
		self.samePreds = {}
		self.individualPred = {}
		self.individualArg = {}
		self.lock = threading.Lock()
	
	def addFact(self, fact, metaData):
		'''
		Adds a fact and its metadata to memory. Note that the lock is acquired at the beginning of this process and released at the end, so that a fact is either completely added to memory or not added at all.
		'''
		self.lock.acquire()
		self.metaData[fact] = metaData
		self._add(fact.simpleHash(), self.exact, fact)
		self._add(fact.sameArgsHash(), self.sameArgs, fact)
		self._add(fact.samePredsHash(), self.samePreds, fact)
		for pred in fact.predicates():
			self._add(hash(pred), self.individualPred, fact)
		for arg in fact.arguments():
			self._add(hash(arg), self.individualArg, fact)
		self.lock.release()
	
	def _add(self, hashVal, dict, fact):
		'''
		adds fact to the set pointed to by key hashVal in dict. If hashVal is not in dict, creates a new set and adds fact.
		'''
		if hashVal not in dict:
			dict[hashVal] = set()
		dict[hashVal].add(fact)
	
	def _retrieve(self, hashVal, dict):
		'''
		retrieves the set of facts pointed to by hashVal in dict. A thread must hold the lock access any memory dict.
		'''
		self.lock.acquire()
		if hashVal in dict:
			return dict[hashVal]
		else:
			return set()
		self.lock.release()
	
	def retrieveExact(self, fact):
		'''
		Retrieves all facts with the same configuration of predicates and arguments. Note that other facts may also be returned if hash values collide.
		'''
		return _retrieve(fact.simpleHash(), self.exact)
	
	def retrieveAllArgs(self, fact):
		return _retrieve(fact.sameArgsHash(), self.sameArgs)
	
	def retrieveAllPreds(self, fact):
		return _retrieve(fact.samePredsHash(), self.samePreds)
	
	#returns any fact s.t. some argument matches an argument in the input fact. Note that facts may be added while this method is running, and they might be retrieved or not.
	def retrieveAnyArg(self, fact):
		all = set()
		for arg in fact.arguments():
			all = all.union(_retrieve(hash(arg), self.individualArg))
		return all
	
	#returns any fact s.t. some predicate matches a predicate in the input fact. Note that facts may be added while this method is running, and they might be retrieved or not.
	def retrieveAnyPred(self, fact):
		all = set()
		for pred in fact.predicates():
			all = all.union(_retrieve(hash(pred), self.individualPred))
		return all
		