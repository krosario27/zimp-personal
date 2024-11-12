from models.player_movement import PlayerMovement


class OutdoorMovement(PlayerMovement):
    def check_environment(self, next_tile):
        # Allow movement to outdoor or patio tiles, restrict others
        if next_tile.environment == "Outdoor":
            return True
        
        if self.player.current_tile.name == "Patio" \
            and next_tile.environment == "Indoor":
            return True
        
        print("Movement from outdoor to indoor"
              "not allowed except through Patio.")
        return False

    def draw_new_tile(self):
        # Draw the next outdoor tile
        next_tile = self.player.get_next_outdoor_tile()
        if next_tile:
            print(self.player.localization["p_tile_drew"]
                  .format(tile=next_tile.name))
        else:
            print(self.player.localization["p_player_tile_no"])
        return next_tile
