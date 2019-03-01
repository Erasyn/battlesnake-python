from util import INF
from point import Point, point_from_string
from snake import Snake

class Board:
    '''Simple class to represent the board'''

    def __init__(self, data):
        '''Sets the board information'''
        self.width = data['board']['width']
        self.height = data['board']['height']
        self.player = Snake(self, data['you']) 
        self.enemies = []
        self.turn = data['turn']
        self.food = []
        self.obstacles = []
        self.heads = []
        self.tails = []

        for snake_data in data['board']['snakes']:
            snake = Snake(self, snake_data)
            for point in snake_data['body']:
                self.obstacles.append(Point(point['x'], point['y']))
            if snake.id != self.player.id:
                self.enemies.append(snake)
            self.heads.append(snake.head)
            self.tails.append(snake.tail)

        for p in data['board']['food']:
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

    def count_available_space_and_snake_data(self, p):
        '''flood fill out from p and return the accessible area, head, and tail count'''
        visited = []
        heads = []
        tails = []
        space = self.rec_flood_fill_with_snake_data(p, visited, heads, tails)
        return [space, len(heads), len(tails)]

    def rec_flood_fill_with_snake_data(self, p, visited, heads, tails):
        '''Recursive flood fill that also counts the number of heads and tails'''
        if p in visited or p in self.obstacles or self.is_outside(p):
            if p in self.heads and p not in heads and p != self.player.head:
                heads.append(p)
            if p in self.tails and p not in tails:
                tails.append(p)
            return 0
        visited.append(p)
        return 1 + (self.rec_flood_fill_with_snake_data(p.left(), visited, heads, tails) + 
                    self.rec_flood_fill_with_snake_data(p.right(), visited, heads, tails) + 
                    self.rec_flood_fill_with_snake_data(p.up(), visited, heads, tails) + 
                    self.rec_flood_fill_with_snake_data(p.down(), visited, heads, tails))

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