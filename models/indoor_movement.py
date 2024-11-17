from models.player_movement import PlayerMovement


class IndoorMovement(PlayerMovement):
    def check_environment(self, next_tile):
        """
        Checks and enforces movement restrictions
        when moving from indoor to outdoor.
        Only allows movement to 'Patio' if the player has the totem.
        """
        # Restriction for indoor to outdoor movement unless moving to Patio with totem
        if self._player.current_tile.environment == "Indoor" \
            and next_tile.environment == "Outdoor":
            if next_tile.name == "Patio" and self._player.has_totem:
                return True
            print("Cannot move from indoor to outdoor without a valid exit (e.g., Patio).")
            return False

        # Block specific exit if moving into the Dining Room
        if next_tile.name == "Dining Room":
            self._player.block_reserved_exit(next_tile)

        # Allow movement to other indoor tiles without restriction
        return next_tile.environment == "Indoor"

    def draw_new_tile(self):
        """Draws the next indoor tile if available, otherwise indicates no tile was drawn."""
        next_tile = self._player.get_next_indoor_tile()
        if next_tile:
            print(self._player.localization["p_tile_drew"].format(
                tile=next_tile.name)
                )
        else:
            print(self._player.localization["p_player_tile_no"])
        return next_tile
