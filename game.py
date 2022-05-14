from board import Board
import matplotlib.pyplot as plt
import numpy as np
import sys
from functools import reduce
np.set_printoptions(threshold=sys.maxsize)


class Game:
    def __init__(self, board_size):
        self.my_board = Board(board_size)
        self.moving_order = None
        self.num_of_living_animals_by_turn = []
        self.dominance_average_by_turn = []
        self.sociability_average_by_turn = []

        self.curiosity_average_by_turn = []
        self.starvation_deaths_by_turn = [0]
        self.danger_deaths_by_turn = [0]
        self.disease_deaths_by_turn = [0]

    def preset_game(self, num_of_animals, food_percentage, danger_percentage):
        self.my_board.add_food(food_percentage)
        self.my_board.add_danger(danger_percentage, 0.2, 0.5)

        self.moving_order = self.my_board.add_animals(num_of_animals)
        self.num_of_living_animals_by_turn.append(num_of_animals)

        dominances = map(lambda a: a.dominance, self.my_board.animals)
        dominances_sum = reduce(lambda a, b: a + b, dominances, 0)
        self.dominance_average_by_turn.append(dominances_sum / num_of_animals)

        sociabilities = map(lambda a: a.sociability, self.my_board.animals)
        sociabilities_sum = reduce(lambda a, b: a + b, sociabilities)
        self.sociability_average_by_turn.append(sociabilities_sum / num_of_animals)

        curiosities = map(lambda a: a.curiosity, self.my_board.animals)
        curiosities_sum = reduce(lambda a, b: a + b, curiosities)
        self.curiosity_average_by_turn.append(curiosities_sum / num_of_animals)


    def run_game(self, turns, num_of_animals, food_percentage, danger_percentage):

        self.preset_game(num_of_animals, food_percentage, danger_percentage)

        print("------------------------------------------------------- start game ------------------------------------------------")

        print("occupency is:")
        print(my_game.my_board.board[:, :, 0])

        print("danger is:")
        print(my_game.my_board.board[:, :, 1])

        print("food is:")
        print(my_game.my_board.board[:, :, 2])

        for turn in range(turns):
            self.run_single_turn()
            self.extract_data()
        self.plot(turns)
        print(
            "------------------------------------------------------- end game ------------------------------------------------")

    def run_single_turn(self):
        print("---------------------------------------------------------- new turn -----------------------------------------------")
        for animal_id in self.moving_order:
            animal = self.my_board.animals[animal_id[0] - 1]
            if animal.is_alive:
                animal.move()
                animal.print_animal()


        print("occupency is:")
        print(my_game.my_board.board[:, :, 0])


    def extract_data(self):

        # how many are alive
        living_animals = list(filter(lambda a: a.is_alive, self.my_board.animals))
        num_of_living_animals_on_current_turn = len(living_animals)
        self.num_of_living_animals_by_turn.append(num_of_living_animals_on_current_turn)


        if num_of_living_animals_on_current_turn != 0:

            # average dominance
            dominances = map(lambda a: a.dominance, living_animals)
            dominances_sum = reduce(lambda a, b: a + b, dominances, 0)
            self.dominance_average_by_turn.append(dominances_sum / num_of_living_animals_on_current_turn)
            print(self.dominance_average_by_turn)

            # average sociability
            sociabilities = map(lambda a: a.sociability, living_animals)
            sociabilities_sum = reduce(lambda a, b: a + b, sociabilities)
            self.sociability_average_by_turn.append(sociabilities_sum / num_of_living_animals_on_current_turn)
            print(self.sociability_average_by_turn)

            # average curiocity
            curiosities = map(lambda a: a.curiosity, living_animals)
            curiosities_sum = reduce(lambda a, b: a + b, curiosities)
            self.curiosity_average_by_turn.append(curiosities_sum / num_of_living_animals_on_current_turn)
            print(self.curiosity_average_by_turn)

        else:
            self.dominance_average_by_turn.append(0)
            self.sociability_average_by_turn.append(0)
            self.curiosity_average_by_turn.append(0)



        starvation_dead_animals = list(filter(lambda a: a.cause_of_death is 1, self.my_board.animals))
        danger_dead_animals = list(filter(lambda a: a.cause_of_death is 2, self.my_board.animals))
        disease_dead_animals = list(filter(lambda a: a.cause_of_death is 3, self.my_board.animals))


        self.starvation_deaths_by_turn.append(len(starvation_dead_animals))
        self.danger_deaths_by_turn.append(len(danger_dead_animals))
        self.disease_deaths_by_turn.append(len(disease_dead_animals))
        print(self.starvation_deaths_by_turn)
        print(self.danger_deaths_by_turn)
        print(self.disease_deaths_by_turn)

    def plot(self, turns):

        x_axis = np.arange(turns+1)
        plt.figure()
        plt.suptitle("")
        plt.subplot(1, 2, 1)
        plt.title("Population Size and Death by Cause")

        plt.plot(x_axis,  self.num_of_living_animals_by_turn, label="living")

        plt.plot(x_axis, self.starvation_deaths_by_turn, label="starvation")
        plt.plot(x_axis, self.danger_deaths_by_turn, label="danger")
        plt.plot(x_axis, self.disease_deaths_by_turn, label="disease")

        plt.legend()
        plt.ylabel("Number of Animals")
        plt.xlabel("Turns")


        plt.subplot(1, 2, 2)
        plt.title("Property Averages")
        plt.plot(x_axis, self.dominance_average_by_turn, label="dominance")
        plt.plot(x_axis, self.sociability_average_by_turn, label="sociability")
        plt.plot(x_axis, self.curiosity_average_by_turn, label="curiosity")
        plt.legend()

        plt.ylabel("Value in (-1,1)")
        plt.xlabel("Turns")
        plt.show()


if __name__ == "__main__":
    my_game = Game(10)
    my_game.run_game(50, 10, 25, 5)
