import unittest
import sys
import os

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from tests.test_player_move import TestPlayerMove
from tests.test_game_resolve_dev_card import TestGameResolveDevCard


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPlayerMove))
    suite.addTest(unittest.makeSuite(TestGameResolveDevCard))
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
