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
                "analysis": {},
            }
        )

    def as_json(self):
        return {k: v for (k, v) in self.__dict__.items() if k not in ("player",)}

    def add_remark(self, type, **kwargs):
        d = {"type": type, "fight": self.name}
        d.update(kwargs)
        self.remarks.append(Remark(d))

    def post_process(self):
        self.check_consumables()
        self.check_casts()
        self.check_talents()
        self.check_gear()
        self.analyze()

    def is_(self, x):
        return self.talents.is_(x)

    def analyze(self):
        self.analyze_casts()

    def analyze_casts(self):
        self.analysis["items"] = []
        self.analysis["spells"] = []
        self.analysis["unknown"] = []
        self.analysis["consumables"] = []
        for (spell_id, count) in self.casts.items():
            val = {"spell_id": spell_id, "count": count}
            if ci := cast_in_fight.get(spell_id):
                if not ci.display:
                    continue
                if ci.type == "spell":
                    self.analysis["spells"].append(val)
                elif ci.type == "consumable":
                    self.analysis["consumables"].append(val)
                elif ci.type == "item":
                    self.analysis["items"].append(val)
            else:
                self.analysis["unknown"].append(val)
        for k in ("unknown", "spells", "consumables", "items"):
            self.analysis[k] = sorted(self.analysis[k], key=lambda x: x["spell_id"])

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
            "À une main": 2,
            "Relique": 1,
            "Deux mains": 1,
            "Tenu(e) en main gauche": 1,
            "Armes de jet": 1,
        }
        for gear in self.gear:
            wowhead_data = get_wowhead_data(item_id=gear.id)
            if wowhead_data.get("slot") in ("Tabard", "Chemise"):
                continue
            slots[wowhead_data["slot"]] -= 1
            if slots[wowhead_data["slot"]] == 0:
                del slots[wowhead_data["slot"]]
        for slot in (
            "Tête",
            "Cou",
            "Épaule",
            "Torse",
            "Taille",
            "Jambes",
            "Pieds",
            "Poignets",
            "Mains",
            "Doigt",
            "Bijou",
            "Dos",
        ):
            if slots.get(slot):
                self.add_remark(type="missing_item_in_slot", slot=slot)
        if all(slot in slots for slot in ("Relique", "Armes de jet", "À distance")):
            self.add_remark(
                type="missing_item_in_slot",
                slot="Relique/Armes de jet/À distance",
            )
        if any(
            slot in slots
            for slot in (
                "Main gauche",
                "Main droite",
                "Tenu(e) en main gauche",
                "Deux mains",
                "À une main",
            )
        ):
            # so we need to figure out
            # possible options:
            # - Main droite + (Main gauche | Tenu(e) en main gauche | À une main)
            # - À une main + (À une main | Main gauche | Tenu(e) en main gauche)
            # - Deux mains
            valid = False
            if "Deux mains" not in slots:
                valid = True
            if "Main droite" not in slots and (
                any(slot in slots for slot in ("Main gauche", "Tenu(e) en main gauche"))
                or slots.get("À une main", 0) > 1
            ):
                valid = True
            if slots.get("À une main", 0) <= 1 and any(
                slot in slots for slot in ("Main gauche", "Tenu(e) en main gauche")
            ):
                valid = True
            if not valid:
                self.add_remark(type="missing_item_in_slot", slot="Armes")

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
