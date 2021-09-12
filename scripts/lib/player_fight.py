from .base import Base
from .remark import Remark
from lib.data.consumables import consumables


class PlayerFight(Base):
    def __init__(self, name, player):
        super().__init__(
            {
                "name": name,
                "auras": {},
                "remarks": [],
                "talents": [],
                "casts": {},
                "player": player,
            }
        )

    def as_json(self):
        return {k: v for (k, v) in self.__dict__.items() if k not in ("player",)}

    def looks_like_enhancement_shaman(self):
        return (
            self.talents[1]["id"] > self.talents[0]["id"]
            and self.talents[1]["id"] > self.talents[2]["id"]
        )

    def looks_like_retribution_paladin(self):
        return (
            self.talents[2]["id"] > self.talents[0]["id"]
            and self.talents[2]["id"] > self.talents[1]["id"]
        )

    def add_remark(self, type, **kwargs):
        d = {"type": type}
        d.update(kwargs)
        self.remarks.append(Remark(d))

    def check_consumables(self):
        if self.name == "Chess Event":
            # nothing wrong with having no consumables during chess event
            return
        missing = {"battle_elixir", "guardian_elixir", "food"}
        invalid = set()
        for aura in self.auras.values():
            consumable = consumables.get(aura["ability"])
            if not consumable:
                continue
            if consumable.is_battle_elixir():
                missing.remove("battle_elixir")
                if consumable.is_restricted(player=self.player, fight=self):
                    invalid.add(("battle_elixir", consumable.id))
            if consumable.is_guardian_elixir():
                missing.remove("guardian_elixir")
                if consumable.is_restricted(player=self.player, fight=self):
                    invalid.add(("guardian_elixir", consumable.id))
            if consumable.is_food():
                missing.remove("food")
                if consumable.is_restricted(player=self.player, fight=self):
                    invalid.add(("food", consumable.id))
        for missing_consumable in missing:
            self.add_remark(
                type=f"missing_{missing_consumable}",
            )
        for invalid_consumable in invalid:
            self.add_remark(
                type=f"invalid_{invalid_consumable[0]}",
                wowhead_attr=f"domain=fr.tbc&spell={invalid_consumable[1]}",
            )
