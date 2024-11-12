from models.event_strategy import DevCardEventStrategy

class ItemAcquisitionStrategy(DevCardEventStrategy):
    def execute(self, card, event):
        prompt = self.game.localization["g_draw_item_prompt_def"]
        while True:
            response = input(prompt).lower()
            if response == "y":
                the_card = self.game.get_card(self.game.localization["g_get_card_prompt_item"])
                print(f"The item is {the_card.item}")
                self.game.player.items.append(the_card.item)
                self.game.attack_points_update()
                break
            elif response == "n":
                print(self.game.localization["g_no_item"])
                break
            else:
                prompt = self.game.localization["g_draw_item_prompt_must"]
                print(prompt)