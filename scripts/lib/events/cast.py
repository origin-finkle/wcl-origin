import logging

from .event import Event
from lib.data.cast_in_fight import cast_in_fight


class Cast(Event):
    def _process(self, player, player_fight):
        player_fight.casts.setdefault(self.abilityGameID, 0)
        player_fight.casts[self.abilityGameID] += 1
        if self.abilityGameID not in cast_in_fight:
            logging.getLogger("default").debug(
                f"missing spell {self.abilityGameID} in cast_in_fight configuration"
            )
