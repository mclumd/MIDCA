import net, record, cPickle, random, pygame, sys

from pygame.locals import *
pygame.font.init()

def createNetFromMidcaData(dataFileNames, destFileName):
	network = net.LocalizedNet(200, net.Tanh(), net.Identity(), 3, 1.0, 0.98, 5)
	mem = record.Memory()
	mem.store(network)
	output = network.addOutput()
	random.shuffle(dataFileNames)
	n = random.choice(list(network.reservoir))
	for fileName in dataFileNames:
		network.zeroActivations()
		states = cPickle.load(open(fileName))
		for locDict, trainVal in states:
			for i in range(5):
				net.setInputs(locDict, network)
				for neuron in network.inputs:
					pass#print "input activation", neuron.activation
				for neuron in network.reservoir:
					for connection, weight in neuron.incomingConnections.items():
						if connection in network.inputs:
							pass#print "input connection weight", weight
				network.calculateActivations()
				for neuron in network.reservoir:
					if (set(neuron.incomingConnections.keys()) & network.inputs):
						pass#print neuron.activation, neuron.nextActivation
				network.learn({output: trainVal}, 0.1)
				network.update()
				#print sum([neuron.activation for neuron in network.reservoir])
				mem.store(network)
	cPickle.dump((network, mem), open(destFileName, 'w'))

def runRecord(fName, screenSize):
	network, mem = cPickle.load(open(fName))
	drawer = record.Drawer(screenSize, mem)
	
	pygame.init()
	screen = pygame.display.set_mode(screenSize, DOUBLEBUF | RESIZABLE)
	screen.fill((0, 0, 0))
	drawer.drawNext(screen)
	pygame.display.flip()
	
	clock = pygame.time.Clock()
	elapsed = 0
	while drawer.hasNext():
		msElapsed = clock.tick(40)
		#print msElapsed
		elapsed += msElapsed
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
		if elapsed >= 200:
			drawer.next()
			#print sum([neuron.activation for neuron in drawer.memory.mem[drawer.i].reservoir])
			screen.fill((0, 0, 0))
			drawer.drawNext(screen)
			pygame.display.flip()
			elapsed = 0

class TestResult:
	
	def __init__(self, name, mem):
		self.name = name
		self.mem = mem
		self.trials = {}
	
	def addResult(self, trial, expectedValue, actualValue):
		if trial not in self.trials:
			self.trials[trial] = []
		self.trials[trial].append((expectedValue, actualValue))
	
	def accuracy(self, epsilon, maxVal, minVal):
		correct = 0
		total = 0
		for vals in self.trials.values():
			for expected, actual in vals:
				if abs(min(maxVal, max(minVal, actual)) - expected) < epsilon:
					correct += 1
				total += 1
		return float(correct) / total
	
	def accuracy2(self):
		correct = 0
		total = 0
		for vals in self.trials.values():
			for expected, actual in vals:
				if (expected < .5 and actual < .5) or (expected > .5 and actual > .5) or (abs(expected - actual) < 0.2 and abs(expected - 0.5 < 0.2)):
					correct += 1
				total += 1
		return float(correct) / total
		

def runTest(recordFileName, testFiles, destFolder):
	network, mem = cPickle.load(open(recordFileName))
	
	for name, files in testFiles.items():
		testMem = record.Memory()
		result = TestResult(name, testMem)
		i = 1
		for fileName in files:
			
			network.zeroActivations()
			mem.store(network)
			states = cPickle.load(open(fileName))
				
			for locDict, trainVal in states:
				for i in range(5):
					net.setInputs(locDict, network)
					network.calculateActivations()
					network.update()
					testMem.store(network)
					result.addResult(str(i), trainVal, list(network.outputs)[0].activation)
			i += 1
					
		cPickle.dump(result, open(destFolder + "/" + name + "Results", 'w'))
		print name, ":", result.accuracy(0.3, 2.0, -1), result.accuracy2()
		#print result.trials

if __name__ == "__main__":
	
	
	runRecord("/home/user1/Written/Studies/UMD/GRA_Perlis/meeting_notes/mida/MIDCA/utils/pyNet/trainedNets/net2", (400, 400))
	sys.exit()
	
	runRecord("/Users/swordofmorning/Documents/_programming/repos/MIDCA/utils/pyNet/trainedNets/net2", (400, 400))
	sys.exit()
	runTest("/Users/swordofmorning/Documents/_programming/repos/MIDCA/utils/pyNet/trainedNets/net2", 
	{"lateFire": {"/Users/swordofmorning/Documents/_programming/repos/MIDCA/utils/pyNet/test/lateFire1", "/Users/swordofmorning/Documents/_programming/repos/MIDCA/utils/pyNet/test/lateFire2"},
	"noFire": {"/Users/swordofmorning/Documents/_programming/repos/MIDCA/utils/pyNet/test/noFire1", "/Users/swordofmorning/Documents/_programming/repos/MIDCA/utils/pyNet/test/noFire2"},
	"lotsFire": {"/Users/swordofmorning/Documents/_programming/repos/MIDCA/utils/pyNet/test/lotsFire1", "/Users/swordofmorning/Documents/_programming/repos/MIDCA/utils/pyNet/test/lotsFire2"}}, "/Users/swordofmorning/Documents/_programming/repos/MIDCA/utils/pyNet/results")
	sys.exit()
	
	dataFileNames = ["/Users/swordofmorning/Documents/_programming/repos/MIDCA/utils/pyNet/train/data" + str(i) for i in range(1, 11)]
	destFileName = "/Users/swordofmorning/Documents/_programming/repos/MIDCA/utils/pyNet/trainedNets/net2"
	createNetFromMidcaData(dataFileNames, destFileName)