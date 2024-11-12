from models.event_strategy import DevCardEventStrategy

class LowHealthStrategy(DevCardEventStrategy):
    def execute(self, card, event):
        prompt = self.game.localization["g_cower_prompt_def"]
        while True:
            response = input(prompt).lower()
            if response == "cower":
                self.game.cower()
                return  # Stop further processing as the player has chosen to cower
            elif response == "continue":
                return  # Stop processing without taking any action
            else:
                prompt = self.game.localization["g_cower_prompt_must"]
