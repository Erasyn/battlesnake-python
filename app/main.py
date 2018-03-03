import bottle
import os
import random

INF = 1000000000
DEBUG = True

def debug(message):
    if DEBUG: print(message)

class Board:
    '''Simple class to represent the board'''

    def __init__(self, data):
        '''Sets the board information'''
        self.width = data['width']
        self.height = data['height']
        self.player = Snake(self, data['you']) 
        self.enemies = []
        self.turn = data['turn']
        self.food = []
        self.obstacles = []

        # for point in data['you']['body']['data'][1:]:
        #     self.obstacles.append(Point(point['x'], point['y']))

        for snake_data in data['snakes']['data']:
            snake = Snake(self, snake_data)
            for point in snake_data['body']['data']:
                self.obstacles.append(Point(point['x'], point['y']))
            if snake.id != self.player.id:
                self.enemies.append(snake) 

        for p in data['food']['data']:
            self.food.append(Point(p['x'], p['y']))

    def is_outside(self, p):
        '''Return true if p is out-of-bounds'''
        return p.x < 0 or p.y < 0 or p.x >= self.width or p.y >= self.height

    def neighbors_of(self, p):
        '''Return list of accessible neighbors of point'''
        res = []
        for p in p.surrounding_four():
            if p not in self.obstacles and not self.is_outside(p):
                res.append(p)
        return res

    def count_available_space(self, p):
        '''flood fill out from p and return the accessible area'''
        visited = [] 
        return self.rec_flood_fill(p, visited)
    
    def rec_flood_fill(self, p, visited):
        '''Recursive flood fill (Used by above method)'''
        if p in visited or p in self.obstacles or self.is_outside(p):
            return 0
        visited.append(p)
        return 1 + (self.rec_flood_fill(p.left(), visited) + 
                    self.rec_flood_fill(p.right(), visited) + 
                    self.rec_flood_fill(p.up(), visited) + 
                    self.rec_flood_fill(p.down(), visited))

    def available_space(self, p):
        '''Same as above but return a list of the points'''
        # TODO: Lazy, should find a better way to achieve this.
        visited = []
        return self.rec_flood_fill2(p, visited)

    def rec_flood_fill2(self, p, visited):
        '''Same as above but returns a list of the points'''
        if p in visited or p in self.obstacles or self.is_outside(p):
            return visited
        visited.append(p)
        self.rec_flood_fill(p.left(), visited)
        self.rec_flood_fill(p.right(), visited)
        self.rec_flood_fill(p.up(), visited)
        self.rec_flood_fill(p.down(), visited)
        return visited

    def distances(self, start, points):
        '''Returns a dict of the distances between start and each point'''
        distances = {}
        for point in points:
            distance = len(self.a_star_path(start, point))
            if distance > 0:
                distances[str(point)] = distance
        return distances

    def is_threatened_by_enemy(self, point):
        '''Returns True if this point is in the path of an enemy'''
        for enemy in self.enemies:
            if enemy.length >= self.player.length:
                if point in enemy.head.surrounding_four():
                    return True
        return False

    def a_star_path(self, start, goal):
        '''Return the A* path from start to goal. Adapted from wikipedia page
        on A*.
        '''
        # TODO: Seems fast enough but code could be cleaned up a bit.

        closed_set = []
        open_set = [start]
        came_from = {}
        g_score = {}
        f_score = {}

        str_start = str(start)
        g_score[str_start] = 0
        f_score[str_start] = start.dist(goal)

        while open_set:
            str_current = str(open_set[0])
            for p in open_set[1:]:
                str_p = str(p)
                if str_p not in f_score:
                    f_score[str_p] = INF
                if str_current not in f_score:
                    f_score[str_current] = INF
                if f_score[str_p] < f_score[str_current]:
                    str_current = str_p

            current = point_from_string(str_current)

            if current == goal:
                path = self.reconstruct_path(came_from, current)
                path.reverse()
                return path[1:]

            open_set.remove(current)
            closed_set.append(current)

            for neighbor in self.neighbors_of(current):
                str_neighbor = str(neighbor)
                if neighbor in closed_set:
                    continue

                if neighbor not in open_set:
                    open_set.append(neighbor)

                if str_current not in g_score:
                    g_score[str_current] = INF
                if str_neighbor not in g_score:
                    g_score[str_neighbor] = INF

                tentative_g_score = (g_score[str_current] + 
                                     current.dist(neighbor))
                if tentative_g_score >= g_score[str_neighbor]:
                    continue

                came_from[str_neighbor] = current
                g_score[str_neighbor] = tentative_g_score
                f_score[str_neighbor] = (g_score[str_neighbor] + 
                                          neighbor.dist(goal))
        return []

    def reconstruct_path(self, came_from, current):
        '''Get the path as a list from A*'''
        total_path = [current]
        while str(current) in came_from.keys():
            current = came_from[str(current)]
            total_path.append(current)
        return total_path
            
