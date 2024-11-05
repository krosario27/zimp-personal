import json
import random

class Room:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = None
        self.load_json()

    def load_json(self):
        """Loads room data from a JSON file."""
        try:
            with open(self.file_path, "r") as file:
                self.data = json.load(file)
        except FileNotFoundError:
            print(f"Error: File '{self.file_path}' not found.")
        except json.JSONDecodeError:
            print(f"Error: File '{self.file_path}' is not a valid JSON file.")

    def shuffle_outdoor(self):
        """Shuffles outdoor room data and returns it."""
        outdoor_room_data = self.data.get("tilesCard", [{}])[0].get("outDoor", [])
        random.shuffle(outdoor_room_data)
        return outdoor_room_data

    def shuffle_indoor(self):
        """Shuffles indoor room data and returns a status message."""
        indoor_room_data = self.data.get("tilesCard", [{}])[1].get("inDoor", [])
        random.shuffle(indoor_room_data)
        return "Shuffling Cards"

    def get_outdoor(self):
        """Returns a random outdoor room and removes it from the list."""
        outdoor_room_data = self.shuffle_outdoor()
        if outdoor_room_data:
            random_outdoor_room = random.choice(outdoor_room_data)
            outdoor_room_data.remove(random_outdoor_room)
            return random_outdoor_room
        return None

    def get_indoor(self):
        """Returns a random indoor room."""
        indoor_room_data = self.data.get("tilesCard", [{}])[1].get("inDoor", [])
        if indoor_room_data:
            return random.choice(indoor_room_data)
        return None

    def indoor_to_outdoor(self):
        """Returns either a random indoor or outdoor room based on availability."""
        outdoor_room_data = self.data.get("tilesCard", [{}])[1].get("inDoor", [])
        if len(outdoor_room_data) == 0:
            return self.get_indoor()
        else:
            return self.get_outdoor()

    def __str__(self):
        """Returns a string representation of the Room class."""
        return f"Room file path: {self.file_path}"

if __name__ == "__main__":
    handler = Room("gameData.json")

    print(handler.get_outdoor())