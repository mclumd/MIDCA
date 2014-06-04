import threading


class TruthValue:
	
	def __init__(self, value):
		self.value = value
	
	def known_true(self):
		return self.value == 1
	
	def known_false(self):
		return self.value == 0
	
	def unknown(self):
		return self.value == -1

TRUE = TruthValue(1)
FALSE = TruthValue(0)
UNKNOWN = TruthValue(-1)

class IllegalAssignException(Exception):
	
	pass

class Predicate:
	
	def truth(self, fact, facts, complete = True):
		if hasattr(self, truthFunc):
			specialTruth = self.truthFunc(fact, facts)
			if specialTruth[0] != UNKNOWN:
				return specialTruth
		confirmations = set()
		negConfirmations = set()
		negation = fact.negation()
		for knownFact in facts:
			if fact == knownFact:
				confirmations.add(fact)
				if not complete:
					return (TRUE, confirmations)
			elif negation == knownFact:
				negConfirmations.add(fact)
				if not complete:
					return (FALSE, negConfirmations)
		if confirmations and not negConfirmations:
			return (TRUE, confirmations)
		elif negConfirmations and not confirmations:
			return (FALSE, negConfirmations)
		else:
			return (UNKNOWN, confirmations.union(negConfirmations))
	
	def __str__(self):
		if self in names:
			return names[self]
		return "UNNAMED_P"


class Variable:

	def predicates(self):
		return set()
	
	def arguments():
		return {self}

	def __str__(self):
		if self in names:
			return names[self]
		return "UNNAMED_V"

class Type:
	
	def predicates(self):
		return set()
	
	def arguments():
		return {self}
	
	def __str__(self):
		if self in names:
			return names[self]
		return "UNNAMED_T"
	
class Instance:

	def predicates(self):
		return set()
	
	def arguments():
		return {self}
	
	def __str__(self):
		if self in names:
			return names[self]
		return "UNNAMED_I"

class SpecialPredicate(Predicate):
		
		def __init__(self, truthFunc):
			self.truthFunc = truthFunc

class Process(Instance):
	
	def __init__(self, process):
		self.process = process
	
	def start(self, args):
		self.process(args)
			

'''
special predicates
'''
def isPredicate(fact, facts):
	(return len(fact.args) == 1 and isinstance(fact.args[0], Predicate), set())

PREDICATE = SpecialPredicate(isPredicate)

def isProcess(fact, facts):
	(return len(fact.args) == 1 and isinstance(fact.args[0], Process), set())

PROCESS = SpecialPredicate(isProcess)

#after debugging, this should catch exceptions relating to number of args and somehow convert them into knowledge of a failure (e.g. return false + reason).
def startProcess(fact, facts):
	fact.args[0].start(fact.args[1:])
	return (TRUE, set())

START = SpecialPredicate(startProcess)

#IN_SEQUENCE
#EXCEPT //possibly an expr type
#WITH_CAVEAT

#math
#numeric is an subclass of instance.
IS_NUMERIC = SpecialPredicate(...)

def atLeast(self, fact, facts):
	
AT_LEAST = SpecialPredicate(None)

#time
def getCurrentTime(fact, facts):
	return 0
	
NOW = SpecialPredicate(getCurrentTime)



'''
convenience predicates
'''
CONTAINS_ARG = Predicate()



class Expr:

	def assign(self, var, val):
		'''
		replaces all occurences of var with val. Val may be a variable, type, instance, expression, etc.
		'''
		raise Exception("Assign not implemented!")
	
	def copy(self):
		return self.assign(None, None)
	
	def truth(self, KB):
		return UNKNOWN
	
	#returns list of conjuncts, each of which is a list of disjuncts
	def CNF(self):
		return []
	
	def negation(self):
		return Negation(self)
		
	def predicates(self):
		return set()
	
	def arguments():
		return set()
	
	def simpleHash(self):
		return hash(0)
	
	def sameArgsHash(self):
		return hash(0)
	
	def samePredsHash(self):
		return hash(0)
	

class Negation:
	
	def __init__(self, expr):
		self.unboundVariables = set(expr.unboundVariables)
		self.expr = expr
	
	def assign(self, var, val):
		return Negation(self.expr.assign(var, val))
	
	def CNF(self):
		raise Exception("not implemented")
	
	def matches(self, other):
		return type(self) == type(other) and self.expr.matches(other.expr)
	
	def __str__(self):
		return "~" + str(self.expr)
	
	def negation(self):
		return self.expr.copy()
	
	def predicates(self):
		return self.expr.predicates()
	
	def arguments():
		return self.expr.arguments()
	
	def simpleHash(self):
		return hash((self.expr.simpleHash(), False))
	
	def sameArgsHash(self):
		return hash((self.expr1.sameArgsHash(), self.expr2.sameArgsHash()))
	
	def samePredsHash(self):
		return hash((self.expr1.samePredsHash(), self.expr2.samePredsHash()))

