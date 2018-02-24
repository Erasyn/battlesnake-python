import bottle
import os
import random

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

        for point in data['you']['body']['data']:
            self.obstacles.append(Point(point['x'], point['y']))

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

    def available_space(self, p):
        '''flood fill out from p and return the area'''
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

    def eat_closest_food(self):
        '''High level goal to eat the food we are closest to'''
        food = self.head.closest(self.board.food)
        self.move_towards(food)

    def random_walk(self):
        '''High level goal to perform a random walk (mostly for testing)'''
        move = random.choice(['up', 'down', 'left', 'right'])
        self.move_towards(self.head.get(move))

    def circle_point(self, point):
        '''High level goal to circle a point, head to tail'''
        # TODO: This seems useful but tough to program. Need to think about it.
        pass

    # Below here is all (currently sloppy) movement code
    
    def move_towards(self, g):
        '''Updates next_move to move efficiently towards g'''
        # NOTE: move_towards() could be swapped out with a smarter algo, 
        #       e.g. A* or something without needing to worry about the 
        #       higher level behavior of the snake.

        self.safe_moves = ['up', 'down', 'left', 'right'] # Won't kill you
        self.smart_moves = [] # Don't trap yourself
        self.preferred_moves = [] # Move you closer to goal
        
        self.prevent_collisions()
        self.smart_moves = self.safe_moves[:]
        self.avoid_larger_snakes()
        self.dont_trap_self()
        self.preferred_moves = self.smart_moves[:]
        self.prefer_moves_towards(g)

        if (len(self.preferred_moves)):
            self.next_move = self.preferred_moves.pop()
        elif (len(self.smart_moves)):
            self.next_move = self.smart_moves.pop()
        elif (len(self.safe_moves)):
            self.next_move = self.safe_moves.pop()
        else:
            self.next_move = 'up' # No possible moves

    def prevent_collisions(self):
        '''Remove moves that will collide (with anything)'''
        for move in self.safe_moves[:]:
            next_pos = self.head.get(move)
            if (next_pos in self.board.obstacles or 
                    self.board.is_outside(next_pos)):
                self.safe_moves.remove(move)

    def avoid_larger_snakes(self):
        '''Don't move into the pather of a longer snake''' 
        dangerous = []
        for enemy in self.board.enemies:
            if enemy.length >= self.length:
                dangerous.extend(enemy.head.surrounding_four())
        for move in self.smart_moves:
            next_pos = self.head.get(move)
            if next_pos in dangerous:
                self.smart_moves.remove(move)
                continue

    def dont_trap_self(self):
        '''Avoid moves that constrain you to a small area'''
        if len(self.smart_moves) == 0:
            return

        areas = {}
        for move in self.smart_moves:
            areas[move] = self.board.available_space(self.head.get(move))
        best_area = max(areas.values())

        for move in areas:
            if areas[move] != best_area:
                self.smart_moves.remove(move)

    def prefer_not_to_move(self, direction):
        '''Update the preferred moves'''
        if (direction in self.preferred_moves):
            self.preferred_moves.remove(direction)

    def prefer_moves_towards(self, p):
        '''Remove moves that take you away from p'''
        if (self.head.x >= p.x):
            self.prefer_not_to_move('right')
        if (self.head.x <= p.x):
            self.prefer_not_to_move('left')
        if (self.head.y <= p.y):
            self.prefer_not_to_move('up')
        if (self.head.y >= p.y):
            self.prefer_not_to_move('down')
            
class Point:
    '''Simple class for points'''

    def __init__(self, x, y):
        '''Defines x and y variables'''
        self.x = x
        self.y = y 

    def __eq__(self, other):
        '''Test equality'''
        return self.x == other.x and self.y == other.y

    def closest(self, l):
        '''Returns Point in l closest to self'''
        closest = l[0]
        for point in l:
            if (self.dist(point) < self.dist(closest)):
                closest = point
        return closest

    def dist(self, other):
        '''Calculate Manhattan distance to other point'''
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
        'color': '#00FF00',
        'taunt': '{} ({}x{})'.format(game_id, board_width, board_height),
        'head_url': head_url,
        'name': 'daddy',
        'head_type': 'smile', # TODO: Why aren't these rendering? 
        'tail_type': 'block-bum'
    }


@bottle.post('/move')
def move():
    data = bottle.request.json
    
    # Set-up our snake and define its goals
    board = Board(data)
    snake = board.player
    snake.eat_closest_food()

    return {
        'move': snake.next_move,
        'taunt': 'battlesnake-python!'
    }


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()
if __name__ == '__main__':
    bottle.run(application, host=os.getenv('IP', '0.0.0.0'), port=os.getenv('PORT', '8080'))