class Point:
    '''Simple class for points'''

    def __init__(self, x, y):
        '''Defines x and y variables'''
        self.x = x
        self.y = y 

    def __eq__(self, other):
        '''Test equality'''
        return self.x == other.x and self.y == other.y

    def __str__(self):
        return (str)(self.x) + ',' + (str)(self.y)

    def __repr__(self):
        return self.__str__()

    def closest(self, l):
        '''Returns Point in l closest to self'''
        closest = l[0]
        for point in l:
            if (self.dist(point) < self.dist(closest)):
                closest = point
        return closest

    def dist(self, other):
        '''Calculate Manhattan distance to other point'''
        # TODO: Should use A* dist not Manhattan
        return abs(self.x - other.x) + abs(self.y - other.y)

    def get(self, direction):
        '''get an adjacent point by passing a string'''
        if (direction == 'left'): 
            return self.left()
        if (direction == 'right'):
            return self.right()
        if (direction == 'up'):
            return self.up()
        if (direction == 'down'):
            return self.down()

    def left(self):
        '''Get the point to the left'''
        return Point(self.x-1, self.y)

    def right(self):
        '''Get the point to the right'''
        return Point(self.x+1, self.y)

    def up(self):
        '''Get the point above'''
        return Point(self.x, self.y-1)

    def down(self):
        '''Get the point below'''
        return Point(self.x, self.y+1)

    def surrounding_four(self):
        '''Get a list of the 4 surrounding points'''
        return [self.left(), self.right(), self.up(), self.down()]

    def direction_of(self, point):
        '''Returns (roughly) what direction a point is in'''
        if self.x < point.x: return 'right'
        if self.x > point.x: return 'left'
        if self.y < point.y: return 'down'
        if self.y > point.y: return 'up'
        return 'left' # whatever

def point_from_string(string):
    s = string.split(',')
    return Point(int(s[0]), int(s[1]))

class Snake:
    '''Simple class to represent a snake'''

    def __init__(self, board, data):
        '''Sets up the snake's information'''
        self.board = board
        self.id = data['id']
        self.name = data['name']
        self.health = data['health']
        self.length = data['length']
        self.head = Point(data['body']['data'][0]['x'], 
                          data['body']['data'][0]['y'])
        self.body = []

        for b in data['body']['data'][1:]:
            self.body.append(Point(b['x'], b['y']))

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
        print self.smart_moves()
        if smart: 
            self.next_move = random.choice(smart)
            return True
        return False

    def chase_tail(self):
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
        if self.is_not_constricting_self(point):
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
        best_area = max(areas.values())
        print areas
        next_area = self.board.count_available_space(point)
        print next_area, best_area

        if(best_area == next_area):
            return False
        return True


        # current_space = self.board.count_available_space(self.head)
        # space_from_point = self.board.count_available_space(point)
        # print space_from_point, ",", current_space
        # if (space_from_point < current_space):
        #     return True
        # return False

    # Below here is just a bunch of (currently sloppy) movement code

    def dont_trap_self(self):
        '''Avoid moves that constrain you to a small area'''
        # TODO: Refactor this so it works with the new movement code.
        if len(self.smart_moves) == 0:
            return

        areas = {}
        for move in self.smart_moves:
            areas[move] = self.board.count_available_space(self.head.get(move))
        best_area = max(areas.values())

        for move in areas:
            if areas[move] != best_area:
                self.smart_moves.remove(move)

# The web server methods start here:

@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')


@bottle.post('/start')
def start():
    data = bottle.request.json
    game_id = data['game_id']
    board_width = data['width']
    board_height = data['height']

    head_url = '%s://%s/static/head.png' % (
        bottle.request.urlparts.scheme,
        bottle.request.urlparts.netloc
    )

    return {
        'color': '#000000',
        'taunt': '{} ({}x{})'.format(game_id, board_width, board_height),
        'head_url': head_url,
        'name': 'daddy',
        'head_type': 'smile', # TODO: Why aren't these rendering? 
        'tail_type': 'block-bum'
    }


@bottle.post('/move')
def move():
    data = bottle.request.json
    
    # Set-up our board and snake and define its goals
    board = Board(data)
    snake = board.player
    snake.smart_movement()

    return {
        'move': snake.next_move,
        'taunt': 'battlesnake-python!'
    }


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()
if __name__ == '__main__':
    bottle.run(application, host=os.getenv('IP', '0.0.0.0'), port=os.getenv('PORT', '8080'))
