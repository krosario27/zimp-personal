from enums.directions import Direction
import json
import random


class Tile:
    def __init__(self, tile_id, name, walls, special, environment=None):
        self.tile_id = tile_id
        self.name = name
        self.walls = walls
        self.special = special
        self.environment = environment

    def get_exit_directions(self):
        """Returns directions which have exits."""
        return [Direction(i) for i, wall in enumerate(self.walls) if wall == 0]

    def rotate(self):
        """Rotates walls clockwise."""
        if not self.walls:
            raise ValueError("Walls list is empty.")
        self.walls = self.walls[-1:] + self.walls[:-1]

    @classmethod
    def load_tiles(cls, file_path):
        """Returns tiles from JSON and populates indoor and outdoor tiles."""
        if not file_path.endswith(".json"):
            raise ValueError("The file must be a JSON file.")

        try:
            with open(file_path, "r") as f:
                data = json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            raise RuntimeError(f"Error reading JSON file: {e}")

        indoor_tiles = []
        outdoor_tiles = []

        try:
            # Populate outdoor tiles
            for tile_data in data["tilesCard"][0]["outDoor"]:
                outdoor_tiles.append(
                    OutdoorTile(
                        tile_id=tile_data["id"],
                        name=tile_data["name"],
                        walls=tile_data["wall"],
                        special=tile_data["special"],
                    )
                )

            # Populate indoor tiles
            for tile_data in data["tilesCard"][1]["inDoor"]:
                indoor_tiles.append(
                    IndoorTile(
                        tile_id=tile_data["id"],
                        name=tile_data["name"],
                        walls=tile_data["wall"],
                        special=tile_data["special"],
                    )
                )
        except KeyError as e:
            raise ValueError(f"Missing key in JSON data: {e}")

        return indoor_tiles, outdoor_tiles


class IndoorTile(Tile):
    def __init__(self, tile_id, name, walls, special):
        super().__init__(tile_id, name, walls, special, environment="Indoor")

    @staticmethod
    def shuffle_tiles(tiles):
        """Shuffles a list of indoor tiles and removes 'Foyer' tile."""
        if not isinstance(tiles, list):
            raise TypeError("Expected a list of tiles.")

        if not all(isinstance(tile, Tile) for tile in tiles):
            raise TypeError("All items in the list must be instances of Tile.")

        random.shuffle(tiles)
        # Remove 'Foyer' tile from the shuffled tiles
        tiles[:] = [tile for tile in tiles if tile.name != "Foyer"]


class OutdoorTile(Tile):
    def __init__(self, tile_id, name, walls, special):
        super().__init__(tile_id, name, walls, special, environment="Outdoor")

    def describe_environment(self):
        """Method specific to outdoor tiles."""
        if self.environment:
            print(f"Environment in {self.name}: {self.environment}")
        else:
            print(f"{self.name} has a standard outdoor environment.")

    @staticmethod
    def shuffle_tiles(tiles):
        """Shuffles a list of outdoor tiles."""
        if not isinstance(tiles, list):
            raise TypeError("Expected a list of tiles.")

        if not all(isinstance(tile, Tile) for tile in tiles):
            raise TypeError("All items in the list must be instances of Tile.")

        random.shuffle(tiles)
