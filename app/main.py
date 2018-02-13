import bottle
import os
import random

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

    dim = Point(data['width'], data['height'])
    
    head = Point(data['you']['body']['data'][0]['x'], 
                 data['you']['body']['data'][0]['y'])

    body_data = data['you']['body']['data'][1:]
    body = []
    for b in body_data:
        body.append(Point(b['x'], b['y']))

    possible_directions = ['up', 'down', 'left', 'right']

    # Don't move into your body
    if (head.right() in body and 'right' in possible_directions):
        possible_directions.remove('right')
    if (head.left() in body and 'left' in possible_directions):
        possible_directions.remove('left')
    if (head.up() in body and 'up' in possible_directions):
        possible_directions.remove('up')
    if (head.down() in body and 'down' in possible_directions):
        possible_directions.remove('down')

    # Don't move into the wall
    if (head.left().x < 0 and 'left' in possible_directions):
        possible_directions.remove('left')
    if (head.right().x > dim.x and 'right' in possible_directions):
        possible_directions.remove('right')
    if (head.down().y > dim.y and 'down' in possible_directions):
        possible_directions.remove('down')
    if (head.up().y < 0 and 'up' in possible_directions):
        possible_directions.remove('up')

    safe_directions = possible_directions[:]

    # Move towards the first food
    food = Point(data['food']['data'][0]['x'],
                 data['food']['data'][0]['y'])
    if (head.x == food.x):
        if ('left' in possible_directions):
            possible_directions.remove('left')
        if ('right' in possible_directions):
            possible_directions.remove('right')
    elif (head.y == food.y):
        if ('up' in possible_directions):
            possible_directions.remove('up')
        if ('down' in possible_directions):
            possible_directions.remove('down')

    if (head.x > food.x and 'right' in possible_directions):
        possible_directions.remove('right')
    if (head.x < food.x and 'left' in possible_directions):
        possible_directions.remove('left')
    if (head.y < food.y and 'up' in possible_directions):
        possible_directions.remove('up')
    if (head.y > food.y and 'down' in possible_directions):
        possible_directions.remove('down')

    smart_directions = possible_directions[:]
    
    # Prioritize safe moves if no smart move available
    if (len(smart_directions) == 0):
        move = random.choice(safe_directions)
    elif (len(smart_directions) == 1):
        move = smart_directions.pop()
    else:
        move = random.choice(smart_directions)

    return {
        'move': move,
        'taunt': 'battlesnake-python!'
    }


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()
if __name__ == '__main__':
    bottle.run(application, host=os.getenv('IP', '0.0.0.0'), port=os.getenv('PORT', '8080'))
