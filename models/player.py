from enums.directions import Direction
from models.tiles import Tile
from models.indoor_movement import IndoorMovement
from models.outdoor_movement import OutdoorMovement 

class Player:
    def __init__(
        self, localization, indoor_tiles, outdoor_tiles, health=6, attack_points=1
    ):
        self.current_tile = None  # Holds the tile the player is currently on
        self.previous_tile = None  # Holds the previous tile the player was on
        self.position = (0, 0)  # Grabs the position of the player in the grid
        self.grid = {}
        self.indoor_tiles = indoor_tiles
        self.outdoor_tiles = outdoor_tiles
        self.health = health
        self.has_totem = False
        self.attack_points = attack_points
        self.items = []
        self.visited_tiles = []  # Tracks all the tiles visited by the player
        self.localization = localization
    

    def place_initial_tile(self):
        """Places the initial tile, which is the Foyer."""
        initial_tile = next(
            (tile for tile in self.indoor_tiles if tile.name == "Foyer"), None
        )
        if initial_tile:
            self.current_tile = initial_tile
            self.grid[self.position] = initial_tile
            self.indoor_tiles.remove(initial_tile)
            print(
                self.localization["p_on_tile_msg"].format(name=self.current_tile.name)
            )
            self.print_exits()
        else:
            print(self.localization["p_error_no_foyer"])

    # def move(self, direction):
    #     """
    #     Handles player movement. Checks for player position, rotates tile walls to connect
    #     with the current room, and checks for movement validity.
    #     """
    #     x, y = self.position  # Extracts current position coordinates
    #     new_position = {
    #         Direction.LEFT: (x - 1, y),
    #         Direction.UP: (x, y + 1),
    #         Direction.RIGHT: (x + 1, y),
    #         Direction.DOWN: (x, y - 1),
    #     }.get(direction)

    #     if new_position is None:
    #         print("Invalid direction provided.")
    #         return False

    #     # Check if moving to an existing tile in the grid
    #     if new_position in self.grid:
    #         next_tile = self.grid[new_position]
        
    #         if next_tile.name == "Dining Room":
    #             self.block_reserved_exit(next_tile)
                

    #         # Rotate tile to align exits
    #         opposite_index = Direction.opposite(direction).value
    #         for _ in range(4):
    #             if next_tile.walls[opposite_index] == 0:
    #                 break
    #             next_tile.rotate()

    #         if next_tile.walls[opposite_index] == 1:
    #             return False

    #         if (
    #             self.current_tile.environment == "Indoor" and
    #             next_tile.environment == "Outdoor"
    #         ):
    #             # Allow only if moving to "Patio" and player has the totem
    #             if next_tile.name == "Patio" and self.has_totem:
    #                 return True
    #             print("Cannot move from indoor to outdoor"
    #                 "without a valid exit (e.g., Patio).")
    #             return False
            
    #         # Restrict outdoor to indoor movement unless via Patio
    #         if (
    #             self.current_tile.environment == "Outdoor"
    #             and next_tile.environment == "Indoor"
    #             and self.current_tile.name != "Patio"
    #         ):
    #             return False

    #         self.previous_tile = self.current_tile
    #         self.current_tile = next_tile
    #         self.position = new_position  # Updates player position
    #         print(
    #             self.localization["p_player_moved_from_to"].format(
    #                 direction=direction.name.lower(),
    #                 current_tile=self.current_tile.name,
    #             )
    #         )
    #         self.print_exits()
    #         return True

    #     # Drawing a new tile
    #     if self.is_in_outdoor_area():
    #         next_tile = self.get_next_outdoor_tile()
    #     else:
    #         next_tile = self.get_next_indoor_tile()

    #     if not next_tile:
    #         print(self.localization["p_player_tile_no"])
    #         print(
    #             self.localization["p_player_moved_from_to"].format(
    #                 direction=direction.name.lower(),
    #                 current_tile=self.current_tile.name,
    #             )
    #         )
    #         return False

    #     print(self.localization["p_tile_drew"].format(tile=next_tile.name))

    #     self.grid[new_position] = next_tile
    #     self.previous_tile = self.current_tile
    #     self.current_tile = next_tile
    #     self.position = new_position
    #     print(
    #         self.localization["p_player_moved_from_to"].format(
    #             direction=direction.name.lower(), current_tile=self.current_tile.name
    #         )
    #     )
    #     self.print_exits()

    #     self.visited_tiles.append(self.current_tile)
    #     return True

    def move(self, direction):
        movement_class = IndoorMovement if self.current_tile.environment == "Indoor" else OutdoorMovement
        movement = movement_class(self, direction)
        return movement.move()

    def is_in_outdoor_area(self):
        """Check if the player is currently in an outdoor environment."""
        return (
            self.current_tile.name == "Patio"
            or self.current_tile.environment == "Outdoor"
        )

    def block_reserved_exit(self, tile):
        """Blocks a specific exit of the Dining Room to reserve for the Patio tile."""
        if tile.name == "Dining Room":
            print(f"Blocking north exit for Dining Room at position {self.position}.")
            north_index = Direction.UP.value  # Reserve the north exit for the Patio
            tile.walls[north_index] = 1  # Block the north exit


    def move_to_tile(self, tile):
        """Moves player to a specified explored tile."""
        self.previous_tile = self.current_tile
        self.current_tile = tile
        self.position = next(
            (pos for pos, t in self.grid.items() if t == tile), self.position
        )
        print(
            self.localization["p_moved_to_prev_tile"].format(
                current_tile=self.current_tile.name
            )
        )

    def get_next_indoor_tile(self):
        """Returns next indoor tile if available."""
        if self.indoor_tiles:
            return self.indoor_tiles.pop(0)
        return None

    def get_next_outdoor_tile(self):
        """Returns next outdoor tile if available."""
        if self.outdoor_tiles:
            return self.outdoor_tiles.pop(0)
        return None

    def print_exits(self):
        """Prints out the exits of the current tile."""
        exits = self.current_tile.get_exit_directions()
        exit_names = [
            direction.name.lower() for direction in exits
        ]  # Gets tile exits in name format
        print(
            self.localization["p_aval_exits"].format(
                current_tile=self.current_tile.name, exits=", ".join(exit_names)
            )
        )

    def get_move_direction(self):
        """Prompts the player for a move direction until a valid response is given."""
        exits = self.current_tile.get_exit_directions()
        while True:
            direction_input = input(
                self.localization["p_choose_dir_or_save"].format(
                    exits=", ".join([d.name.lower() for d in exits])
                )
            ).lower()
            if direction_input == "//save":
                return direction_input
            for direction in exits:
                if (
                    direction.name.lower() == direction_input
                ):  # Checks player's input against the exits of the current room
                    return direction
            print(self.localization["p_invalid_dir"])

    def modify_health(self, amount):
        """Modifies the player's health by a given amount."""
        self.health += amount
        self.health = max(self.health, 0)  # Health cannot go below zero
        print(self.localization["p_health_msg"].format(health=self.health))

    def modify_attack_points(self):
        """Updates and displays the player's total attack points based on the items they have collected."""
        total_attack_points = self.attack_points  # Start with the base attack points
        for item in self.items:
            for card in self.dev_card_list:
                if card.item == item:
                    total_attack_points += card.attack_points
                    break
        self.attack_points = total_attack_points

    def display_health(self):
        """Displays the player's current health."""
        print(f"Player's current health: {self.health}")

    def get_totem_status(self):
        """Returns whether the player has the totem."""
        return self.has_totem
