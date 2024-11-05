from enum import Enum

#represents four directional moves
class Direction(Enum):
    #each movement is assigned a number which will be used for comparison and indexing
    LEFT = 0
    UP = 1
    RIGHT = 2
    DOWN = 3

    @staticmethod
    def opposite(direction):
        opposites = {
            Direction.LEFT: Direction.RIGHT,
            Direction.UP: Direction.DOWN,
            Direction.RIGHT: Direction.LEFT,
            Direction.DOWN: Direction.UP
        }
        return opposites[direction]


