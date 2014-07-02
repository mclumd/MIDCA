import sys, cPickle
sys.path.append("../../")
from utils import adistadapt, pyNet
from modules import module

class AnomalyDetector:
	
	def __init__(self, world, mem, memKeys, threshold = 0.5, size = None):
		self.mem = mem
		self.memKeys = memKeys
		if size:
			aDist = adistadapt.ADistWrapper(threshold, windowsize = size)
		else:
			aDist = adistadapt.ADistWrapper(threshold)
		aDist.init(world)
		self.mem.update({self.memKeys.MEM_ADIST: [aDist]})
		self.dimension = len(adistadapt.get_pred_names(world))
	
	def update(self, world):
		self.mem.update_all(self.memKeys.MEM_ADIST, world)
	
	def anomalous(self):
		wrappers = self.mem.get(self.memKeys.MEM_ADIST)
		for wrapper in wrappers:
			for pred in range(len(wrapper.trace.values[-1])):
				val, threshold = wrapper.trace.values[-1][pred]
				if val > threshold:
					return pred
		return False
	
	def clear(self):
		self.mem.remove(self.memKeys.MEM_ADIST)
	
	def add_WP(self, windowStart, threshold = 0.5, size = None):
		if not self.mem.get("worldStates"):
			raise Exception("World states not in memory; cannot create new WP")
		states = self.mem.get("worldStates")
		if len(states) < windowStart + 1:
			raise Exception("Starting WP in future not allowed")
		if size:
			aDist = adistadapt.ADistWrapper(threshold, size, start = windowStart)
		else:
			aDist = adistadapt.ADistWrapper(threshold, start = windowStart)
		aDist.init(states[windowStart])
		windowStart += 1
		if windowStart + aDist.windowsize >= len(states):
			for i in range(windowStart, len(states)):
				aDist.update(states[i])
		else:
			#fill first window, then add last windows' width of data
			for i in range(windowStart, windowStart + aDist.windowsize):
				aDist.update(states[i])
			for i in range(max(i, len(states) - windowSize), len(states)):
				aDist.update(states[i])	
		self.mem.update({self.memKeys.MEM_ADIST: aDist})
	
	def __str__(self):
		s = ""
		n = 1
		for aDist in self.mem.get(self.memKeys.MEM_ADIST):
			s += "Window Pair " + str(n) + ". Window start time = " + str(aDist.start) + "\n" + str(aDist) + "\n"
			n += 1
		return s[:-1]

class ADNoter(module.Module):
	
	def __init__(self, windowsize = None, threshold = 0.5):
		self.size = windowsize
		self.threshold = threshold
	
	def init(self, world, mem, memKeys):
		self.detector = AnomalyDetector(world, mem, memKeys, self.threshold, self.size)
		self.mem = mem
		self.memKeys = memKeys
		#net stuff:
		self.mem.set("net mem", pyNet.midcastate.StateMem())
		self.numFires = 0
	
	def update(self, world):
		self.detector.update(world)
	
	def anomalous(self):
		return self.detector.anomalous()
	
	def run(self, verbose = 2):
		world = self.mem.get(self.memKeys.MEM_STATES)[-1]
		#net
		freeArsonist = False
		for atom in world.atoms:
			if atom.predicate.name == "onfire":
				self.numFires += 1
				print "total fires:", self.numFires
			elif atom.predicate.name == "free":
				freeArsonist = True
		if not freeArsonist:
			self.numFires -= 3 #gradually turn off anomaly memory
		#end net
		super = "p" + str(self.mem.get("pNum") - 1)
		pName, trace = self.processStart(super, processType = "anomaly detection", algorithm = "a-distance")
		self.update(world)
		self.mem.add(self.memKeys.MEM_ANOM, self.anomalous())
		if self.anomalous():
			trace.observe("anomaly detected", pName)
		else:
			trace.observe("no anomaly detected", pName)
		trace.endProcess(pName)
		if verbose >= 1 and self.anomalous():
			print "Anomaly detected."
		elif verbose >= 2 and not self.anomalous():
			print "No anomaly detected."
		#net stuff:
		anomalyRating = max(0, min(1, self.numFires * 0.2))
		netMem = self.mem.get("net mem")
		netMem.add(pyNet.midcastate.MIDCANetState(world), anomalyRating)
		f = open("/Users/swordofmorning/Documents/_programming/repos/MIDCA/utils/pyNet/test/lateFire2", 'w')
		cPickle.dump([netMem.value(i) for i in range(len(netMem))], f)
		f.close()
		
	
	#simple implementaton; will not work with multiple windows
	def __str__(self):
		s = str(self.detector)
		return s[s.rindex("\n") + 1:]
	
			
