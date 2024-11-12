import random
from models.dev_cards import DevCards
from models.player import Player
from models.tiles import IndoorTile, OutdoorTile
from enums.directions import Direction
import json
from models.generic_event_strategy import GenericEventStrategy
from models.health_change_strategy import HealthChangeStrategy
from models.item_acquisition_strategy import ItemAcquisitionStrategy
from models.zombie_fight_strategy import ZombieFightStrategy


class Game:
    def __init__(self, localization):
        self.dev_card_list = []
        self.id_order = list(range(1, 10))
        self.time = 9  # time management
        self.out_of_dev_card = False
        self.player = None
        self.game_over = False
        self.chainsaw_count = 2
        self.localization = localization

    def load_dev_cards(self):
        with open("game_data.json") as d:
            dev_card_data = json.load(d)["devCard"]
            for dev_card in dev_card_data:
                dev_card = DevCards(
                    id=dev_card["id"],
                    activity_at_nine=dev_card["9:00"],
                    activity_at_ten=dev_card["10:00"],
                    activity_at_eleven=dev_card["11:00"],
                    item=dev_card["item"],
                    attack_points=dev_card["attack_points"],
                )
                self.dev_card_list.append(dev_card)

    def reset_id_order(self):
        self.id_order = list(range(1, 10))

    def reset_game(self):
        self.reset_id_order()
        self.time = 9
        self.game_over = False

    def shuffle_dev_card(self):
        random.shuffle(self.id_order)
        self.id_order.pop(0)
        self.id_order.pop(0)

    def get_card(self, prompt=None):
        while True:
            if len(self.id_order) == 0:
                self.check_last_card_in_dev()
            if prompt is None:
                prompt = self.localization["g_get_card_prompt_def"]
            response = input(prompt).lower()
            if response == "y":
                card_id = self.id_order.pop(0)
                for card in self.dev_card_list:
                    if card.id == card_id:
                        return card
            else:
                prompt = self.localization["g_get_card_prompt_must"]

    def check_last_card_in_dev(self):
        if len(self.id_order) == 0:
            print(self.localization["g_last_card"])
            self.reset_id_order()
            self.shuffle_dev_card()
            self.time += 1
            print(self.localization["g_time_updated"].format(time=self.time))

    # =============================================================

    # TARGET BLOCK OF CODE (BELOW)

    # =============================================================

    # def resolve_dev_card(self, card):
    #     """Function resolves development cards"""
    #     if self.time == 9:
    #         event = card.activity_at_nine
    #     elif self.time == 10:
    #         event = card.activity_at_ten
    #     elif self.time == 11:
    #         event = card.activity_at_eleven
    #     else:
    #         return
    #     print(event)

    #     if self.player.health <= 2:
    #         prompt = self.localization["g_cower_prompt_def"]
    #         while True:
    #             response = input(prompt).lower()
    #             if response == "cower":
    #                 self.cower()
    #                 return
    #             elif response == "continue":
    #                 return
    #             else:
    #                 prompt = self.localization["g_cower_prompt_must"]

    #     if "zombies" in event.lower():
    #         zombies = int(event.split()[0])
    #         prompt = self.localization["g_fight_zombie_prompt_def"].format(
    #             zombies=zombies
    #         )
    #         while True:
    #             response = input(prompt).lower()
    #             if response == "run":
    #                 self.run_away()
    #                 # Deduct 1 health for running away
    #                 self.player.modify_health(-1)
    #                 break
    #             elif response == "fight":
    #                 self.item_usage()
    #                 if not self.resolve_combat(zombies):
    #                     self.game_over = True
    #                 break
    #             else:
    #                 prompt = self.localization["g_fight_zombie_prompt_must"]

    #     elif "health" in event.lower():
    #         health_change = -1 if "-1" in event else +1
    #         self.player.modify_health(health_change)

    #     elif "item" in event.lower():
    #         prompt = self.localization["g_draw_item_prompt_def"]
    #         while True:
    #             response = input(prompt).lower()
    #             if response == "y":
    #                 the_card = self.get_card(
    #                     self.localization["g_get_card_prompt_item"]
    #                 )
    #                 print(f"The item is {the_card.item}")
    #                 self.player.items.append(the_card.item)
    #                 self.attack_points_update()
    #                 break
    #             elif response == "n":
    #                 print(self.localization["g_no_item"])
    #                 break
    #             else:
    #                 prompt = self.localization["g_draw_item_prompt_must"]
    #                 print(prompt)
    #     else:
    #         print(self.localization["g_print_event"].format(event=event))

    # =====================================================================
    # =====================================================================

    def resolve_dev_card(self, card):
        """Function resolves development cards based on the current time"""

        # Retrieve the event based no the current game time
        if self.time == 9:
            event = card.activity_at_nine
        elif self.time == 10:
            event = card.activity_at_ten
        elif self.time == 11:
            event = card.activity_at_eleven
        else:
            return # Exit if time is out of games event bounds
        
        # Determine the appropriate strategy based on the event
        if "zombies" in event.lower():
            strategy = ZombieFightStrategy(self)
        elif "health" in event.lower():
            strategy = HealthChangeStrategy(self)
        elif "item" in event.lower():
            strategy = ItemAcquisitionStrategy(self)
        else:
            strategy = GenericEventStrategy(self)

        strategy.execute(card, event)


    def run_away(self):
        """Allows player to run away to any previously explored tile"""
        if not self.player.visited_tiles:
            print(self.localization["g_no_tile_to_run_away"])
            return
        print(self.localization["g_run_away"])
        for i, tile in enumerate(self.player.visited_tiles):
            print(f"{i + 1}: {tile.name}")

        while True:
            try:
                choice = int(input(
                    self.localization["g_run_away_tile_prompt"])
                    ) - 1
                if 0 <= choice < len(self.player.visited_tiles):
                    self.player.move_to_tile(self.player.visited_tiles[choice])
                    print(
                        self.localization["g_run_away_to"].format(
                            name=self.player.current_tile.name
                        )
                    )
                    break
                else:
                    print(self.localization["g_run_away_error1"])
            except ValueError:
                print(self.localization["g_run_away_error2"])

    def cower(self):
        """Player can choose to cower and regain health,
            but loses time in the process"""
        print(self.localization["g_cowerd_msg"])
        self.player.modify_health(3)
        print(self.localization["g_cowerd_health_gained"])

        if self.id_order:
            self.id_order.pop(0)
            print(self.localization["g_cowered_time_passed"])
        else:
            self.check_last_card_in_dev()

    def resolve_combat(self, zombies):
        """This function shows how combat is resolved"""
        damage_received = max(0, zombies - self.player.attack_points)

        if "Candle" in self.player.items and "Oil" in self.player.items:
            print(self.localization["g_used_candle_oil"])
            self.player.items.pop(0)
            self.player.items.pop(0)
        elif "Candle" in self.player.items and "Gasoline" in self.player.items:
            print(self.localization["g_used_candle_gas"])
            self.player.items.pop(0)
            self.player.items.pop(0)
        elif damage_received > 0:
            print(self.localization["g_damage_recieved"]
                  .format(damage=damage_received))
            self.player.modify_health(-damage_received)
        else:
            print(self.localization["g_no_damage_recieved"])
        return True

    def special_room_item(self, prompt=None):
        """This function connects with handle_tile_feature
            to get an item from rooms with special."""
        if prompt is None:
            prompt = self.localization["g_draw_item_prompt_def"]
        while True:
            response = input(prompt).lower()
            if response == "y":
                card_id = self.id_order.pop(0)
                for card in self.dev_card_list:
                    if card.id == card_id:
                        print(
                            f"The item was: {card.item}, "
                            f"with attack points of {card.attack_points}"
                        )
                        self.player.items.append(card.item)
                        self.attack_points_update()
                        return card
            elif response == "n":
                print("Player chose not to get another card for an item.")
                return None
            else:
                response = "You have to answer (Type 'y or n')"

    def handle_tile_feature(self, tile):
        """Handles features of a given tile."""
        if self.player.current_tile.special == "+1 Health if end turn here.":
            self.player.modify_health(1)
            print(
                "\n"
                + self.localization["g_tile_special_recieved"].format(
                    name=self.player.current_tile.name,
                    special=self.player.current_tile.special,
                )
                + "\n"
            )
        elif self.player.current_tile.special == "May draw a new card to find an item.":
            self.get_card(self.localization["g_draw_item_prompt_def"])
            self.player.current_tile.special = None
            print(self.player.current_tile.special)

    def attack_points_update(self):
        """Updates and displays the player's total attack points and item details."""
        total_attack_points = 1
        if len(self.player.items) == 3:
            prompt = input(
                self.localization["g_replace_item"].format(
                    item0=self.player.items[0], item1=self.player.items[1]
                )
            )
            if prompt == "1":
                self.player.items.pop(0)
            elif prompt == "2":
                self.player.items.pop(1)
            else:
                self.player.items.pop(2)
                print(self.localization["g_no_item_replace"])

        for item in self.player.items:
            found = False
            for card in self.dev_card_list:
                if card.item == item:
                    total_attack_points += card.attack_points
                    found = True
                    if card.item == "Can of soda":
                        self.player.modify_health(2)
                    break
            if not found:
                print(self.localization["g_invalid_item_alarm"].format(item=item))

        self.player.attack_points = total_attack_points
        return self.player.attack_points

    def item_usage(self):
        """Check and use items in the player's inventory."""
        if "Gasoline" in self.player.items and "Chainsaw" in self.player.items:
            response = input(self.localization["g_combain_gas_chain_prompt"]).lower()
            if response == "y":
                self.chainsaw_count += 2
                self.player.items.remove("Gasoline")
                print(self.localization["g_combain_gas_chain_msg"])
                print(
                    self.localization["g_chainsaw_use_count"].format(
                        count=self.chainsaw_count
                    )
                )
                return
        elif "Candle" in self.player.items and "Oil" in self.player.items:
            print(f"{self.player.items[0]} and {self.player.items[1]}")
            response = input(self.localization["g_combain_candle_oil_prompt"]).lower()
            if response == "y":
                return
        elif "Candle" in self.player.items and "Gasoline" in self.player.items:
            print(f"{self.player.items[0]} and {self.player.items[1]}")
            response = input(self.localization["g_combain_candle_gas_prompt"]).lower()
            if response == "y":
                return
        if len(self.player.items) == 1:
            response = input(
                self.localization["g_use_item_prompt"].format(item=self.player.items[0])
            ).lower()
            if response == "y":
                if self.player.items[0] == "Chainsaw":
                    self.chainsaw_usage_count_handler()
                else:
                    print(f"{self.player.items[0]} is used.")
                    self.player.items.pop(0)
            else:
                print(self.localization["g_no_item_used"])
        elif len(self.player.items) == 2:
            response = input(
                self.localization["g_choose_use_item"].format(
                    item1=self.player.items[0], item2=self.player.items[1]
                )
            ).lower()
            if response == "1":
                if self.player.items[0] == "Chainsaw":
                    self.chainsaw_usage_count_handler()
                else:
                    print(f"{self.player.items[0]} is used.")
                    self.player.items.pop(0)
            elif response == "2":
                if self.player.items[1] == "Chainsaw":
                    self.chainsaw_usage_count_handler()
                else:
                    print(
                        self.localization["g_item_used"].format(
                            item=self.player.items[1]
                        )
                    )
                    self.player.items.pop(1)
            else:
                print(self.localization["g_no_item_used"])

    def chainsaw_usage_count_handler(self):
        """Added to resolve chainsaw use counts, so that it actually works"""
        self.chainsaw_count -= 1
        print(self.localization["g_chainsaw_used"].format(count=self.chainsaw_count))
        if self.chainsaw_count <= 0:
            print(self.localization["g_max_chainsaw_used"])
            self.player.items.remove("Chainsaw")

    def initialize_player(self, indoor_tiles, outdoor_tiles):
        """Initializes player with the given tiles and health"""
        self.player = Player(self.localization, indoor_tiles, outdoor_tiles, 6)
        self.player.place_initial_tile()

    def initialize_game(self, indoor_tiles, outdoor_tiles):
        """Initializes the game"""
        self.load_dev_cards()
        self.shuffle_dev_card()
        self.remove_and_store_patio_tile(outdoor_tiles)
        self.get_card()

    def remove_and_store_patio_tile(self, outdoor_tiles):
        """Removes and stores the patio tile for later use"""
        self.patio_tile = next(
            (tile for tile in outdoor_tiles if tile.name == "Patio"), None
        )
        if self.patio_tile:
            outdoor_tiles.remove(self.patio_tile)

    def place_patio_tile(self):
        """Places the patio tile within certain conditions"""
        if self.player.current_tile.name == "Dining Room" and self.player.has_totem:
            if any(tile.name == "Patio" for tile in self.player.outdoor_tiles):
                prompt = self.localization["g_place_patio_prompt"]
                while True:
                    place_patio = input(prompt).lower()
                    if place_patio == "y":
                        x, y = self.player.position
                        reserved_position = (x, y - 1)
                        if reserved_position not in self.player.grid:
                            patio_tile = next(
                                tile
                                for tile in self.player.outdoor_tiles
                                if tile.name == "Patio"
                            )
                            self.player.grid[reserved_position] = patio_tile
                            self.player.outdoor_tiles.remove(patio_tile)
                            self.player.current_tile.walls[Direction.UP.value] = 0
                            print(self.localization["g_placed_patio_msg"])
                            print(self.display_player_info())
                            break
                        else:
                            print(self.localization["g_patio_place_error_alarm"])
                    elif place_patio == "n":
                        print(self.localization["g_patio_no_placed"])
                        break
                    else:
                        prompt = self.localization["g_place_patio_prompt_must"]
            else:
                print(self.localization["g_tile_cant_outdoor"])

    def displaying_map(self):
        """Display a map of placed tiles"""
        the_grid = self.player.grid
        min_x = min(coord[0] for coord in the_grid.keys())
        max_x = max(coord[0] for coord in the_grid.keys())
        min_y = min(coord[1] for coord in the_grid.keys())
        max_y = max(coord[1] for coord in the_grid.keys())

        map_str = self.localization["g_map_title"]

        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                room = the_grid.get((x, y))
                if room is not None:
                    map_str += f"|{room.name:12}|"
                else:
                    map_str += " " * 14
            map_str += "\n"
        map_str += "---------------------------"
        return map_str

    def display_player_info(self):
        """
        Display player information.
        """
        output = self.localization["g_info_1"].format(
            time=self.time,
            health=self.player.health,
            attack_points=self.player.attack_points,
        )
        if self.player.current_tile is not None:
            output += self.localization["g_info_2"].format(
                current_tile=self.player.current_tile.name
            )
        if self.player.previous_tile is not None:
            output += self.localization["g_info_3"].format(
                previous_tile=self.player.previous_tile.name
            )
        if len(self.player.items) != 0:
            output += self.localization["g_info_4"].format(item=self.player.items)
        output += self.displaying_map()
        return output

    def check_dead_end(self):
        """Check if the player is at a dead end considering all reachable tiles and offer zombie doors option."""
        queue = [self.player.position]
        visited_positions = set(queue)

        while queue:
            current_position = queue.pop(0)
            current_tile = self.player.grid.get(current_position)

            if not current_tile:
                continue

            exits = current_tile.get_exit_directions()

            for direction in exits:
                new_position = self.calculate_new_position(current_position, direction)
                if new_position not in self.player.grid:
                    return

                if new_position not in visited_positions:
                    visited_positions.add(new_position)
                    queue.append(new_position)

        response = input(self.localization["g_deadend_prompt"]).lower()
        if response == "y":
            self.trigger_zombie_doors()
        else:
            print(self.localization["g_deadend_stay_msg"])

    def calculate_new_position(self, current_position, direction):
        """Calculate the new grid position based on the current position and direction of movement"""
        x, y = current_position
        if direction == Direction.LEFT:
            return x - 1, y
        elif direction == Direction.UP:
            return x, y - 1
        elif direction == Direction.RIGHT:
            return x + 1, y
        elif direction == Direction.DOWN:
            return x, y + 1
        return current_position

    def trigger_zombie_doors(self):
        """Allows zombie to break through the wall, opening a new exit and triggering combat"""
        prompt = self.localization["g_choose_wall_prompt"]
        while True:
            try:
                wall_choice = int(input(prompt)) - 1
                if 0 <= wall_choice <= 3:
                    if self.player.current_tile.walls[wall_choice] == 0:
                        print("There is already an exit there. Choose a different wall.")
                    else:
                        self.player.current_tile.walls[wall_choice] = 0
                        print(
                            self.localization["g_choose_wall_msg"].format(
                                dir=Direction(wall_choice).name.lower()
                            )
                        )
                        self.resolve_combat(3)
                        break
                else:
                    prompt = self.localization["g_invalid_choice"]
            except ValueError:
                prompt = self.localization["g_invalid_input"]

    def check_win_condition(self):
        """Checks if the player can win the game"""
        if self.player.current_tile.name == "Graveyard" and self.player.has_totem:
            prompt = input(self.localization["g_final_prompt1"]).lower()
            if prompt == "y":
                first_card = self.get_card(self.localization["g_bury_draw_1"])
                self.resolve_dev_card(first_card)

                if self.player.health > 0:
                    second_card = self.get_card(self.localization["g_bury_draw_2"])
                    self.resolve_dev_card(second_card)

                    if self.player.health > 0 and self.time < 12:
                        print(self.localization["g_win_msg"])
                        self.game_over = True
                    else:
                        print(self.localization["g_lose_msg1"])
                else:
                    print(self.localization["g_lose_msg2"])
            else:
                print(self.localization["g_choose_bury_no"])

    def save_game(self, filename="game_save.json"):
        """Save the current game state to a file."""
        game_state = {
            "time": self.time,
            "game_over": self.game_over,
            "id_order": self.id_order,
            "player": {
                "health": self.player.health,
                "attack_points": self.player.attack_points,
                "item": self.player.items,
                "current_tile": self.player.current_tile.name
                if self.player.current_tile
                else None,
                "previous_tile": self.player.previous_tile.name
                if self.player.previous_tile
                else None,
                "position": self.player.position,
                "has_totem": self.player.has_totem,
            },
            "grid": {(x, y): tile.name for (x, y), tile in self.player.grid.items()},
        }

        def convert_keys_to_strings(d):
            new_dict = {}
            for key, value in d.items():
                if isinstance(key, tuple):
                    key = str(key)
                if isinstance(value, dict):
                    value = convert_keys_to_strings(value)
                new_dict[key] = value
            return new_dict

        game_state = convert_keys_to_strings(game_state)

        with open("game_save.json", "w") as f:
            json.dump(game_state, f, indent=4)

        print(f"Game saved to {filename}")

    def handle_command(self, command):
        """Handle special game commands."""
        if command.strip().lower() == "//save":
            self.save_game()
            return True
        return False

    def start_game(self, indoor_tiles, outdoor_tiles):
        self.reset_game()
        self.load_dev_cards()
        self.shuffle_dev_card()
        self.initialize_player(indoor_tiles, outdoor_tiles)
        print(self.display_player_info())

        IndoorTile.shuffle_tiles(indoor_tiles)
        OutdoorTile.shuffle_tiles(outdoor_tiles)

        while not self.game_over:
            direction = self.player.get_move_direction()
            if direction == "//save":
                self.save_game()
            elif direction and direction != "//save":
                self.check_last_card_in_dev()
                if self.time > 11:
                    self.localization["g_lose_msg3"]
                    self.game_over = True
                    return None

                valid_move = self.player.move(direction)
                if not valid_move:
                    continue

                current_tile = self.player.current_tile
                self.handle_tile_feature(current_tile)
                self.check_dead_end()

                the_card = self.get_card()
                self.resolve_dev_card(the_card)
                print(self.display_player_info())

                if (
                    self.player.current_tile.name == "Evil Temple"
                    and not self.player.has_totem
                ):
                    the_card = self.get_card(self.localization["g_find_totem_prompt"])
                    self.resolve_dev_card(the_card)
                    if self.player.health > 0:
                        self.player.has_totem = True
                        print(self.localization["g_totem_aqquired_msg"])

                self.place_patio_tile()
                self.check_win_condition()

                if self.player.health <= 0:
                    print(self.localization["g_lose_msg4"])
                    self.game_over = True
                    return None

            else:
                break
