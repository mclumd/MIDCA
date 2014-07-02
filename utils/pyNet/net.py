import random, numpy, math

class Neuron:
	
	nextID = 1
	
	def __init__(self, activationFunction):
		self.incomingConnections = {}
		self.activation = 0
		self.nextActivation = 0
		self.input = 0
		self.activationFunction = activationFunction
		self.id = self.nextID
		Neuron.nextID += 1
	
	def calculateNextActivation(self):
		self.input = sum([neuron.activation * weight for neuron, weight in self.incomingConnections.items()])
		
		#print self.id, ":", self.input
		#for neuron, weight in self.incomingConnections.items():
			#print '\t', neuron.id, weight, neuron.activation
		self.nextActivation = self.activationFunction.get(self.input, self.activation)
		#print self.nextActivation, "\n"
		
		#activation function takes (input, lastActivation) as params.
	
	def update(self):
		self.activation = self.nextActivation
	
	def addConnection(self, neuron, weight):
		self.incomingConnections[neuron] = weight
	
	def removeConnection(self, neuron):
		if neuron in self.incomingConnections:
			del self.incomingConnections[neuron]
	
	def connectionWeight(self, neuron):
		if neuron not in self.incomingConnections:
			return 0
		return self.incomingConnections[neuron]

class InputNeuron:
	
	def __init__(self, activation):
		self.activation = activation

class OutputNeuron(Neuron):
	
	def learnNewWeights(self, expectedOutput, learnRate):
		error = expectedOutput - self.nextActivation
		derivative = self.activationFunction.derivative(self.input, self.activation)
		newWeights = {neuron: learnRate * error * derivative * neuron.activation + weight for neuron, weight in self.incomingConnections.items()}
		self.incomingConnections = newWeights

class Net:
	
	def __init__(self):
		self.reservoir = set()
		self.inputs = set()
		self.outputs = set()
	
	def calculateActivations(self):
		for neuron in self.reservoir:
			neuron.calculateNextActivation()
		for neuron in self.outputs:
			neuron.calculateNextActivation()
		
	def learn(self, expectedOutputs, learnRate):
		'''
		expectedOutputs is a map {outputNode: expectedOutput}
		'''
		for neuron in expectedOutputs:
			if neuron not in self.outputs:
				raise Exception("Expected output set for neuron " + str(neuron) + " which is not in the output set.")
			neuron.learnNewWeights(expectedOutputs[neuron], learnRate)
	
	def update(self):
		for neuron in self.reservoir:
			neuron.update()
		for neuron in self.outputs:
			neuron.update()
	
	def zeroActivations(self):
		for neuron in self.reservoir:
			neuron.activation = 0
	
class RandomNet(Net):
	
	def __init__(self, reservoirSize, reservoirActivationFunc, outputActivationFunc, connectivity, connectivityVariance, spectralRadius):
		self.reservoir = {Neuron(reservoirActivationFunc) for i in range(reservoirSize)}
		self.outputs = set()
		self.inputs = set()
		self.createRandomConnections(connectivity, connectivityVariance)
		self.scaleWeights(spectralRadius)
		
	def chooseRandomNeuron(self, choices):
		if not choices:
			raise Exception("No choices for random neuron")
		if not isinstance(choices, dict):
			choices = {choice: 1.0 for choice in choices}
		totalProb = sum(choices.values())
		probIndex = random.random() * totalProb
		#print probIndex, totalProb
		current = 0.0
		for choice, probability in choices.items():
			if current + probability > probIndex:
				#print probability, probability / totalProb
				return choice
			current += probability
		assert False #should never reach here without choosing a neuron.
	
	def getConnectionProbabilities(self, neuron):
		'''
		overwrite this to change connection behavior.
		'''
		choices = {}
		for otherNeuron in self.reservoir:
			if otherNeuron != neuron:
				choices[otherNeuron] = 1.0
		return choices
	
	def randomWeightsGaussian(self, num, mean, variance, minEach, maxEach, minTotal, maxTotal):
		if num <= 0:
			return []
		weights = [min(maxEach, max(minEach, random.gauss(mean, variance))) for i in range(num)]
		total = sum(weights)
		if total > maxTotal:
			change = (maxTotal - total) / num
			weights = [weight + change for weight in weights]
		elif total < minTotal:
			change = (minTotal - total) / num
			weights = [weight + change for weight in weights]
		return weights
	
	def randomWeightsUniform(self, num):
		return [random.random() for i in range(num)]
	
	def getWeightMatrix(self):
		orderedNeurons = list(self.reservoir)
		matrix = []
		for neuron in orderedNeurons:
			matrix.append([])
			for otherNeuron in orderedNeurons:
				if otherNeuron in neuron.incomingConnections:
					matrix[-1].append(neuron.connectionWeight(otherNeuron))
				else:
					matrix[-1].append(0)
		matrix = numpy.array(matrix)
		return matrix
	
	def getWeightMultiplier(self):
		matrix = self.getWeightMatrix()
		spectralRadius = float(max(numpy.linalg.eigvals(matrix)))
		return 1.0 / spectralRadius
	
	def scaleWeights(self, targetRadius):
		multiplier = self.getWeightMultiplier() * targetRadius
		for neuron in self.reservoir:
			neuron.incomingConnections = {connection: weight * multiplier for connection, weight in neuron.incomingConnections.items()}
	
	def getRandomConnections(self, neuron, num, choices):
		connections = []
		#print "min:", min([distance(self.locations[neuron], self.locations[other]) for other in self.reservoir]), "score:", max([1.0 / max(0.001, distance(self.locations[neuron], self.locations[other]) ** self.distanceImportance) for other in self.reservoir])
		for i in range(num):
			connection = self.chooseRandomNeuron(choices)
			#print distance(self.locations[connection], self.locations[neuron])
			connections.append(connection)
			del choices[connection]
		return connections
	
	def addRandomConnections(self, neuron, num, choices):
		connections = self.getRandomConnections(neuron, num, choices)
		weights = self.randomWeightsUniform(num)
		for i in range(len(connections)):
			neuron.addConnection(connections[i], weights[i])		
	
	def createRandomConnections(self, connectivity, variance):
		for neuron in self.reservoir:
			numConnections = int(round(random.gauss(connectivity, variance)))
			self.addRandomConnections(neuron, numConnections, self.getConnectionProbabilities(neuron))
	
	def addOutput(self):
		output = OutputNeuron(Identity())
		for neuron in self.reservoir:
			output.addConnection(neuron, 0.0)
		self.outputs.add(output)
		return output

