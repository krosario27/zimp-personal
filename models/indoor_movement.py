from models.player_movement import PlayerMovement


class IndoorMovement(PlayerMovement):
    def check_environment(self, next_tile):
        # Check if moving into the Dining Room to block the reserved exit
        if next_tile.name == "Dining Room":
            self.player.block_reserved_exit(next_tile)

        # Enforce restriction: Only allow
        # specific outdoor tiles (e.g., Patio) with the totem
        if (
            self.player.current_tile.environment == "Indoor" and
            next_tile.environment == "Outdoor"
        ):
            # Allow only if moving to "Patio" and player has the totem
            if next_tile.name == "Patio" and self.player.has_totem:
                return True
            print("Cannot move from indoor to outdoor"
                  "without a valid exit (e.g., Patio).")
            return False

        # Allow movement to other indoor tiles freely
        if next_tile.environment == "Indoor":
            return True

        print("Movement from indoor to outdoor is not allowed without totem.")
        return False

    def draw_new_tile(self):
        next_tile = self.player.get_next_indoor_tile()
        if next_tile:
            print(self.player.localization["p_tile_drew"]
                  .format(tile=next_tile.name))
        else:
            print(self.player.localization["p_player_tile_no"])
        return next_tile
