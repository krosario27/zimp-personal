from models.event_strategy import DevCardEventStrategy

class ZombieFightStrategy(DevCardEventStrategy):
    def execute(self, card, event):
        zombies = int(event.split()[0])
        prompt = self.game.localization["g_fight_zombie_prompt_def"].format(
            zombies=zombies
        )

        while True:
            response = input(prompt).lower()
            if response == "run":
                self.game.run_away()
                self.game.player.modify_health(-1)
                break
            elif response == "fight":
                self.game.item_usage()
                if not self.game.resolve_combat(zombies):
                    self.game.game_over = True
                break
            else:
                prompt = self.game.localization["g_fight_zombie_prompt_must"]