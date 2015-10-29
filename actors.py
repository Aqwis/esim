import random
import uuid


class Person(object):
	def __init__(self):
		## Parameters
		self.illness_risk = 0.05
		# Resources required per turn
		self.required_resources = {
			'water': 50,
			'easily_obtainable_food': 5,
		}

		## State
		self.illnesses = []
		self.resource_deficit = 0
		self.ill = False
		self.dead = False

		self.id = uuid.uuid4()

	def check_if_dead(self):
		if len(self.illnesses) >= 2:
			self.dead = True
		if self.resource_deficit > 100:
			self.dead = True

	def handle_illness(self):
		for illness in self.illnesses:
			illness.act()
		self.illnesses[:] = [illness for illness in self.illnesses if not illness.is_cured]

		if random.random() < self.illness_risk:
			self.illnesses.append(Illness())

	def handle_resource_needs(self, state):
		for resource, amount_required in self.required_resources.items():
			consumed = state.resources[resource].consume(amount_required)
			if consumed < amount_required:
				self.resource_deficit += (amount_required - consumed)

	def live(self, state):
		self.check_if_dead()
		if self.dead:
			return

		self.handle_illness()
		self.handle_resource_needs(state)


class Resource(object):
	def __init__(self, name, abundance, regeneration_rate):
		self.name = name
		self.abundance = abundance
		self.regeneration_rate = regeneration_rate

	def consume(self, amount):
		if self.abundance > amount:
			self.abundance = self.abundance - amount
			return amount
		else:
			consumed = self.abundance
			self.abundance = 0
			return consumed

	def act(self):
		self.abundance += self.regeneration_rate

class Company(object):
	pass


class Illness(object):
	def __init__(self):
		self.duration_remaining = 3
		self.is_cured = False

	def act(self):
		if not self.is_cured:
			self.duration_remaining -= 1
		else:
			self.is_cured = True