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