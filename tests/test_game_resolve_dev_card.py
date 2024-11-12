import unittest
from unittest.mock import patch
from models.game import Game
from models.dev_cards import DevCards
from models.player import Player
from models.tiles import Tile
from enums.directions import Direction

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
