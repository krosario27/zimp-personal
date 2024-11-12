from abc import ABC, abstractmethod
from enums.directions import Direction


class PlayerMovement(ABC):
    def __init__(self, player, direction):
        self._player = player       # Use _player to suggest protected access
        self._direction = direction # Use _direction to suggest protected access

    # Template Method
    def move(self):
        new_position = self.calculate_new_position()
        if new_position is None:
            print("Invalid direction provided")
            return False

        if self.is_existing_tile(new_position):
            next_tile = self._player.grid[new_position]
            if not self._prepare_next_tile(next_tile):
                return False
            return self.update_position(new_position, next_tile)

        next_tile = self.draw_new_tile()
        if not next_tile:
            return False
        self._player.grid[new_position] = next_tile
        return self.update_position(new_position, next_tile)

    def calculate_new_position(self):
        """Calculate new position based on direction."""
        x, y = self._player.position
        return {
            Direction.LEFT: (x - 1, y),
            Direction.UP: (x, y + 1),
            Direction.RIGHT: (x + 1, y),
            Direction.DOWN: (x, y - 1),
        }.get(self._direction)

    def is_existing_tile(self, new_position):
        """Check if the tile already exists in the grid."""
        return new_position in self._player.grid

    def _prepare_next_tile(self, next_tile):
        """Prepare the next tile before moving the player."""
        if not self._align_exits(next_tile):
            return False
        return self.check_environment(next_tile)  # check_environment remains public

    def _align_exits(self, next_tile):
        """Rotate tile to align exits."""
        opposite_index = Direction.opposite(self._direction).value
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
        self._player.previous_tile = self._player.current_tile
        self._player.current_tile = next_tile
        self._player.position = new_position
        print(
            self._player.localization["p_player_moved_from_to"].format(
                direction=self._direction.name.lower(),
                current_tile=self._player.current_tile.name,
            )
        )
        self._player.print_exits()
        self._player.visited_tiles.append(self._player.current_tile)
        return True

    @abstractmethod
    def draw_new_tile(self):
        """Draw a new tile. To be overridden by subclasses."""
        raise NotImplementedError

