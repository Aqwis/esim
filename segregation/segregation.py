#!/usr/bin/env python3

## An implementation of Thomas Schelling's model of segregation
## http://nifty.stanford.edu/2014/mccown-schelling-model-segregation/

import numpy
import matplotlib.pyplot as plt

from random import random, choice

Px = 0.2 # Probability of kind X
Po = 0.1 # Probability of kind O
# 1-Px-Po is the probability of a position being empty

INFLUENCE_PERIMETER = 6 # Number of positions on each side of an individual that the individual cares about
MOVE_PERIMETER = 6 # Number of positions away from its current position an individual can move
LIMIT = 0.6 # Ratio of same/(other+same), below which individual wants to move

MOVE_TO_BETTER = 'move-to-better'
MOVE_TO_BEST_ALTERNATIVE = 'move-to-best-alternative'
MOVE_RANDOMLY = 'move-randomly'

class SegregationSystem:
	def __init__(self, n, influence_perimeter, move_perimeter, limit, strategy=MOVE_TO_BETTER, debug=False):
		self.n = n
		self.influence_perimeter = influence_perimeter
		self.move_perimeter = move_perimeter
		self.limit = limit
		self.strategy = strategy
		self.debug = debug
		self.matrix = numpy.zeros(shape=(n, n), dtype=object)

		for i in range(self.n):
			for j in range(self.n):
				rand = random()
				if rand > (1-Px):
					self.matrix[i][j] = 'X';
				elif rand > (1-Px-Po):
					self.matrix[i][j] = 'O';
				else:
					self.matrix[i][j] = ' ';

	def calculate_ratio(self, i, j, kind):
		# Checks if individual in position (i, j) wants to move
		# Returns true if individual wants to move, and false otherwise

		top_boundary = i-self.influence_perimeter if i-self.influence_perimeter >= 0 else 0
		bottom_boundary = i+self.influence_perimeter if i+self.influence_perimeter < self.n else self.n-1

		left_boundary = j-self.influence_perimeter if j-self.influence_perimeter >= 0 else 0
		right_boundary = j+self.influence_perimeter if j+self.influence_perimeter < self.n else self.n-1

		X_count = 0
		O_count = 0
		for k in range(top_boundary, bottom_boundary+1):
			for l in range(left_boundary, right_boundary+1):
				if self.matrix[k][l] == 'X':
					X_count += 1
				elif self.matrix[k][l] == 'O':
					O_count += 1
				elif self.matrix[k][l] == ' ':
					pass
				else:
					raise Exception('Position (%s, %s) contained invalid element!' % (k, l,))

		ratio = 0
		if kind == 'X':
			X_count -= 1
			if X_count + O_count == 0:
				return 0.5
			ratio = X_count/(X_count + O_count)
		elif kind == 'O':
			O_count -= 1
			if X_count + O_count == 0:
				return 0.5
			ratio = O_count/(X_count + O_count)

		return ratio

	def check(self, i, j):
		if self.matrix[i][j] in ('X', 'O'):
			ratio = self.calculate_ratio(i, j, self.matrix[i][j])
		else:
			return False

		if ratio > self.limit:
			return False # Doesn't want to move
		else:
			return True # Wants to move

	def move(self, i, j):
		# Moves an individual to a neighbouring position with a higher ratio than that of the one it is currently in
		kind = self.matrix[i][j]
		original_ratio = self.calculate_ratio(i, j, kind)

		top_boundary = i-self.move_perimeter if i-self.move_perimeter >= 0 else 0
		bottom_boundary = i+self.move_perimeter if i+self.move_perimeter < self.n else self.n-1

		left_boundary = j-self.move_perimeter if j-self.move_perimeter >= 0 else 0
		right_boundary = j+self.move_perimeter if j+self.move_perimeter < self.n else self.n-1

		if self.strategy in (MOVE_TO_BETTER, MOVE_TO_BEST_ALTERNATIVE):
			reference = 0
			top_score = 0
			if self.strategy == MOVE_TO_BETTER:
				reference = original_ratio
				top_score = original_ratio
			top_k = -1
			top_l = -1
			for k in range(top_boundary, bottom_boundary+1):
				for l in range(left_boundary, right_boundary+1):
					if self.matrix[k][l] == ' ':
						self.matrix[i][j] = ' '
						ratio = self.calculate_ratio(k, l, kind)
						self.matrix[i][j] = kind
						if ratio > top_score:
							top_score = ratio
							top_k = k
							top_l = l

			if top_k != -1 and top_l != -1 and top_score > reference:
				self.matrix[i][j] = ' '
				self.matrix[top_k][top_l] = kind
				if self.debug:
					print('Moved (%s, %s) to (%s, %s)' % (i, j, top_k, top_l,))
				return True # moved
			return False # did not move
		elif self.strategy == MOVE_RANDOMLY:
			available = []
			for k in range(top_boundary, bottom_boundary+1):
				for l in range(left_boundary, right_boundary+1):
					if self.matrix[k][l] == ' ':
						available.append((k, l))
			if len(available) == 0:
				return False # did not move
			new_position = choice(available)
			self.matrix[i][j] = ' '
			self.matrix[new_position[0]][new_position[1]] = kind
			if self.debug:
				print('Moved (%s, %s) to (%s, %s)' % (i, j, new_position[0], new_position[1],))
			return True # moved
		else:
			raise Exception('Invalid strategy "%s"' % (self.strategy,))

	def run(self):
		number_moved = 0
		for i in range(self.n):
			for j in range(self.n):
				if self.check(i, j):
					if self.move(i, j):
						number_moved += 1
		return number_moved

	def run_rounds(self, round_count):
		rounds_finished = 0
		for r in range(round_count):
			if self.debug:
				print('\nNew round:')
				print(self.matrix)
			number_moved = self.run()

			if number_moved == 0:
				print('Converged after running %s rounds' % (rounds_finished,))
				return

			rounds_finished += 1
			if self.debug:
				input()

	def simulate(self, round_count):
		start_matrix = numpy.matrix.copy(self.matrix)
		self.run_rounds(round_count)

		print('\nStart matrix:')
		print(start_matrix)

		print('\nEnd matrix:')
		print(self.matrix)

		return self.matrix

def plot(matrix):
	n = matrix.shape[0]
	num_matrix = numpy.zeros(shape=(n, n))
	for k in range(matrix.shape[0]):
		for l in range(matrix.shape[1]):
			if matrix[k][l] == 'X':
				num_matrix[k][l] = 1;
			elif matrix[k][l] == 'O':
				num_matrix[k][l] = -1;
			elif matrix[k][l] == ' ':
				num_matrix[k][l] = 0;
			else:
				raise Exception('Position (%s, %s) contained invalid element!' % (k, l,))

	plt.matshow(num_matrix)
	plt.savefig('output.png')

def main():
	system = SegregationSystem(80, INFLUENCE_PERIMETER, MOVE_PERIMETER, LIMIT, strategy=MOVE_RANDOMLY)
	matrix = system.simulate(20) # should be higher when using the strategy MOVE_RANDOMLY
	plot(matrix)

if __name__ == "__main__":
	main()