
ON_TABLE = 0.25
ON_NOT_CLEAR = 0.4
ON_CLEAR = 0.6
HELD = 0.8

BLOCK = 0.33
TRIANGLE = 0.45
FIRE = 0.8

class MIDCANetState:
	
	def __init__(self, world):
		self.inputLocations = []
		#print world.objects
		#print world.atoms
		#print world.predicates
		for objName in world.objects:
			locVal = None
			if world.is_true("on-table", [objName]):
				locVal = ON_TABLE
			elif world.is_true("clear", [objName]):
				locVal = ON_CLEAR
			elif world.is_true("holding", [objName]):
				locVal = HELD
			else:
				locVal = ON_NOT_CLEAR			
			if not locVal:
				continue #not a block 
			if world.is_true("onfire", [objName]):
				self.inputLocations.append((FIRE, locVal))
			if world.is_true("block", [objName]):
				self.inputLocations.append((BLOCK, locVal))
			elif world.is_true("triangle", [objName]):
				self.inputLocations.append((TRIANGLE, locVal))

	def locDicts(self):
		return [{loc: 1.0} for loc in self.inputLocations]

class StateMem:
	
	def __init__(self):
		self.states = []
	
	def add(self, state):
		self.states.append(state)
