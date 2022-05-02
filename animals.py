
import numpy as np

class Animal:
    def __init__(self, world, identity, dom, soc, cur, sick, x, y):
        print(world, identity, dom, soc, cur, x, y)
        self.world = world  # the board - (x,x,3)
        self.id = identity

        # personality
        self.dominance = dom  # between 0 and 1
        self.sociability = soc  # between -1 and 1
        self.curiosity = cur  # between 0 and 1

        #
        self.current_hunger = 1
        self.sickness_probability = sick  # between 0 and 0.1
        self.is_sick = False
        self.sickness_timer = 3
        self.position_x = x
        self.position_y = y
        self.world.set_as_occupied(self.position_x, self.position_y, self.id)
        self.is_alive = True
        self.cause_of_death = None
        self.last_visited = []


    # methods

    def get_surroundings(self):
        surroundings = [[self.position_x - 1, self.position_y, 0],
                          [self.position_x - 1, self.position_y + 1, 0],
                          [self.position_x, self.position_y + 1, 0],
                          [self.position_x + 1, self.position_y + 1, 0],
                          [self.position_x + 1, self.position_y, 0],
                          [self.position_x + 1, self.position_y - 1, 0],
                          [self.position_x, self.position_y - 1, 0],
                          [self.position_x - 1, self.position_y - 1, 0]]

        return np.array(surroundings)

    def update_last_visited(self):
        if len(self.last_visited) == 5:
            self.last_visited.pop(0)
        self.last_visited.append((self.position_x, self.position_y))

    def remove_out_of_bounds_slots(self, surroundings):
        indices_to_remove1 = np.where(surroundings[:, 0] < 0)
        indices_to_remove2 = np.where(surroundings[:, 1] < 0)
        indices_to_remove3 = np.where(surroundings[:, 0] >= self.world.board_size)
        indices_to_remove4 = np.where(surroundings[:, 1] >= self.world.board_size)
        indices_to_remove5 = np.hstack((indices_to_remove1, indices_to_remove2))
        indices_to_remove6 = np.hstack((indices_to_remove3, indices_to_remove4))
        indices_to_remove7 = np.unique(np.hstack((indices_to_remove5, indices_to_remove6)))
        # removing impossible moves
        return np.delete(surroundings, indices_to_remove7, axis=0)


    def add_food_factor_to_decision(self, possible_moves):
        food_indices = np.where(self.world.board[possible_moves[:, 0], possible_moves[:, 1], :][:, 2] == 1)
        possible_moves = possible_moves.astype(np.float)
        possible_moves[food_indices, 2] = 1 - self.current_hunger
        return possible_moves

    def add_sociability_factor_to_decision(self, possible_moves):
        occupied_indices = np.where(self.world.board[possible_moves[:, 0].astype(np.int), possible_moves[:, 1].astype(np.int), :][:, 0] > 0)[0]

        for i in range(occupied_indices.shape[0]):
            for j in range(possible_moves.shape[0]):
                if abs(possible_moves[occupied_indices[i], 0] - possible_moves[j, 0]) <= 1 and abs(
                        possible_moves[occupied_indices[i], 1] - possible_moves[j, 1]) <= 1:
                    possible_moves[j, 2] += self.sociability

        possible_moves = np.delete(possible_moves, occupied_indices, axis=0)
        return possible_moves

    def add_curiosity_factor_to_decision(self, possible_moves):
        for j in range(possible_moves.shape[0]):
            if (possible_moves[j, 0], possible_moves[j, 1]) in self.last_visited:
                possible_moves[j, 2] -= self.curiosity

        danger_indices = np.where(self.world.board[possible_moves[:, 0].astype(np.int), possible_moves[:, 1].astype(np.int), :][:, 1] > 0)
        possible_moves = possible_moves.astype(np.float)
        possible_moves[danger_indices, 2] -= 1 - self.curiosity
        return possible_moves


    def calculate_move(self):
        possible_moves = self.remove_out_of_bounds_slots(self.get_surroundings())

        # adding food factor
        possible_moves = self.add_food_factor_to_decision(possible_moves)

        # adding sociability factor
        possible_moves = self.add_sociability_factor_to_decision(possible_moves)

        # adding curiosity factor
        possible_moves = self.add_curiosity_factor_to_decision(possible_moves)


        if possible_moves.shape[0] != 0:
            chosen_move_index = np.argmax(possible_moves[:, 2])
            return tuple([possible_moves[chosen_move_index, 0], possible_moves[chosen_move_index, 1]])
        return (self.position_x, self.position_y)



    def move(self):
        chosen_move = self.calculate_move()
        self.world.set_as_free(self.position_x, self.position_y)
        self.position_x = int(chosen_move[0])
        self.position_y = int(chosen_move[1])
        self.world.set_as_occupied(self.position_x, self.position_y, self.id)
        self.update_last_visited()
        self.move_consequence()

    def starvation_consequence(self):
        if self.world.is_there_food(self.position_x, self.position_y):
            self.current_hunger = 1
        else:
            self.current_hunger = round(self.current_hunger - 0.1, 1)
            if self.current_hunger == 0:
                self.death(1)

    def danger_consequence(self):
        danger_level = self.world.is_there_danger(self.position_x, self.position_y)
        if danger_level:
            performance = np.random.uniform(0, 1)
            if performance < danger_level:
                self.death(2)

    def sickness_consequence(self):
        if self.is_sick:
            if not self.sickness_timer:
                self.is_sick = False
                self.sickness_timer = 3
            else:
                self.sickness_timer -= 1

                # death by disease
                death_probability = np.random.uniform(0, 1)
                if death_probability < 0.05:
                    self.death(3)

                # infecting
                my_surroundings = self.remove_out_of_bounds_slots(self.get_surroundings())
                occupied_indices = np.where(self.world.board[my_surroundings[:, 0].astype(np.int), my_surroundings[:, 1].astype(np.int), :][:, 0] > 0)[0]

                for i in range(occupied_indices.shape[0]):
                    neighbour = self.world.get_animal_by_index(my_surroundings[occupied_indices[i], 0],
                                                               my_surroundings[occupied_indices[i], 1])
                    neighbour.is_sick = np.random.uniform(0, 1) < 0.25
        else:

            # disease status
            sickness_develpoment = np.random.uniform(0, 1)
            self.is_sick = sickness_develpoment < self.sickness_probability

    def move_consequence(self):

        # starvation status
        self.starvation_consequence()

        # danger status
        self.danger_consequence()

        # sickness status
        self.sickness_consequence()

    def death(self, cause):
        self.is_alive = False
        self.cause_of_death = cause
        self.world.set_as_free(self.position_x, self.position_y)


    def print_animal(self):
        string = f"id: {self.id}, life: {self.is_alive}, hunger: {self.current_hunger}, sickneses: {self.is_sick} position: ({self.position_x},{self.position_y})"
        print(string)
