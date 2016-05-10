import random

from copy import copy

from actors import Person, Company, Resource

class WorldState(object):
	def __init__(self):
		self.year = 0
		self.people = []
		self.resources = {}

class Simulation(object):
	def __init__(self):
		# Parameters
		self.POPULATION = 5000

		# State
		self.state = WorldState()

		# Statistics
		self.state_by_year = {}

		for p in range(self.POPULATION):
			self.state.people.append(Person())

		self.state.resources['water'] = Resource('water', 5000000, 1000000)
		self.state.resources['easily_obtainable_food'] = Resource('easily_obtainable_food', 25000, 5000)

	def register_state(self):
		self.state_by_year[self.state.year] = copy(self.state)

	def display_state(self):
		print("Number of people alive: " + str(len(self.state.people)))
		print("År: " + str(self.state.year))

	def write_population_statistics_to_csv(self):
		population_tuple_list = sorted([(year, len(state.people)) for year, state in self.state_by_year.items()], key=lambda x: x[0])
		with open('population.csv', 'w+') as popfile:
			for year, population in population_tuple_list:
				popfile.write('%s,%s\n' % (year, population,))

	def loop(self):
		self.state.people = [person for person in self.state.people if not person.dead]

		random.shuffle(self.state.people)
		for person in self.state.people:
			person.live(self.state)

		for resource_name, resource in self.state.resources.items():
			resource.act()

	def run(self):
		while len(self.state.people) > 0:
			self.register_state()
			self.display_state()
			self.loop()
			self.state.year += 1
		self.register_state()
		self.display_state()

		self.write_population_statistics_to_csv()
			

def main():
	simulation = Simulation()
	simulation.run()

if __name__ == "__main__":
	main()