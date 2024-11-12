from models.player_movement import PlayerMovement


class OutdoorMovement(PlayerMovement):
    def check_environment(self, next_tile):
        """
        Allows movement between outdoor tiles, and allows movement
        to indoor tiles only through 'Patio'.
        """
        # Allow movement between outdoor tiles without restriction
        if next_tile.environment == "Outdoor":
            return True

        # Restriction: Allow indoor access only from Patio
        if self._player.current_tile.name == "Patio" and next_tile.environment == "Indoor":
            return True

        print("Movement from outdoor to indoor not allowed except through Patio.")
        return False

    def draw_new_tile(self):
        """Draws the next outdoor tile if available, otherwise indicates no tile was drawn."""
        next_tile = self._player.get_next_outdoor_tile()
        if next_tile:
            print(self._player.localization["p_tile_drew"].format(tile=next_tile.name))
        else:
            print(self._player.localization["p_player_tile_no"])
        return next_tile