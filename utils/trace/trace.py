
class Predicate:
	
	def __init__(self, name):
		self.name = name
	
	def __str__(self):
		return str(self.name)

class Instance:
	
	def __init__(self, name):
		self.name = name
	
	def __str__(self):
		return str(self.name)

class Variable:
	
	def __init__(self, name):
		self.name = name
	
	def __str__(self):
		return str(self.name)

class Atom:

	def __init__(self, predicate, args):
		self.predicate = predicate
		self.args = args
	
	def __str__(self):
		s = str(predicate) + "("
		for arg in args:
			s += str(arg) + ", "
		if args:
			s = s[:-2]
		return s + ")"

class Process:
	
	def __init__(self, id, super, type, algorithm, inputs, goals, sideEffects):
		self.id = id
		self.super = super
		self.type = type
		self.algorithm = algorithm
		self.inputs = inputs
		self.goals = goals
		self.sideEffects = sideEffects
	
	def __str__(self):
		s = "Process " + str(self.id) 
		if self.type:
			s += " of type " + str(self.type) 
		if self.algorithm:
			s += " using algorithm " + str(self.algorithm)
		s += "."
		if self.inputs:
			s += " Inputs: ["
			for input in self.inputs:
				s += str(input) + ", "
			s = s[:-2] + "]"
		if self.goals:
			s += " Goals: ["
			for goal in self.goals:
				s += str(goal) + ", "
			s = s[:-2] + "]"
		if self.sideEffects:
			s += " Expected Side Effects: ["
			for sideEffect in self.sideEffects:
				s += str(sideEffect) + ", "
			s = s[:-2] + "]"
		return s

class Observation:
	
	def __init__(self, fact, source):
		self.fact = fact
		self.source = source
	
	def __str__(self):
		s = ""
		if self.source:
			try:
				s += str(self.source.id)
			except Exception:
				s += str(self.source)
			s += " observed "
		s += str(self.fact)
		return s
	
class Event:
	
	START = 0
	END = 1
	OBSERVE = 2
	
	def __init__(self, type, val):
		self.type = type
		self.val = val
	
	def __str__(self):
		if self.type == self.START:
			return str(self.val.super) + " Starting: " + str(self.val) + "\n"
		elif self.type == self.END:
			return "Ending: " + str(self.val) + "\n"
		elif self.type == self.OBSERVE:
			return str(self.val)

class Trace:
	
	def __init__(self):
		self.events = []
		self.ongoingProcesses = {}
		self.idNums = {}
	
	def startProcess(self, id, super = None, processType = None, algorithm = None, inputs = [], desiredEffects = [], sideEffects = []):
		if not super:
			super = "Agent"
		process = Process(id, super, processType, algorithm, inputs, desiredEffects, sideEffects)
		assert id not in self.ongoingProcesses
		self.ongoingProcesses[id] = process
		event = Event(Event.START, process)
		self.events.append(event)
	
	def endProcess(self, id, anomalousEffects = []):
		process = self.ongoingProcesses[id]
		event = Event(Event.END, process)
		self.events.append(event)
		del self.ongoingProcesses[id]
	
	def observe(self, fact, source = None):
		observation = Observation(fact, source)
		self.events.append(Event(Event.OBSERVE, observation))
	
	def __str__(self):
		s = ""
		for event in self.events:
			s += str(event) + "\n"
		return s.lower()
		