def distance(loc1, loc2):
	total = 0
	for i in range(len(loc1)):
		total += (loc1[i] - loc2[i]) ** 2
	return total ** 0.5

class LocalizedNet(RandomNet):
	
	def __init__(self, reservoirSize, reservoirActivationFunc, outputActivationFunc, connectivity, connectivityVariance, spectralRadius, distanceImportance):
		self.reservoir = {Neuron(reservoirActivationFunc) for i in range(reservoirSize)}
		self.locations = {neuron: (random.random(), random.random()) for neuron in self.reservoir}
		self.distanceImportance = distanceImportance
		self.outputs = set()
		self.inputs = set()
		self.inputDurations = {}
		self.createRandomConnections(connectivity, connectivityVariance)
		self.scaleWeights(spectralRadius)
	
	def getConnectionProbabilities(self, neuron):
		'''
		overwrite this to change connection behavior.
		'''
		choices = {}
		for otherNeuron in self.reservoir:
			if otherNeuron != neuron:
				choices[otherNeuron] = 1.0 / max(0.0000000001, distance(self.locations[neuron], self.locations[otherNeuron]) ** self.distanceImportance)
		return choices
	
	def width(self):
		return 1.0
	
	def height(self):
		return 1.0
	
	def inputConnectionProbabilities(self, locs):
		choices = {}
		for neuron in self.reservoir:
			choices[neuron] = max([1 / max(0.0000000001, distance(self.locations[neuron], loc) ** self.distanceImportance) for loc in locs])
		return choices
	
	def addInput(self, locs, connectivity, variance, duration = 999999, totalStrength = 0.8, strengthVariance = 0.2):
		'''
		strengthVariance is a ratio (to mean strength). The input neuron actually always has activation 1; weights are adjusted to fit desired strength.
		
		Connectivity is per loc; locs is a dict {loc: probability}
		'''
		input = InputNeuron(1.0)
		numConnections = int(round(len(locs) * random.gauss(connectivity, variance)))
		connections = self.getRandomConnections(input, numConnections, self.inputConnectionProbabilities(locs))
		weights = [max(0.0, random.gauss(1.0, strengthVariance)) for connection in connections]
		total = sum(weights)
		weights = [weight * totalStrength / total for weight in weights]
		i = 0
		for connection in connections:
			connection.addConnection(input, weights[i])
			i += 1
		self.inputs.add(input)
		#note: the following line does not generalize. Fix later.
		if locs:
			self.locations[input] = list(locs)[0]
		else:
			self.locations[input] = (0.5, 0.5)
		self.inputDurations[input] = duration
	
	def clearInputs(self):
		for input in self.inputs:
			for neuron in self.reservoir:
				if input in neuron.incomingConnections:
					neuron.removeConnection(input)
			del self.locations[input]
		self.inputs.clear()
		self.inputDurations.clear()
		

class Logistic:
	
	def get(self, input, activation):
		return (1.0 / (1 + math.exp(-input)) - .5) * 2
	
	def derivative(self, input, activation):
		val = self.get(input, activation)
		return val * (1 - val)

class Tanh:
	
	def get(self, input, activation):
		return (1 - math.exp(-2 * input)) / (1 + math.exp(-2 * input))
	
	def derivative(self, input, activation):
		val = self.get(input, activation)
		return 1 - val ** 2
		
class Identity:
	
	def get(self, input, activation):
		return input
	
	def derivative(self, input, activation):
		return 1

def setInputs(state, network):
	network.clearInputs()
	for locDict in state:
		#print "adding input", locDict
		network.addInput(locDict, 3.0, 0.5)

def createNetFromMidcaData(dataFileNames, destFileName):
	import cPickle, record
	network = LocalizedNet(200, Tanh(), Identity(), 3, 1.0, 0.98, 5)
	mem = record.Memory()
	mem.store(network)
	output = network.addOutput()
	random.shuffle(dataFileNames)
	for fileName in dataFileNames:
		states = cPickle.load(open(fileName))
		for locDict, trainVal in states:
			for i in range(5):
				setInputs(locDict, network)
				network.calculateActivations()
				network.learn({output: trainVal}, 0.1)
				network.update
				mem.store(network)
	cPickle.dump((network, mem), open(destFileName, 'w'))

if __name__ == "__main__":

	dataFileNames = ["/Users/swordofmorning/Documents/_programming/repos/MIDCA/utils/pyNet/train/data" + str(i) for i in range(1, 11)]
	destFileName = "/Users/swordofmorning/Documents/_programming/repos/MIDCA/utils/pyNet/trainedNets/net"
	createNetFromMidcaData(dataFileNames, destFileName)