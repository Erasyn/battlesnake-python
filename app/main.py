import bottle
import os

from board import Board

@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')

@bottle.post('/start')
def start():
    return {
        "color": "#002200",
        "headType":"",
        "tailType":""
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
        'taunt': 'drawing...'
    }

@bottle.post('/end')
def end():
    return {}

@bottle.post('/ping')
def ping():
    return {}

# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()
if __name__ == '__main__':
    bottle.run(application, host=os.getenv('IP', '0.0.0.0'), port=os.getenv('PORT', '8080'))