class AndExpr(Expr):
	
	def __init__(self, expr1, expr2):
		self.unboundVariables = expr1.unboundVariables.union(expr2.unboundVariables)
		self.expr1 = expr1
		self.expr2 = expr2	
	
	def assign(self, var, val):
		newExpr1 = self.expr1.assign(var, val)
		newExpr2 = self.expr2.assign(var, val)
		newVars = newExpr1.unboundVariables.union(newExpr2.unboundVariables)
		return AndExpr(newExpr1, newExpr2, newVars)
	
	#returns list of conjuncts, each of which is a list of disjuncts, each of which is a PredicateExpr
	def CNF(self):
		return self.expr1.CNF() + self.expr2.CNF()
	
	def matches(self, other):
		return type(self) == type(other) and ((self.expr1.matches(other.expr1) and self.expr2.matches(other.expr2)) or (self.expr1.matches(other.expr2) and self.expr2.matches(other.expr1)))
	
	def __str__(self):
		return "(" + str(self.expr1) + " ^ " + str(self.expr2) + ")"
	
	def predicates(self):
		return self.expr1.predicates().union(self.expr2.predicates())
	
	def arguments():
		return self.expr1.arguments().union(self.expr2.arguments())
	
	def simpleHash(self):
		return hash((self.expr1.simpleHash(), self.expr2.simpleHash()))
	
	def sameArgsHash(self):
		return hash((self.expr1.sameArgsHash(), self.expr2.sameArgsHash()))
	
	def samePredsHash(self):
		return hash((self.expr1.samePredsHash(), self.expr2.samePredsHash()))
	
	'''
	def truth(self, KB):
		truth1 = self.expr1.truth(KB)
		if truth1 != TRUE:
			return truth1
		return self.expr2.truth(KB)
	'''
	
class OrExpr(Expr):
	
	def __init__(self, expr1, expr2):
		self.unboundVariables = expr1.unboundVariables.union(expr2.unboundVariables)
		self.expr1 = expr1
		self.expr2 = expr2	
	
	def assign(self, var, val):
		newExpr1 = self.expr1.assign(var, val)
		newExpr2 = self.expr2.assign(var, val)
		newVars = newExpr1.unboundVariables.union(newExpr2.unboundVariables)
		return OrExpr(newExpr1, newExpr2, newVars)
	
	#returns list of conjuncts, each of which is a list of disjuncts, each of which is a PredicateExpr
	def CNF(self):
		cnf1 = self.expr1.CNF()
		cnf2 = self.expr2.CNF()
		cnf = []
		for conjunct1 in cnf1:
			for conjunct2 in cnf2:
				cnf.append(conjunct1 + conjunct2)
		return cnf	
	
	def matches(self, other):
		return type(self) == type(other) and ((self.expr1.matches(other.expr1) and self.expr2.matches(other.expr2)) or (self.expr1.matches(other.expr2) and self.expr2.matches(other.expr1)))
	
	def __str__(self):
		return "(" + str(self.expr1) + " v " + str(self.expr2) + ")"
	
	def predicates(self):
		return self.expr1.predicates().union(self.expr2.predicates())
	
	def arguments():
		return self.expr1.arguments().union(self.expr2.arguments())
	
	def simpleHash(self):
		return hash((self.expr1.simpleHash(), self.expr2.simpleHash()))
	
	def sameArgsHash(self):
		return hash((self.expr1.sameArgsHash(), self.expr2.sameArgsHash()))
	
	def samePredsHash(self):
		return hash((self.expr1.samePredsHash(), self.expr2.samePredsHash()))
	
	
class PredicateExpr:

	def __init__(self, predicate, args):
		self.predicate = predicate
		self.args = args
		self.unboundVariables = {arg for arg in args if isinstance(arg, Variable)}
	
	def assign(self, var, val):
		'''
		replaces all occurences of var with val. Val may be a variable, type, instance, expression, etc.
		'''
		newArgs = [arg if arg != var else val for arg in self.args]
		return PredicateExpr(self.predicate, newArgs)
	
	def truth(self, facts):
		try:
			self.predicate.truth(self.args, facts)
		except NotImplementedError: 
			if KB.contains_fact(self):
				return TRUE
			elif KB.contains_fact(self.negation()):
				return FALSE
			else:
				return UNKNOWN
	
	def CNF(self):
		return [[self]]
	
	def matches(self, other):
		return self.predicate == other.predicate and self.args == other.args
	
	def __str__(self):
		s = str(self.predicate) + "("
		for arg in self.args:
			s += str(arg) + ", "
		if self.args:
			s = s[:-2]
		return s + ")"
	
	def predicates(self):
		return {self.predicate}
	
	def arguments():
		return {arg for arg in self.args}
	
	def simpleHash(self):
		return hash((self.predicate, tuple(self.args)))
	
	def sameArgsHash(self):
		return hash(tuple(self.args))
	
	def samePredsHash(self):
		return hash(self.predicate)

