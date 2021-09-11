from .event import Event


class Cast(Event):
    def _process(self, player, player_fight):
        player_fight.setdefault("casts", {}).setdefault(self.abilityGameID, 0)
        player_fight["casts"][self.abilityGameID] += 1
