
class Module:
	
	def processStart(self, super, processType = None, algorithm = None, inputs = [], desiredEffects = [], sideEffects = []):
		pNum = self.mem.get("pNum")
		pName = "p" + str(pNum)
		trace = self.mem.get("trace")
		trace.startProcess(pName, super, processType, algorithm, inputs, desiredEffects, sideEffects)
		self.mem.set("pNum", pNum + 1)
		return pName, trace