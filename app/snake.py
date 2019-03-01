import random

from util import debug
from point import Point, point_from_string

class Snake:
    '''Simple class to represent a snake'''

    def __init__(self, board, data):
        '''Sets up the snake's information'''
        self.board = board
        self.id = data['id']
        self.name = data['name']
        self.health = data['health']
        self.head = Point(data['body'][0]['x'], 
                          data['body'][0]['y'])
        self.tail = Point(data['body'][-1]['x'], 
                          data['body'][-1]['y'])
        self.body = []

        for b in data['body'][1:]:
            self.body.append(Point(b['x'], b['y']))

        self.length = len(self.body)

    # High level, composable actions the snake can perform

    def smart_movement(self):
        '''Attempt at a smart decision making snake (in progress)'''
        if not self.eat_closest_food():
            debug('smart_movement: No path to food')
            self.smart_walk()
        elif not self.is_smart_move(self.head.get(self.next_move)):
            debug('smart_movement: No smart move to food')
            self.smart_walk()

    def eat_closest_food(self):
        '''High level goal to eat the food we are closest to. Returns False
        if there is no closest food we can head towards.'''
        distances = self.board.distances(self.head, self.board.food)
        if distances:
            closest_food = point_from_string(min(distances, key=distances.get))
            return self.move_towards(closest_food)
        return False

    def random_walk(self):
        '''High level goal to perform a random walk (mostly for testing). 
        Returns False if there are no valid moves (i.e. you are trapped.)'''
        valid = self.valid_moves()
        if valid:
            self.next_move = random.choice(valid)
            return True
        return False

    def random_smart_walk(self):
        '''Like above but only smart moves'''
        smart = self.smart_moves()
        if smart: 
            self.next_move = random.choice(smart)
            return True
        return False

    def walk(self):
        '''Like random_walk but deterministic (good for testing)'''
        valid = self.valid_moves()
        if valid:
            self.next_move = random.choice(valid)
            return True
        return False

    def smart_walk(self):
        '''Like random_smart_walk but deterministic (good for testing)'''
        smart = self.smart_moves()
        if smart: 
            self.next_move = random.choice(smart)
            return True
        return False

    def chase_tail(self):
        # TODO Make this used
        '''High level goal to chase tail tightly. Return False if there is no
        path to your tail.'''
        tail = self.body[-1]
        return self.move_towards(tail)

    def move_towards(self, point):
        '''High level goal to move (with pathfinding) towards a point. Returns
        False if no path is found.'''
        path = self.board.a_star_path(self.head, point)
        if path:
            direction = self.head.direction_of(path[0])
            self.next_move = direction
            return True
        debug('move_towards: no path found to point ' + str(point))
        return False

    # Utility functions, etc.

    def valid_moves(self):
        '''Returns a list of moves that will not immediately kill the snake'''
        moves = ['up', 'down', 'left', 'right']
        for move in moves[:]:
            next_pos = self.head.get(move)
            if (next_pos in self.board.obstacles or 
                    self.board.is_outside(next_pos)):
                moves.remove(move)
        return moves

    def smart_moves(self):
        '''Returns a list of moves that are self-preserving'''
        moves = self.valid_moves()
        for move in moves[:]:
            next_pos = self.head.get(move)
            if not self.is_smart_move(next_pos):
                moves.remove(move)
        return moves

    def is_smart_move(self, point):
        '''Returns true if moving to the point is self-preserving. If False,
        the move won't kill you now, but it might or might in the future.'''
        if self.board.is_threatened_by_enemy(point):
            return False
        if self.is_not_trapped_with_no_out(point):
            return False
        return True

    def is_not_constricting_self(self, point):
        '''Returns True if moving here will put us in a smaller area'''
        possible_moves = self.valid_moves()

        if len(possible_moves) == 0:
            return

        areas = {}
        for move in possible_moves:
            areas[move] = self.board.count_available_space(self.head.get(move))

        best_area = max(areas.values)
        next_area = self.board.count_available_space(point)

        if(best_area == next_area):
            return False
        return True

    def is_not_trapped_with_no_out(self, point):
        '''Returns True if moving here will put us in an area without any tails'''
        possible_moves = self.valid_moves()

        if len(possible_moves) == 0:
            return

        areas = {}
        for move in possible_moves:
            areas[move] = self.board.count_available_space_and_snake_data(self.head.get(move))
        # have some check to see when this is necessary and speed this up
        best_area = sorted(areas.items(), key=lambda e: (e[1][2], e[1][2] > e[1][1], e[1][1] > 0, -e[1][1], e[1][0]), reverse=True)[0][1]
        #  This is good, needs to go to a tail space over space with no tails.
        # print("best area", best_area)
        # tails > heads # heads == tails # tails > 0 # heads > 0 # max area
        # {'s': [8, 0, 0], 't': [20, 0, 0], 'k': [9, 1, 0], 'e': [8, 3, 1], 'r': [4, 1, 1], 'o': [3, 0, 1], 'c': [8, 1, 2]}

        print(areas)
        next_area = self.board.count_available_space_and_snake_data(point)
        print(next_area, best_area)

        if(best_area == next_area):
            return False
        return True