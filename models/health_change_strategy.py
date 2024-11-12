from models.event_strategy import DevCardEventStrategy

class HealthChangeStrategy(DevCardEventStrategy):
    def execute(self, card, event):
        health_change = -1 if "-1" in event else +1
        self.game.player.modify_health(health_change)