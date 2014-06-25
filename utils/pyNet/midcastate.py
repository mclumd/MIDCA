
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
		for objName in world.objects:
			locVal = None
			if world.is_true("on-table", objName):
				locVal = ON_TABLE
			elif world.is_true("on", objName):
				if world.is_true("clear", objName):
					locVal = ON_CLEAR
				else:
					locVal = ON_NOT_CLEAR
			elif world.is_true("holding", objName):
				locVal = HELD
			if not locVal:
				continue #not a block 
			if world.is_true("onfire", objName):
				self.inputLocations.append((FIRE, locVal))
			if world.is_true("block", objName):
				self.inputLocations.append((BLOCK, locVal))
			elif world.is_true("triangle", objName):
				self.inputLocations.append((TRIANGLE, locVal))

def get_block_list(world):
	blocks = {}
	for obj in world.objects.values():
		if obj.type.name != "BLOCK":
			continue
		block = None
		if world.atom_true(worldsim.Atom(world.predicates["table"], [obj])):
			block = Block(Block.TABLE, obj.name)
		elif world.atom_true(worldsim.Atom(world.predicates["triangle"], [obj])):
			block = Block(Block.TRIANGLE, obj.name)
		elif world.atom_true(worldsim.Atom(world.predicates["block"], [obj])):
			block = Block(Block.SQUARE, obj.name)
		if not block:
			continue
		block.clear = False
		block.on = None
		block.onfire = False
		if block.type == block.TABLE:
			table = block
		blocks[obj.name] = block
	for atom in world.atoms:
		if atom.predicate == world.predicates["on"]:
			blocks[atom.args[0].name].on = blocks[atom.args[1].name]
		elif atom.predicate == world.predicates["on-table"]:
			blocks[atom.args[0].name].on = table
		elif atom.predicate == world.predicates["clear"]:
			blocks[atom.args[0].name].clear = True
		elif atom.predicate == world.predicates["onfire"]:
			blocks[atom.args[0].name].onfire = True
	return sorted(blocks.values(), key = lambda x: x.id)