def CNFstr(cnf):
	s = ""
	for conjunct in cnf:
		s += "("
		for pred in conjunct:
			s += str(pred) + " v "
		if conjunct:
			s = s[:-3]
		s += ") ^ "
	if cnf:
		s = s[:-3]
	return s

person = Type()
doug = Instance()
dog = Instance()
cat = Instance()
has = Predicate()
eats = Predicate()

names = {doug: "doug", dog: "dog", cat: "cat", has: "has", eats: "eats"}

expr = OrExpr(AndExpr(PredicateExpr(has, [doug, dog]), PredicateExpr(has, [doug, cat])), OrExpr(PredicateExpr(has, [doug, dog]), PredicateExpr(eats, [dog, cat])))

print expr
print CNFstr(expr.CNF())

print hash(expr), expr.simpleHash(), expr.sameArgsHash(), expr.samePredsHash()

def evalExpr(expr, facts):
	if expr in facts:
		return TRUE
	elif negation(expr) in facts:
		return FALSE

'''
class Fact:
	
	def __init__(self, expr, knowledgeSource, time):
		self.expr = expr
		self.knowledgeSource = knowledgeSource
		self.time = time
	
	def CNF(self):
		return self.expr.CNF()
	
	def matchesExpr(self, expr):
		return self.expr.matches(fact)
	
	def __hash__(self):
		return hash(self.expr)
'''

class Prover:
	
	def __init__(self):
		self.addedFacts = []
	
	def prove(self, queryExpr, facts):
		'''
		basic implementation that checks for an occurence of queryExpr in facts.
		'''
		negation = queryExpr.negation()
		for fact in facts:
			if fact.matchesExpr(queryExpr):
				return (TRUE, fact)
			elif fact.matchesExpr(negation):
				return FALSE, fact			
		return (UNKNOWN, None)

class SimpleMPProver(Prover):
	
	'''
	MP based on P v ~Q formulation
	
	
	def prove(self, queryExpr, facts):
		negation = queryExpr.negation()
		conds = {fact in facts if type(fact) == OrExpr}
		preds = {fact in facts if type(fact) == PredExpr}
		for pred in preds:
			for cond in conds:
				if cond.expr1.matches(
	'''
	
class Query:
	
	def __init__(self, KB, fact, factProver):
		self.KB = KB
		self.fact = fact
		self.unprovenConjuncts = fact.CNF()
		self.provenConjuncts = []
		self.newFacts = []
		self.lock = threading.Lock()
		self.prover = factProver
	
	def getRelevantKnowledge(self, fact):
		'''
		implementation that returns facts that share any predicate or
		argument with the fact being searched for.
		'''
		return self.KB.retrieveAnyArg(fact).union(self.KB.retrieveAnyPred(fact))	
	
	def addNewFact(self, fact):
		with self.lock:
			self.newFacts.append(fact)
	
	def proveConjunct(self, conjunct):
		'''
		
		'''
		currentTruth = FALSE
		for predicateExpr in conjunct:
			with self.KB.lock:
				relevantFacts = self.getRelevantKnowledge(predicateExpr)
			truth, source = self.prover.prove(predicateExpr, relevantFacts)
			self.newFacts += self.prover.addedFacts
			self.prover.addedFacts = []
			if truth == TRUE:
				return TRUE
			elif truth == UNKNOWN:
				currentTruth = UNKNOWN
		return currentTruth
	
	def proveFact(self):
		attempted = []
		
def cleanCNF(cnf):
	newCNF = []
	conjunctsSeen = set()
	for conjunct in cnf:
		tupleForm = tuple(conjunct)
		if hash(tupleForm) in conjunctsSeen:
			continue
		newCNF.append([])
		conjunctsSeen.add(hash(tupleForm))
		disjunctsSeen = set()
		for disjunct in conjunct:
			if hash(disjunct) in disjunctsSeen:
				continue
			disjunctsSeen.add(hash(disjunct))
			newCNF[-1].append(disjunct)
	return newCNF

print CNFstr(cleanCNF(expr.CNF()))	
