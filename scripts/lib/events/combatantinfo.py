from urllib.parse import urlencode
import logging

from .event import Event
from lib.data.wowhead import get_wowhead_data
from lib.data import cheap_enchants, gems, temporary_enchants, players
from lib.config import (
    CHEAP_GEM_QUALITY_LOWER_BOUND,
    SLOTS_WITH_TEMPORARY_ENCHANT,
    SLOTS_TO_ENCHANT,
)


class CombatantInfo(Event):
    def _process(self, player_fight, player):
        player_fight.talents = self.talents
        player_fight.auras = {aura["ability"]: aura for aura in self.auras}
        for aura in player_fight.auras.values():
            aura["events"] = []
        player_fight.gear = [
            gear
            for gear in self.gear
            if not gear["icon"].startswith("inv_shirt_") and gear["id"] > 0
        ]
        for item in player_fight.gear:
            self._process_gear_item(player=player, player_fight=player_fight, item=item)

    def _process_gear_item(self, player, player_fight, item):
        wowhead_qs = {
            "domain": "fr.tbc",
            "item": item["id"],
        }
        wowhead_data = get_wowhead_data(item_id=item["id"])
        # gems added to the equipment
        if item.get("gems"):
            for gem in item["gems"]:
                wowhead_gem_data = get_wowhead_data(gem_id=gem["id"])
                if wowhead_gem_data["quality"] < CHEAP_GEM_QUALITY_LOWER_BOUND or (
                    (gem_i := gems.get(gem["id"]))
                    and gem_i.is_restricted(player=player, fight=player_fight)
                ):
                    player_fight.add_remark(
                        type="cheap_gem",
                        item_wowhead_attr=f"domain=fr.tbc&item={item['id']}",
                        wowhead_attr=f"domain=fr.tbc&item={gem['id']}",
                    )
            wowhead_qs["gems"] = ":".join(f"{gem['id']}" for gem in item["gems"])

        # missing gems on gem slots
        if len(item.get("gems", [])) != wowhead_data["sockets"]:
            player_fight.add_remark(
                type="missing_gems",
                item_wowhead_attr=f"domain=fr.tbc&item={item['id']}",
                count=wowhead_data["sockets"] - len(item.get("gems", [])),
            )

        if item.get("permanentEnchant"):
            if item["permanentEnchant"] in cheap_enchants:
                player_fight.add_remark(
                    type="cheap_enchant",
                    item_wowhead_attr=f"domain=fr.tbc&item={item['id']}",
                    wowhead_attr=f"domain=fr.tbc&spell={item['permanentEnchant']}",
                )
            wowhead_qs["ench"] = item["permanentEnchant"]
        elif wowhead_data["slot"] in SLOTS_TO_ENCHANT:
            player_fight.add_remark(
                type="no_enchant",
                item_wowhead_attr=f"domain=fr.tbc&item={item['id']}",
            )
        item["wowhead_attr"] = urlencode(wowhead_qs)

        if item.get("temporaryEnchant"):
            if te := temporary_enchants.get(item["temporaryEnchant"]):
                if te.is_restricted(player=player, fight=player_fight):
                    player_fight.add_remark(
                        type="invalid_temporary_enchant",
                        item_wowhead_attr=f"domain=fr.tbc&item={item['id']}&ench={item['temporaryEnchant']}",
                    )
            else:
                player_fight.add_remark(
                    type="invalid_temporary_enchant",
                    item_wowhead_attr=f"domain=fr.tbc&item={item['id']}&ench={item['temporaryEnchant']}",
                )
                logging.getLogger("default").info(
                    f"Unknown temporary enchant {item['temporaryEnchant']} on player {player.name} and fight {player_fight.name}"
                )
        elif wowhead_data["slot"] in SLOTS_WITH_TEMPORARY_ENCHANT:
            # could be due to windfury in the group, so this would apply only to melee classes
            if player.benefits_from_windfury_totem(player_fight=player_fight) and any(
                # at least one shaman is in the raid and participated to the fight
                p.is_shaman() and p.participated_to_fight(name=player_fight.name)
                for p in players.values()
            ):
                player_fight.add_remark(
                    type="no_temporary_enchant_but_windfury",
                    item_wowhead_attr=f"domain=fr.tbc&item={item['id']}",
                )
            else:
                player_fight.add_remark(
                    type="no_temporary_enchant",
                    item_wowhead_attr=f"domain=fr.tbc&item={item['id']}",
                )
