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
            return
        cast = cast_in_fight[self.abilityGameID]
        if cast.is_restricted(player=player, fight=player_fight):
            kw = {
                "type": cast.invalid_reason,
            }
            if cast.type == "spell":
                kw["spell_id"] = cast.spell_id
                kw["suggested_spell_id"] = cast.suggested_spell_id
            else:
                raise Exception(
                    f"unhandled type for cast_in_fight restriction: {cast.type}"
                )
            player_fight.add_remark(**kw)
