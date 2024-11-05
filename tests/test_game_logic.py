import unittest
from unittest.mock import patch
from models.game import Game
from models.dev_cards import DevCards
from models.player import Player
from models.tiles import Tile
from enums.directions import Direction


class TestPlayerMove(unittest.TestCase):
    def setUp(self):
        # Setup mock localization and initial player state
        self.localization = {
            "p_on_tile_msg": "Player is on {name}.",
            "p_player_moved_from_to": "Moved {direction} to {current_tile}.",
            "p_player_tile_no": "No new tile drawn.",
            "p_aval_exits": "Available exits from {current_tile}: {exits}.",
            "p_error_no_foyer": "No foyer tile found.",
            "p_tile_drew": "You drew the {tile} tile.",
        }
        self.indoor_tiles = [Tile(8, "Foyer", [1, 0, 1, 1], "None")]
        self.outdoor_tiles = [
            Tile(6, "Patio", [1, 0, 0, 0], "None"),
            Tile(5, "Garage", [0, 1, 1, 0], "None"),
        ]
        self.player = Player(
            self.localization, self.indoor_tiles, self.outdoor_tiles
            )
        self.player.place_initial_tile()

    def test_move_valid(self):
        self.player.grid[(1, 0)] = Tile(1, "Bathroom", [1, 0, 1, 1], "None")
        self.assertTrue(self.player.move(Direction.RIGHT))

    def test_moved_blocked_wall(self):
        self.player.grid[(1, 0)] = Tile(
            1, "Blocked Room", [1, 1, 1, 1], "None"
            )
        self.player.current_tile = self.player.grid[(0, 0)]
        self.assertFalse(self.player.move(Direction.RIGHT))

    def test_move_invalid_direction(self):
        self.assertFalse(self.player.move(None))

    def test_move_indoor_to_outdoor_requires_totem(self):
        self.player.grid[(0, 0)] = Tile(6, "Dining Room", [0, 0, 0, 0], "None")
        self.player.current_tile = self.player.grid[(0, 0)]
        self.player.has_totem = True

        # Attempt to move directly to Garage (outdoor) should fail
        self.player.grid[(0, -1)] = Tile(5, "Garage", [0, 1, 1, 0], "None")
        self.assertFalse(self.player.move(Direction.DOWN))

        # Place Patio in between Dining Room and Garage
        self.player.grid[(0, 1)] = Tile(6, "Patio", [1, 0, 0, 0], "None")
        self.assertTrue(self.player.move(Direction.DOWN))  # Move to Patio
        self.assertTrue(self.player.move(Direction.DOWN))  # Move to Garage

    def test_move_outdoor_to_indoor_requires_patio(self):
        self.player.grid[(0, 0)] = Tile(6, "Patio", [1, 0, 0, 0], "None")
        self.player.current_tile = self.player.grid[(0, 0)]

        # Move to an indoor tile (Foyer) should be allowed
        self.player.grid[(0, 1)] = Tile(8, "Foyer", [1, 0, 1, 1], "None")
        self.assertTrue(self.player.move(Direction.DOWN))

        # Attempt to move from Garage (outdoor)
        # to an indoor tile directly should be blocked
        self.player.grid[(1, 0)] = Tile(5, "Garage", [0, 1, 1, 0], "None")
        self.player.current_tile = self.player.grid[(1, 0)]
        self.assertFalse(self.player.move(Direction.RIGHT))


class TestGameResolveDevCard(unittest.TestCase):
    def setUp(self):
        # Mock localization and player setup
        self.localization = {
            "g_fight_zombie_prompt_def": "Fight or run? {zombies} zombies.",
            "g_damage_recieved": "You received {damage} damage.",
            "g_no_damage_recieved": "No damage received.",
            "g_draw_item_prompt_def": "Draw an item?",
            "g_get_card_prompt_def": "Draw the next card?",
            "g_print_event": "Event: {event}.",
            "p_health_msg": "Player's health: {health}.",
            "g_get_card_prompt_item":
                "Would you like to draw another card for an item?",
            "g_no_tile_to_run_away": "There are no tiles to run away to.",
        }
        self.game = Game(self.localization)
        self.game.load_dev_cards()
        self.player = Player(self.localization, [], [])
        self.game.player = self.player

    def test_resolve_zombie_event(self):
        # Simulate resolving a zombie event at 9:00
        card = DevCards(
            7,
            "3 Zombies",
            "You hear terrible screams",
            "5 Zombies",
            "Chainsaw",
            3
            )
        self.game.time = 9
        with patch('builtins.input', return_value='run'):
            self.game.resolve_dev_card(card)
        self.assertEqual(self.player.health, 5)

    def test_resolve_health_gain_event(self):
        card = DevCards(8,
                        "Candybar in your pocket. +1 HEALTH",
                        "ITEM",
                        "4 Zombies",
                        "Can of soda",
                        0
                        )
        self.game.time = 9
        self.game.resolve_dev_card(card)
        self.assertEqual(self.player.health, 7)

    def test_resolve_item_acquisition(self):
        initial_card = DevCards(3,
                                "ITEM",
                                "4 Zombies",
                                "Something icky in your mouth. -1 HEALTH",
                                "Board with Nails",
                                1
                                )
        self.game.time = 9

        # Prepare the next card in the deck for drawing,
        # which actually provides the item
        next_card = DevCards(2,
                             "4 Zombies",
                             "You sense your impending doom. -1 HEALTH",
                             "ITEM",
                             "Gasoline",
                             0
                             )
        self.game.dev_card_list = [next_card]

        with patch('builtins.input', side_effect=['y', 'y', 'y']):
            self.game.resolve_dev_card(initial_card)

        self.assertIn("Gasoline", self.player.items)
        self.assertEqual(self.player.attack_points, 1)


if __name__ == '__main__':
    unittest.main()
