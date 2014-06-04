import sys
sys.path.append("../../")
from utils import blockstate, scene
from modules import module

class SimpleObserver(module.Module):

	def init(self, world, mem, memKeys):
		self.world = world
		self.mem = mem
		self.memKeys = memKeys
	
	#perfect observation
	def observe(self):
		return self.world.copy()
	
	def world_repr(self, world):
		blocks = blockstate.get_block_list(world)
		return str(scene.Scene(blocks))
		
	def run(self, verbose = 2):
		world = self.observe()
		if not world:
			raise Exception("World obervation failed.")
		trace = self.mem.get("trace")
		trace.observe(str(world), "p" + str(self.mem.get("pNum") - 1))
		self.mem.add(self.memKeys.MEM_STATES, world)
		repr = str(self.world_repr(world))
		if verbose == 2:
			print "World observed: \n" + str(repr)
		elif verbose == 1:
			print "World observed."