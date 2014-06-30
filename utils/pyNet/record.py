import pygame, random, net, cPickle, midcastate

from pygame.locals import *
pygame.font.init()

from Tkinter import *

class NetFrame:
	
	def __init__(self, reservoir, inputs, outputs, locations, dimensions):
		self.reservoir = set(reservoir)
		self.inputs = set(inputs)
		self.outputs = set(outputs)
		self.locations = dict(locations)
		self.dimensions = dimensions
	
class Memory:
	
	def __init__(self):
		self.mem = []
	
	def store(self, net):
		self.mem.append(NetFrame(net.reservoir, net.inputs, net.outputs, net.locations, (net.width(), net.height())))
	
	def __getitem__(self, i):
		return self.mem[i]


class Drawer:
	
	neuronRadius = 4
	
	def __init__(self, size, memory):
		self.memory = memory
		self.i = 0
	
	def hasNext(self):
		return len(memory.mem) > self.i
	
	def getColor(self, intensity):
		r = int(round(min(255, (intensity ** .5) * 300)))
		g = int(round(min(255, (intensity ** .5) * 300)))
		b = int(round(min(255, max(0, (intensity - .5) * 500))))
		return pygame.Color(r, g, b, min(255, int(intensity * 1000)))
	
	def getConnectionColor(self, weight):
		r = 255#int(round(min(255, (weight * 1000))))
		g = 0
		b = 0
		return pygame.Color(r, g, b, max(0, min(255, int((weight - 0.1) * 1000))))
	
	def addNeuronIntensities(self, activation, loc, intensities):
		for x in range(-self.neuronRadius, self.neuronRadius + 1):
			if loc[0] + x < 0 or loc[0] + x >= len(intensities):
				continue
			for y in range(-self.neuronRadius, self.neuronRadius + 1):
				if loc[1] + y < 0 or loc[1] + y >= len(intensities[0]):
					continue
				distance = (x ** 2 + y ** 2) ** .5
				intensity = max(0, activation * (1 - distance / self.neuronRadius))
				intensities[loc[0] + x][loc[1] + y] += intensity
	
	def drawNeurons(self, neurons, locations, scale, surface):
		intensities = [[0 for y in range(surface.get_height())] for x in range(surface.get_width())]
		for neuron in neurons:
			x = int(round(locations[neuron][0] / scale[0] * surface.get_width()))
			y = int(round(locations[neuron][1] / scale[1] * surface.get_height()))
			self.addNeuronIntensities(neuron.activation, (x, y), intensities)	
		pixArray = pygame.PixelArray(surface)
		for x in range(surface.get_width()):
			for y in range(surface.get_height()):
				if intensities[x][y] > 0:
					pixArray[x, y] = self.getColor(intensities[x][y])
		del pixArray
	
	def drawInputs(self, inputs, locations, scale, surface):
		for inputs in inputs:
			x = int(round(locations[inputs][0] / scale[0] * surface.get_width()))
			y = int(round(locations[inputs][1] / scale[1] * surface.get_height()))
			pygame.draw.circle(surface, (150, 0, 0), (x, y), 10, 1)
	
	def drawConnections(self, neurons, locations, scale, surface):
		for neuron in neurons:
			startX = int(round(locations[neuron][0] / scale[0] * surface.get_width()))
			startY = int(round(locations[neuron][1] / scale[1] * surface.get_height()))
			for connection, weight in neuron.incomingConnections.items():
				endX = int(round(locations[connection][0] / scale[0] * surface.get_width()))
				endY = int(round(locations[connection][1] / scale[1] * surface.get_height()))
				if ((startX - endX) ** 2 + (startY - endY) ** 2) ** .5 < 0:
					pygame.draw.line(surface, self.getConnectionColor(weight * connection.activation), (startX, startY), (endX, endY), 2)
			
	
	def drawNext(self, surface):
		frame = self.memory[self.i]
		#self.drawConnections(frame.reservoir, frame.locations, frame.dimensions, surface)
		self.drawNeurons(frame.reservoir, frame.locations, frame.dimensions, surface)
		self.drawInputs(frame.inputs, frame.locations, frame.dimensions, surface)
	
	def next(self):
		self.i += 1

def setInputs(state, network):
	network.clearInputs()
	for locDict in state:
		network.addInput(locDict, 3.0, 0.5)

def runOnMidcaData(filename, screenSize):
	states = cPickle.load(open(filename))
	network = net.LocalizedNet(200, net.Tanh(), None, 3, 1.0, 0.98, 5)
	mem = Memory()
	mem.store(network)
	drawer = Drawer(screenSize, mem)
	
	pygame.init()
	screen = pygame.display.set_mode(screenSize, DOUBLEBUF | RESIZABLE)
	screen.fill((0, 0, 0))
	drawer.drawNext(screen)
	pygame.display.flip()
	
	clock = pygame.time.Clock()
	elapsed = 0
	stateIterations = 0
	currentState = states.pop(0)
	
	while 1:
		msElapsed = clock.tick(40)
		#print msElapsed
		elapsed += msElapsed
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
		if elapsed >= 500:
			if stateIterations > 5:
				if states:
					currentState = states.pop(0)
				else:
					currentState = []
				stateIterations = 0
				setInputs(currentState, network)
				print currentState
			network.calculateActivations()
			network.update()
			#inputNeuron.activation = 1.0
			mem.store(network)
			drawer.next()
			screen.fill((0, 0, 0))
			drawer.drawNext(screen)
			pygame.display.flip()
			elapsed = 0
			stateIterations += 1

if __name__ == "__main__":

	DEFAULT_SIZE = (400, 400)
	
	runOnMidcaData("/Users/swordofmorning/Documents/_programming/repos/MIDCA/utils/pyNet/data", DEFAULT_SIZE)
	sys.exit()
	
	network = net.LocalizedNet(200, net.Tanh(), None, 3, 1.0, 0.95, 5)
	for neuron in network.reservoir:
		neuron.activation = random.random()
	inputNeuron = random.choice(list(network.reservoir))
	mem = Memory()
	mem.store(network)
	drawer = Drawer(DEFAULT_SIZE, mem)
			
	pygame.init()
	screen = pygame.display.set_mode(DEFAULT_SIZE, DOUBLEBUF | RESIZABLE)
	screen.fill((0, 0, 0))
	drawer.drawNext(screen)
	pygame.display.flip()
	
	clock = pygame.time.Clock()
	elapsed = 0
	while 1:
		msElapsed = clock.tick(40)
		#print msElapsed
		elapsed += msElapsed
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
		if elapsed >= 500:
			network.calculateActivations()
			network.update()
			#inputNeuron.activation = 1.0
			random.choice(list(network.reservoir)).activation = 1.0
			mem.store(network)
			drawer.next()
			screen.fill((0, 0, 0))
			drawer.drawNext(screen)
			pygame.display.flip()
			elapsed = 0