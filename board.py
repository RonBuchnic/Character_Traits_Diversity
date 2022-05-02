import numpy as np
from animals import Animal
import random


class Board:

    def __init__(self, board_size):
        self.board_size = board_size
        self.board = np.zeros((board_size, board_size, 3))
        self.sample_from = np.arange(0, board_size)
        self.animals = []

    def add_food(self, percentage):
        coordinates_x, coordinates_y = self.random_indices(percentage)
        self.board[coordinates_x, coordinates_y, 2] = 1

    def add_danger(self, percentage_of_dangerous_slots, danger_range_min, danger_range_max):
        coordinates_x, coordinates_y = self.random_indices(percentage_of_dangerous_slots)
        self.board[coordinates_x, coordinates_y, 1] = np.random.uniform(danger_range_min, danger_range_max, int(percentage_of_dangerous_slots / 100 * (self.board_size ** 2)))

    def random_indices(self, percentage):

        indices_x = np.random.choice(self.sample_from, int(percentage / 100 * (self.board_size ** 2)), replace=True)
        indices_y = np.random.choice(self.sample_from, int(percentage / 100 * (self.board_size ** 2)), replace=True)
        return indices_x, indices_y

    def is_occupied(self, x, y):
        return self.board[x, y, 0]

    def set_as_occupied(self, x, y, id):
        if self.board[x, y, 0]:
            print("slot is occupied")
            return 0
        self.board[x, y, 0] = id
        return 1

    def set_as_free(self, x, y):
        self.board[x, y, 0] = 0

    def is_there_food(self, x, y):
        return self.board[x, y, 2]

    def is_there_danger(self, x, y):
        return self.board[x, y, 1]

    def random_place(self):
        while True:
            x = random.randint(0, self.board_size - 1)
            y = random.randint(0, self.board_size - 1)
            if not self.is_occupied(x, y):
                return x, y

    def add_animals(self, num):
        dominance = []
        for n in range(num):
            x, y = self.random_place()
            self.animals.append(Animal(self, n+1, random.uniform(0, 1), random.uniform(-1, 1), random.uniform(0, 1), random.uniform(0, 0.1), x, y))
            dominance.append([self.animals[-1].id, self.animals[-1].dominance])
        return sorted(dominance, key=lambda x: x[1], reverse=True)

    def get_animal_by_index(self, x, y):
        animal_id = int(self.board[x, y, 0])
        if not animal_id:
            print("slot is empty")
            return 0
        return self.animals[animal_id - 1]

