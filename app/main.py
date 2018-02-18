import bottle
import os
import random

class Board:
    '''Simple class to represent the board'''

    def __init__(self, data):
        '''Sets the board information'''
        self.width = data['width']
        self.height = data['height']
        self.obstacles = []
        self.food = []
        self.flood_visited = [] 

        for p in data['you']['body']['data']:
            self.obstacles.append(Point(p['x'], p['y']))

        # TODO: Add other snake's bodies to obstacles

        for p in data['food']['data']:
            self.food.append(Point(p['x'], p['y']))

    def is_outside(self, p):
        '''Return true if p is out-of-bounds'''
        return p.x < 0 or p.y < 0 or p.x >= self.width or p.y >= self.height

    def fill_size(self, p):
        '''flood fill out from p and return the area'''
        self.flood_visited = [] 
        return self.rec_flood_fill(p)
    
    def rec_flood_fill(self, p):
        '''Recursive flood fill'''
        if (p in self.flood_visited or 
            p in self.obstacles or 
            self.is_outside(p)):
            return 0

        self.flood_visited.append(p)
        return 1 + self.rec_flood_fill(p.left()) + \
                   self.rec_flood_fill(p.right()) + \
                   self.rec_flood_fill(p.up()) + \
                   self.rec_flood_fill(p.down())

class Snake:
    '''Simple class to represent the snake'''

    def __init__(self, data):
        '''Sets up the snakes information'''
        self.board = Board(data)

        self.head = Point(data['you']['body']['data'][0]['x'], 
                          data['you']['body']['data'][0]['y'])

        self.body = []
        for b in data['you']['body']['data'][1:]:
            self.body.append(Point(b['x'], b['y']))


    def eat_food(self):
        '''High level goal to eat the food we are closest to'''
        food = self.head.closest(self.board.food)
        self.move_towards(food)

    def move_random(self):
        '''High level goal to move to a random place on the board'''
        point = 
    
    def move_towards(self, g):
        # TODO: Now you can make this smarter, without worry about about
        # anything except best way to move between two points on the board.
        self.safe_moves = ['up', 'down', 'left', 'right'] # Won't kill you
        self.preferred_moves = [] # Move you closer to goal
        self.prevent_collisions()
        self.prefer_moves_towards(g)

    def dont_move(self, direction):
        '''Update the safe moves'''
        if (direction in self.safe_moves):
            self.safe_moves.remove(direction)

    def try_not_to_move(self, direction):
        '''Update the preferred moves'''
        if (direction in self.preferred_moves):
            self.preferred_moves.remove(direction)

    def prevent_collisions(self):
        '''Remove moves that will collide (with anything)'''
        if (self.head.right() in self.body or 
                self.board.is_outside(self.head.right())):
            self.dont_move('right')
        if (self.head.left() in self.body or 
                self.board.is_outside(self.head.left())):
            self.dont_move('left')
        if (self.head.up() in self.body or 
                self.board.is_outside(self.head.up())):
            self.dont_move('up')
        if (self.head.down() in self.body or 
                self.board.is_outside(self.head.down())):
            self.dont_move('down')

    def prefer_moves_towards(self, p):
        '''Remove moves that take you away from p'''
        self.preferred_moves = self.safe_moves[:]

        if (self.head.x >= p.x):
            self.try_not_to_move('right')
        if (self.head.x <= p.x):
            self.try_not_to_move('left')
        if (self.head.y <= p.y):
            self.try_not_to_move('up')
        if (self.head.y >= p.y):
            self.try_not_to_move('down')

    def dont_trap_self(self, board):
        smart_moves = self.safe_moves[:]

        for m in smart_moves:
            pos = self.head.get(m) 
            if (board.fill_size(pos) < len(self.body)):
                smart_moves.remove(m)
        self.preferred_moves = list(set(self.preferred_moves) & set(smart_moves))
            

    def get_next_move(self):
        '''Return a preferred move, or just a safe one'''
        if (len(self.preferred_moves)):
            return self.preferred_moves.pop()
        return self.safe_moves.pop()

class Point:
    '''Simple class for 2d points'''

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
        if (len(l) > 1):
            for p in l:
                if (self.dist(p) < self.dist(closest)):
                    closest = p
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
        'head_type': 'smile',
        'tail_type': 'block-bum'
    }


@bottle.post('/move')
def move():
    data = bottle.request.json
    
    # Setup our snake and define its goals
    snake = Snake(data)
    snake.eat_food()

    return {
        'move': snake.get_next_move(),
        'taunt': 'battlesnake-python!'
    }


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()
if __name__ == '__main__':
    bottle.run(application, host=os.getenv('IP', '0.0.0.0'), port=os.getenv('PORT', '8080'))
