import unittest
from unittest.mock import patch
from models.game import Game
from models.dev_cards import DevCards
from models.player import Player
from models.tiles import Tile
from enums.directions import Direction


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
                6,
                "Patio",
                [1, 0, 0, 0],
                "None"
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
        self.player.has_totem = True

        # Place Garage tile at (0, -1), an outdoor environment directly below the Dining Room
        self.player.grid[(0, -1)] = Tile(
            5,
            "Garage",
            [0, 1, 1, 0],  # Specific wall configuration
            "None",
            environment="Outdoor"
        )
        # Attempt to move down and check if it's correctly blocked
        self.assertFalse(self.player.move(Direction.DOWN))

        # Place Patio tile at (0, 1), an outdoor environment directly above the Dining Room
        self.player.grid[(0, 1)] = Tile(
            6,
            "Patio",
            [1, 0, 0, 0],  # Specific wall configuration
            "None",
            environment="Outdoor"
        )
        # Move down to Patio (should be allowed)
        self.assertTrue(self.player.move(Direction.DOWN))

        # Attempt to move further DOWN from Patio
        self.assertTrue(self.player.move(Direction.DOWN))


    def test_move_outdoor_to_indoor_requires_patio(self):
        self.player.grid[(0, 0)] = Tile(
            5,
            "Garage",
            [0, 1, 1, 0],
            "None",
            environment="Outdoor"
        )
        self.player.current_tile = self.player.grid[(0, 0)]

        self.player.grid[(-1, 0)] = Tile(
            6,
            "Dining Room",
            [0, 0, 0, 0],
            "None",
            environment="Indoor"
        )
        moved = self.player.move(Direction.LEFT)

        print(
            f"Current tile: {self.player.current_tile.name}, "
            f"Environment: {self.player.current_tile.environment}"
        )
        print(
            f"Next tile: {self.player.grid[(-1, 0)].name}, "
            f"Environment: {self.player.grid[(-1, 0)].environment}"
        )
        print(f"Move result: {moved}")

        self.assertFalse(moved)

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

        print(f"Walls before blocking: {dining_room_tile.walls}")

        self.player.block_reserved_exit(dining_room_tile)

        print(f"Walls after blocking: {dining_room_tile.walls}")

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