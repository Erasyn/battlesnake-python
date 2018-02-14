import bottle
import os
import random

class Board:
    '''Simple class to represent the board'''

    def __init__(self, data):
        '''Sets the board information'''
        self.width = data['width']
        self.height = data['height']

    def is_outside(self, p):
        '''Return true if p is in-bounds'''
        return p.x < 0 or p.y < 0 or p.x >= self.width or p.y >= self.height

class Snake:
    '''Simple class to represent the snake'''

    def __init__(self, data):
        '''Sets up the snakes information'''
        self.head = Point(data['you']['body']['data'][0]['x'], 
                          data['you']['body']['data'][0]['y'])

        self.body = []
        for b in data['you']['body']['data'][1:]:
            self.body.append(Point(b['x'], b['y']))

        self.safe_moves = ['up', 'down', 'left', 'right']
        self.preferred_moves = ['up', 'down', 'left', 'right']

    def dont_move(self, direction):
        '''Update the safe moves'''
        if (direction in self.safe_moves):
            self.safe_moves.remove(direction)

    def try_not_to_move(self, direction):
        '''Update the preferred moves'''
        if (direction in self.preferred_moves):
            self.preferred_moves.remove(direction)

    def prevent_collisions(self, board):
        '''Remove moves that will collide (with anything)'''
        if (self.head.right() in self.body or 
                board.is_outside(self.head.right())):
            self.dont_move('right')
        if (self.head.left() in self.body or 
                board.is_outside(self.head.left())):
            self.dont_move('left')
        if (self.head.up() in self.body or 
                board.is_outside(self.head.up())):
            self.dont_move('up')
        if (self.head.down() in self.body or 
                board.is_outside(self.head.down())):
            self.dont_move('down')

        self.preferred_moves = self.safe_moves[:]

    def prefer_moves_towards(self, p):
        '''Remove moves that take you away from p'''
        if (self.head.x >= p.x):
            self.try_not_to_move('right')
        if (self.head.x <= p.x):
            self.try_not_to_move('left')
        if (self.head.y <= p.y):
            self.try_not_to_move('up')
        if (self.head.y >= p.y):
            self.try_not_to_move('down')

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
    
    board = Board(data)
    snake = Snake(data)
    food = Point(data['food']['data'][0]['x'], # Only works with a single 
                 data['food']['data'][0]['y']) # food right now...

    snake.prevent_collisions(board)
    snake.prefer_moves_towards(food)
    move = snake.get_next_move()

    return {
        'move': move,
        'taunt': 'battlesnake-python!'
    }


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()
if __name__ == '__main__':
    bottle.run(application, host=os.getenv('IP', '0.0.0.0'), port=os.getenv('PORT', '8080'))
