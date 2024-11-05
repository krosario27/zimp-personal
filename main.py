from models.tiles import Tile
from models.game import Game
from enums.directions import Direction
import json


def load_localization(language_code):
    """Load the localization data based on the specified language."""
    with open("localization.json", "r", encoding='utf-8') as f:
        localization_data = json.load(f)
    return localization_data.get(language_code, None)

def get_langauge_code():
    """Keep asking user for a valid langauge code until a valid one is provided"""
    while True:
        language_code = input("\nChoose your langauge code (English - 'en', Spanish - 'es', Simplified Chinese - 'zh', Japanese - 'jp'): ").lower()
        localization = load_localization(language_code)

        if localization:
            return localization
        else:
            print(f"Invalid language code '{language_code}'. Please try again.")


def main():
    while True:
        choice = input("Choose an option: [start], [quit], [save], [load]: ").lower()
        choice = input("\nWelocme to Zombie in my pocket [start, quit]: ").lower()
        if choice == "start":
            # langauge option
            localization = get_langauge_code()
            # Create a Game instance
            game = Game(localization)
            # Initialize game with default or empty tile lists
            indoor_tiles = []
            outdoor_tiles = []
            # Load tiles from the file
            indoor_tiles, outdoor_tiles = Tile.load_tiles("game_data.json")
            # Start a new game with loaded tiles
            game.start_game(indoor_tiles, outdoor_tiles)
        elif choice == "quit":
            # Exit the game loop
            print("Exiting the game. Goodbye!")
            break
        else:
            # Handle invalid input
            print("Invalid choice. Please select 'start' or 'quit'.")

if __name__ == "__main__":
    main()