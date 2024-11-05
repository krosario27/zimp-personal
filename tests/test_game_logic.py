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
        self.player.grid[(1, 0)] = Tile(
            1,
            "Bathroom",
            [1, 0, 1, 1],
            "None"
        )
        self.assertTrue(self.player.move(Direction.RIGHT))

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
        self.player.grid[(0, 0)] = Tile(
            6,
            "Dining Room",
            [0, 0, 0, 0],
            "None"
        )
        self.player.current_tile = self.player.grid[(0, 0)]
        self.player.has_totem = True

        self.player.grid[(0, -1)] = Tile(
            5,
            "Garage",
            [0, 1, 1, 0],
            "None"
        )
        self.assertFalse(self.player.move(Direction.DOWN))

        self.player.grid[(0, 1)] = Tile(
            6,
            "Patio",
            [1, 0, 0, 0],
            "None"
        )
        self.assertTrue(self.player.move(Direction.DOWN))
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


class TestGameResolveDevCard(unittest.TestCase):
    def setUp(self):
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
            "g_cower_prompt_def": "You are terrified. Cower or continue?",
            "g_cower_prompt_must": "You must choose to cower or continue.",
            "g_fight_zombie_prompt_must": "You must choose to fight or run.",
            "g_draw_item_prompt_must": (
                "Please choose a valid option! "
                "Would you like to draw another dev "
                "card to retrieve an item? (Type 'y' for yes, 'n' for no)"
            ),
            "g_no_item": "You chose not to draw an item."
        }
        self.game = Game(self.localization)
        self.game.load_dev_cards()
        self.player = Player(self.localization, [], [])
        self.game.player = self.player

    def test_draw_item_invalid_input(self):
        card = DevCards(
            5,
            "ITEM",
            "5 Zombies.",
            "Your soul isn't wanted here. -1 HEALTH",
            "Grisly Femur",
            1
        )
        self.game.time = 9

        with patch('builtins.input', side_effect=['invalid', 'n']), \
                patch('builtins.print') as mock_print:
            self.game.resolve_dev_card(card)

            mock_print.assert_any_call(
                self.localization["g_draw_item_prompt_must"]
                )
            mock_print.assert_any_call(self.localization["g_no_item"])

    def test_resolve_dev_card_invalid_time(self):
        card = DevCards(
            1,
            "You try hard not to wet yourself.",
            "ITEM",
            "6 Zombies",
            "Oil",
            0
        )
        self.game.time = 12

        with patch('builtins.print') as mock_print:
            self.game.resolve_dev_card(card)

        mock_print.assert_not_called()

    def test_resolve_dev_card_cower(self):
        card = DevCards(
            1,
            "You try hard not to wet yourself.",
            "ITEM",
            "6 Zombies",
            "Oil",
            0
        )
        self.game.time = 9
        self.player.health = 2

        with patch('builtins.input', side_effect=['cower']), \
                patch.object(self.game, 'cower') as mock_cower:
            self.game.resolve_dev_card(card)

        mock_cower.assert_called_once()

    def test_resolve_dev_card_invalid_then_valid_response(self):
        card = DevCards(
            1,
            "You try hard not to wet yourself.",
            "ITEM",
            "6 Zombies",
            "Oil",
            0
        )
        self.game.time = 9
        self.player.health = 2

        with patch('builtins.input', side_effect=['invalid', 'cower']), \
                patch.object(self.game, 'cower') as mock_cower:
            self.game.resolve_dev_card(card)

        mock_cower.assert_called_once()

    def test_resolve_dev_card_continue(self):
        card = DevCards(
            1,
            "You try hard not to wet yourself.",
            "ITEM",
            "6 Zombies",
            "Oil",
            0
        )
        self.game.time = 9
        self.player.health = 2

        with patch('builtins.input', side_effect=['continue']), \
                patch.object(self.game, 'cower') as mock_cower:
            self.game.resolve_dev_card(card)

        mock_cower.assert_not_called()

    def test_resolve_fight_event_with_invalid_input(self):
        card = DevCards(
            7,
            "3 Zombies",
            "You hear terrible screams",
            "5 Zombies",
            "Chainsaw",
            3
        )
        self.game.time = 9
        self.player.health = 6

        with patch('builtins.input', side_effect=['invalid', 'fight']), \
                patch.object(self.game, 'item_usage') as mock_item_usage, \
                patch.object(self.game, 'resolve_combat', return_value=True) \
                as mock_resolve_combat:
            self.game.resolve_dev_card(card)

        mock_item_usage.assert_called_once()
        mock_resolve_combat.assert_called_once_with(3)
        self.assertFalse(self.game.game_over)

    def test_resolve_fight_event_game_over(self):
        card = DevCards(
            7,
            "3 Zombies",
            "You hear terrible screams",
            "5 Zombies",
            "Chainsaw",
            3
        )
        self.game.time = 9
        self.player.health = 6

        with patch('builtins.input', side_effect=['fight']), \
                patch.object(self.game, 'item_usage') as mock_item_usage, \
                patch.object(self.game, 'resolve_combat', return_value=False) \
                as mock_resolve_combat:
            self.game.resolve_dev_card(card)

        mock_item_usage.assert_called_once()
        mock_resolve_combat.assert_called_once_with(3)
        self.assertTrue(self.game.game_over)

    def test_resolve_event_at_ten(self):
        card = DevCards(
            2,
            "4 Zombies",
            "You sense your impending doom. -1 HEALTH",
            "ITEM",
            "Gasoline",
            0
        )
        self.game.time = 10
        self.game.resolve_dev_card(card)
        self.assertEqual(self.player.health, 5)

    def test_resolve_event_at_eleven(self):
        card = DevCards(
            3,
            "ITEM",
            "4 Zombies",
            "Something icky in your mouth. -1 HEALTH",
            "Board with Nails",
            1
        )
        self.game.time = 11

        with patch('builtins.input', side_effect=['y']):
            self.game.resolve_dev_card(card)

        self.assertEqual(self.player.health, 5)

    def test_resolve_zombie_event(self):
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
        card = DevCards(
            8,
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
        initial_card = DevCards(
            3,
            "ITEM",
            "4 Zombies",
            "Something icky in your mouth. -1 HEALTH",
            "Board with Nails",
            1
        )
        self.game.time = 9
        next_card = DevCards(
            2,
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

    def test_draw_item_declined(self):
        card = DevCards(
            5,
            "ITEM",
            "5 Zombies.",
            "Your soul isn't wanted here. -1 HEALTH",
            "Grisly Femur",
            1
        )
        self.game.time = 9

        with patch('builtins.input', return_value='n'), \
                patch('builtins.print') as mock_print:
            self.game.resolve_dev_card(card)

        mock_print.assert_any_call(self.localization["g_no_item"])

    def test_print_event(self):
        card = DevCards(
            1,
            "You try hard not to wet yourself.",
            "ITEM",
            "6 Zombies",
            "Oil",
            0
        )
        self.game.time = 9

        with patch('builtins.print') as mock_print:
            self.game.resolve_dev_card(card)

        mock_print.assert_any_call(
            self.localization["g_print_event"]
            .format(event="You try hard not to wet yourself.")
            )


if __name__ == '__main__':
    unittest.main()
