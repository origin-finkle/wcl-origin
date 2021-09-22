from .base import Base
from .talents import Talents
from .remark import Remark
from lib.data.consumables import consumables
from lib.data.cast_in_fight import cast_in_fight
from lib.data.wowhead import get_wowhead_data


class PlayerFight(Base):
    def __init__(self, name, player):
        super().__init__(
            {
                "name": name,
                "auras": {},
                "remarks": [],
                "talents": None,
                "casts": {},
                "player": player,
                "gear": [],
            }
        )

    def as_json(self):
        return {k: v for (k, v) in self.__dict__.items() if k not in ("player",)}

    def add_remark(self, type, **kwargs):
        d = {"type": type}
        d.update(kwargs)
        self.remarks.append(Remark(d))

    def post_process(self):
        self.check_consumables()
        self.check_casts()
        self.check_talents()
        self.check_gear()

    def is_(self, x):
        return self.talents.is_(x)

    def check_gear(self):
        if not self.gear:
            return
        slots = {
            "Tête": 1,
            "Cou": 1,
            "Épaule": 1,
            "Torse": 1,
            "Taille": 1,
            "Jambes": 1,
            "Pieds": 1,
            "Poignets": 1,
            "Mains": 1,
            "Doigt": 2,
            "Bijou": 2,
            "Dos": 1,
            "Main droite": 1,
            "Main gauche": 1,
            "À distance": 1,
            "À une main": 1,
            "Relique": 1,
            "Deux mains": 1,
            "Tenu(e) en main gauche": 1,
        }
        for gear in self.gear:
            wowhead_data = get_wowhead_data(item_id=gear.id)
            if wowhead_data["slot"] in ("Tabard",):
                continue
            slots[wowhead_data["slot"]] -= 1
            if slots[wowhead_data["slot"]] == 0:
                del wowhead_data["slot"]
        if slots:
            print(slots)

    def check_casts(self):
        for (spell_id, count) in self.casts.items():
            cast = cast_in_fight.get(spell_id)
            if not cast:
                continue
            if cast.is_restricted(player=self.player, fight=self):
                kw = {
                    "type": cast.invalid_reason,
                }
                if cast.type == "spell":
                    kw["spell_id"] = cast.spell_id
                    kw["suggested_spell_id"] = cast.suggested_spell_id
                    kw["spell_wowhead_attr"] = f"spell={cast.spell_id}"
                    kw[
                        "higher_ranked_spell_wowhead_attr"
                    ] = f"spell={cast.suggested_spell_id}"
                    kw["count"] = count
                else:
                    raise Exception(
                        f"unhandled type for cast_in_fight restriction: {cast.type}"
                    )
                self.add_remark(**kw)

    def set_talents(self, talents):
        self.talents = Talents(talents=talents, player=self.player)

    def check_talents(self):
        if not self.talents:
            return
        used_talents = sum(self.talents.points)
        if used_talents != 61 and used_talents > 0:
            self.add_remark(
                type="invalid_talent_points",
                expected_points=61,
                points_used=used_talents,
            )

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
                wowhead_attr=f"spell={invalid_consumable[1]}",
            )
