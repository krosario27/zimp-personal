from models.event_strategy import DevCardEventStrategy


class GenericEventStrategy(DevCardEventStrategy):
    def execute(self, card, event):
        print(self.game.localization["g_print_event"].format(event=event))