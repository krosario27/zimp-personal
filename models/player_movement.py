from abc import ABC, abstractmethod
from enums.directions import Direction


class PlayerMovement(ABC):
    def __init__(self, player, direction):
        self.player = player
        self.direction = direction

    # Template Method
    def move(self):
        new_position = self.calculate_new_position()
        if new_position is None:
            print("Invalid direction provided")
            return False

        if self.is_existing_tile(new_position):
            next_tile = self.player.grid[new_position]
            if not self.prepare_next_tile(next_tile):
                return False
            return self.update_position(new_position, next_tile)
        next_tile = self.draw_new_tile()
        if not next_tile:
            return False
        self.player.grid[new_position] = next_tile
        return self.update_position(new_position, next_tile)

    def calculate_new_position(self):
        """Calculate new position based on direction."""
        x, y = self.player.position
        return {
            Direction.LEFT: (x - 1, y),
            Direction.UP: (x, y + 1),
            Direction.RIGHT: (x + 1, y),
            Direction.DOWN: (x, y - 1),
        }.get(self.direction)

    def is_existing_tile(self, new_position):
        """Check if the tile already exists in the grid."""
        return new_position in self.player.grid

    def prepare_next_tile(self, next_tile):
        """Check if the tile already exists in the grid."""
        if not self.align_exits(next_tile):
            return False
        return self.check_environment(next_tile)

    def align_exits(self, next_tile):
        """Rotate tile to align exits."""
        opposite_index = Direction.opposite(self.direction).value
        for _ in range(4):
            if next_tile.walls[opposite_index] == 0:
                print(f"Aligned exits for movement to {next_tile.name}")
                return True
            next_tile.rotate()
        print(f"Failed to align exits for {next_tile.name}")
        return next_tile.walls[opposite_index] == 0

    @abstractmethod
    def check_environment(self, next_tile):
        """Check environment-specific rules. To be overridden by subclasses."""
        raise NotImplementedError

    def update_position(self, new_position, next_tile):
        """Update player position and move them to the new tile."""
        self.player.previous_tile = self.player.current_tile
        self.player.current_tile = next_tile
        self.player.position = new_position
        print(
            self.player.localization["p_player_moved_from_to"].format(
                direction=self.direction.name.lower(),
                current_tile=self.player.current_tile.name,
            )
        )
        self.player.print_exits()
        self.player.visited_tiles.append(self.player.current_tile)
        return True

    @abstractmethod
    def draw_new_tile(self):
        """Draw a new tile. To be overridden by subclasses."""
        raise NotImplementedError
