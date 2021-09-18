import logging

from .event import Event
from lib.data.wowhead import get_wowhead_data
from lib.data import enchants, gems, temporary_enchants, players
from lib.config import (
    SLOTS_WITH_TEMPORARY_ENCHANT,
    SLOTS_TO_ENCHANT,
)
from lib.talents import Class
from lib.gear_item import GearItem


class CombatantInfo(Event):
    def _process(self, player_fight, player):
        player_fight.set_talents(self.talents)
        player_fight.auras = {aura["ability"]: aura for aura in self.auras}
        for aura in player_fight.auras.values():
            aura["events"] = []
        player_fight.gear = [
            GearItem(gear)
            for gear in self.gear
            if not gear["icon"].startswith("inv_shirt_") and gear["id"] > 0
        ]
        for item in player_fight.gear:
            self._process_gear_item(player=player, player_fight=player_fight, item=item)
            item.check_meta_gem(player_fight=player_fight)

    def _process_gear_item(self, player, player_fight, item):
        wowhead_data = item.wowhead_data
        # gems added to the equipment
        if hasattr(item, "gems"):
            for gem in item.gems:
                gem_i = gems.get(gem["id"])
                if not gem_i or gem_i.is_restricted(player=player, fight=player_fight):
                    player_fight.add_remark(
                        type="invalid_gem",
                        item_wowhead_attr=f"domain=fr.tbc&item={item.id}",
                        wowhead_attr=f"domain=fr.tbc&item={gem['id']}",
                    )

        # missing gems on gem slots
        nbr_gems = len(item.gems) if hasattr(item, "gems") else 0
        if nbr_gems != wowhead_data["sockets"]:
            player_fight.add_remark(
                type="missing_gems",
                item_wowhead_attr=f"domain=fr.tbc&item={item.id}",
                count=wowhead_data["sockets"] - nbr_gems,
            )

        if hasattr(item, "permanentEnchant"):
            e = enchants.get(item.permanentEnchant)
            if not e:
                player_fight.add_remark(
                    type="invalid_enchant",
                    item_wowhead_attr=f"domain=fr.tbc&item={item.id}&ench={item.permanentEnchant}",
                    slot=wowhead_data["slot"],
                    enchant_id=item.permanentEnchant,
                )
            elif e.is_restricted(
                player=player,
                fight=player_fight,
                slot=wowhead_data["slot"],
            ):
                player_fight.add_remark(
                    type="invalid_enchant",
                    item_wowhead_attr=f"domain=fr.tbc&item={item.id}&ench={item.permanentEnchant}",
                    wowhead_attr=(
                        f"domain=fr.tbc&spell={e.spell_id}"
                        if hasattr(e, "spell_id")
                        else None
                    ),
                    slot=wowhead_data["slot"],
                    enchant_id=item.permanentEnchant,
                )
        elif wowhead_data["slot"] in SLOTS_TO_ENCHANT:
            player_fight.add_remark(
                type="no_enchant",
                item_wowhead_attr=f"domain=fr.tbc&item={item.id}",
            )

        if hasattr(item, "temporaryEnchant"):
            if te := temporary_enchants.get(item.temporaryEnchant):
                if te.is_restricted(player=player, fight=player_fight):
                    player_fight.add_remark(
                        type="invalid_temporary_enchant",
                        item_wowhead_attr=f"domain=fr.tbc&item={item.id}&ench={item.temporaryEnchant}",
                    )
            else:
                player_fight.add_remark(
                    type="invalid_temporary_enchant",
                    item_wowhead_attr=f"domain=fr.tbc&item={item.id}&ench={item.temporaryEnchant}",
                )
                logging.getLogger("default").info(
                    f"Unknown temporary enchant {item.temporaryEnchant} on player {player.name} and fight {player_fight.name}"
                )
        elif wowhead_data["slot"] in SLOTS_WITH_TEMPORARY_ENCHANT:
            # could be due to windfury in the group, so this would apply only to melee classes
            if player.benefits_from_windfury_totem(player_fight=player_fight) and any(
                # at least one shaman is in the raid and participated to the fight
                p.is_(Class.Shaman) and p.participated_to_fight(name=player_fight.name)
                for p in players.values()
            ):
                player_fight.add_remark(
                    type="no_temporary_enchant_but_windfury",
                    item_wowhead_attr=f"domain=fr.tbc&item={item.id}",
                )
            else:
                player_fight.add_remark(
                    type="no_temporary_enchant",
                    item_wowhead_attr=f"domain=fr.tbc&item={item.id}",
                )
