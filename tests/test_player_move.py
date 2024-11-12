import unittest
from unittest.mock import patch, MagicMock
from models.player import Player
from models.tiles import Tile
from enums.directions import Direction
from models.player_movement import PlayerMovement


class TestPlayerMove(unittest.TestCase):
    def setUp(self):
        self.localization = {
            "p_on_tile_msg": "Player is on {name}.",
            "p_player_moved_from_to": "Moved {direction} to {current_tile}.",
            "p_player_tile_no": "No new tile drawn.",
            "p_aval_exits": "Available exits from {current_tile}: {exits}.",
            "p_error_no_foyer": "No foyer tile found.",
            "p_tile_drew": "You drew the {tile} tile.",
        }
        self.indoor_tiles = [
            Tile(
                8,
                "Foyer",
                [1, 0, 1, 1],
                "None"
            )
        ]
        self.outdoor_tiles = [
            Tile(
                7,
                "Yard",
                [1, 0, 0, 1],
                "None",
                environment="Outdoor"
            ),
            Tile(
                5,
                "Garage",
                [0, 1, 1, 0],
                "None"
            ),
        ]
        self.player = Player(
            self.localization,
            self.indoor_tiles,
            self.outdoor_tiles
        )
        self.player.place_initial_tile()

    def test_move_valid(self):
        # Place the player's current tile at (0, 0) as the initial position
        self.player.grid[(0, 0)] = Tile(
            8,
            "Foyer",
            [1, 0, 1, 1],  # Assuming Foyer has exits open to the right for movement
            "None",
            environment="Indoor"
        )
        self.player.current_tile = self.player.grid[(0, 0)]

        # Place Bathroom tile to the right at (1, 0)
        self.player.grid[(1, 0)] = Tile(
            1,
            "Bathroom",
            [1, 0, 1, 1],  # Bathroom has an exit to the left to allow entry from Foyer
            "None",
            environment="Indoor"
        )

        # Attempt to move to the Bathroom tile to the right
        result = self.player.move(Direction.RIGHT)
        
        # Check that the move was successful
        self.assertTrue(result)

    def test_moved_blocked_wall(self):
        self.player.grid[(1, 0)] = Tile(
            1,
            "Blocked Room",
            [1, 1, 1, 1],
            "None"
        )
        self.player.current_tile = self.player.grid[(0, 0)]
        self.assertFalse(self.player.move(Direction.RIGHT))

    def test_move_invalid_direction(self):
        self.assertFalse(self.player.move(None))

    def test_move_indoor_to_outdoor_requires_totem(self):

        # Place the Dining Room tile at (0, 0) and set it as the current tile
        self.player.grid[(0, 0)] = Tile(
            6,
            "Dining Room",
            [0, 0, 0, 0],  # All exits are open for testing
            "None",
            environment="Indoor"
        )
        self.player.current_tile = self.player.grid[(0, 0)]
    
        # Scenario 1: Moving from Indoor to Outdoor (not Patio) with Totem (Expect False)
        self.player.has_totem = True
        self.player.grid[(0, 1)] = Tile(
            5,
            "Garage",
            [0, 1, 1, 0],  # Specific wall configuration
            "None",
            environment="Outdoor"
        )
        result = self.player.move(Direction.UP)
        self.assertFalse(result)
        self.assertEqual(self.player.current_tile.name, "Dining Room")  # Ensure player is still in Dining Room

        # Scenario 2: Moving from Indoor to Patio without Totem (Expect False)
        self.player.has_totem = False
        self.player.grid[(0, 1)] = Tile(
            6,
            "Patio",
            [1, 0, 0, 0],  # Specific wall configuration
            "None",
            environment="Outdoor"
        )
        self.player.current_tile = self.player.grid[(0, 0)]
        result = self.player.move(Direction.UP)
       
        self.assertFalse(result)

        # Scenario 3: Moving Indoor to Patio with Totem (Expect True)
        self.player.has_totem = True
        self.player.grid[(0, 1)] = Tile(
            6,
            "Patio",
            [1, 0, 0, 0],  # Specific wall configuration
            "None",
            environment="Outdoor"
        )
        result = self.player.move(Direction.UP)
        self.assertTrue(result)  # This should now pass with `return True` in `check_environment`

    def test_move_outdoor_to_indoor_requires_patio(self):

        # Scenario 1: Player tries to move from an outdoor tile (Garage) to an indoor tile (Dining Room) without Patio
        self.player.grid[(0, 0)] = Tile(
            5,
            "Garage",
            [0, 1, 1, 0],
            "None",
            environment="Outdoor"
        )
        self.player.current_tile = self.player.grid[(0, 0)]

        # Place Dining Room tile to the left of Garage at (-1, 0)
        self.player.grid[(-1, 0)] = Tile(
            6,
            "Dining Room",
            [0, 0, 0, 0],
            "None",
            environment="Indoor"
        )
        moved = self.player.move(Direction.LEFT)
        self.assertFalse(moved)
        
        # Scenario 2: Player moves from Patio to Dining Room (expecting True)
        # Place Patio tile at (0, 0) and reset player's current position to Patio
        self.player.grid[(0, 0)] = Tile(
            6,
            "Patio",
            [1, 0, 0, 0],
            "None",
            environment="Outdoor"
        )
        self.player.current_tile = self.player.grid[(0, 0)]

        # Move Dining Room tile to the right of Patio at (1, 0)
        self.player.grid[(0, -1)] = Tile(
            6,
            "Dining Room",
            [0, 0, 0, 0],
            "None",
            environment="Indoor"
        )
        moved = self.player.move(Direction.DOWN)
  
        # Check that the move was successful and the player is now in Dining Room
        self.assertTrue(moved)
        self.assertEqual(self.player.current_tile.name, "Dining Room")

    def test_restrict_indoor_to_outdoor_without_totem(self):
        self.player.grid[(0, 0)] = Tile(
            8,
            "Foyer",
            [1, 0, 1, 1],
            "None",
            environment="Indoor"
        )
        self.player.current_tile = self.player.grid[(0, 0)]
        self.player.grid[(1, 0)] = Tile(
            6,
            "Patio",
            [1, 0, 0, 0],
            "None",
            environment="Outdoor"
        )

        moved = self.player.move(Direction.RIGHT)
        self.assertFalse(moved)

    def test_block_reserved_exit(self):
        dining_room_tile = Tile(
            6,
            "Dining Room",
            [0, 0, 0, 0],
            "None",
            environment="Indoor"
        )

        self.player.block_reserved_exit(dining_room_tile)

        self.assertEqual(dining_room_tile.walls[Direction.UP.value], 1)

    def test_block_reserved_exit_called_during_move(self):
        self.player.grid[(0, 0)] = Tile(
            8,
            "Foyer",
            [1, 0, 1, 1],
            "None",
            environment="Indoor"
        )
        self.player.current_tile = self.player.grid[(0, 0)]

        dining_room_tile = Tile(
            6,
            "Dining Room",
            [0, 0, 0, 0],
            "None",
            environment="Indoor"
        )
        self.player.grid[(1, 0)] = dining_room_tile

        moved = self.player.move(Direction.RIGHT)

        self.assertTrue(moved)
        self.assertEqual(dining_room_tile.walls[Direction.UP.value], 1)

    def test_draw_new_tile_when_moving_to_empty_position(self):

        # Place the Dining Room tile at (0, 0) and set it as the current tile
        self.player.grid[(0, 0)] = Tile(
            6,
            "Dining Room",
            [0, 0, 0, 0],  # All exits are open for testing
            "None",
            environment="Indoor"
        )
        self.player.current_tile = self.player.grid[(0, 0)]

        self.player.indoor_tiles.append(Tile(
            2,
            "Kitchen",
            [0, 0, 0, 1],
            "+1 Health if end turn here.",
            environment="Indoor"
        ))
        # Attempt to move to a position where there is no existing tile in the grid
        result = self.player.move(Direction.RIGHT)


        # Check that the player's current tile is now the newly drawn tile
        self.assertEqual(self.player.current_tile.name, "Kitchen")


        # Scenario 2: Moving to another empty position with no indoor tiles left to draw
        # Clear `indoor_tiles` to trigger the else block
        self.player.indoor_tiles.clear()
        result = self.player.move(Direction.UP)

        # Check that the move was unsuccessful and the player's position hasn't changed
        self.assertFalse(result)
        self.assertEqual(self.player.current_tile.name, "Kitchen")

    def test_outdoor_movement(self):
        
        # Scenario 1: Starting on Patio and moving to an outdoor tile (Garage)
        self.player.grid[(0, 0)] = Tile(
            6,
            "Patio",
            [1, 0, 0, 0],
            "None",
            environment="Outdoor"
        )
        self.player.current_tile = self.player.grid[(0, 0)]

        # Place Garage tile at (0, 1) and move UP to it
        self.player.grid[(0, 1)] = Tile(
            5,
            "Garage",
            [0, 1, 1, 0],
            "None",
            environment="Outdoor"
        )
        moved = self.player.move(Direction.UP)

        self.assertTrue(moved)
        self.assertEqual(self.player.current_tile.name, "Garage")

        # Scenario 2: Moving to an unexplored position to trigger a new outdoor tile draw
        self.player.outdoor_tiles.append(Tile(
            7,
            "Yard",
            [1, 0, 0, 1],
            "None",
            environment="Outdoor"
        ))

        # Move LEFT from Garage to trigger the draw of the next outdoor tile (Yard)
        moved = self.player.move(Direction.LEFT)

        # Verify that the move was successful and the new tile drawn is "Yard"
        self.assertTrue(moved)
        self.assertEqual(self.player.current_tile.name, "Yard")

        self.player.outdoor_tiles.clear()
        
        moved = self.player.move(Direction.LEFT)
   
        # Verify that the move was unsuccessful and the player remains on the current tile
        self.assertFalse(moved)
        self.assertEqual(self.player.current_tile.name, "Yard")


# Create a minimal subclass with empty `pass` implementations for testing instantiation
class TestPlayerMovementWithoutImplementation(PlayerMovement):
    def check_environment(self, next_tile):
        super().check_environment(next_tile)  # Will raise NotImplementedError

    def draw_new_tile(self):
        super().draw_new_tile()  # Will raise NotImplementedError

class TestPlayerMovementNotImplemented(unittest.TestCase):

    def setUp(self):
        # Create a mock player and direction to instantiate PlayerMovement
        self.mock_player = MagicMock()
        self.mock_direction = Direction.RIGHT

    def test_check_environment_not_implemented(self):
        # Instantiate the subclass and attempt to call the check_environment method
        movement = TestPlayerMovementWithoutImplementation(self.mock_player, self.mock_direction)
        with self.assertRaises(NotImplementedError):
            movement.check_environment(MagicMock())  # Call the method directly

    def test_draw_new_tile_not_implemented(self):
        # Instantiate the subclass and attempt to call the draw_new_tile method
        movement = TestPlayerMovementWithoutImplementation(self.mock_player, self.mock_direction)
        with self.assertRaises(NotImplementedError):
            movement.draw_new_tile()  # Call the method directly