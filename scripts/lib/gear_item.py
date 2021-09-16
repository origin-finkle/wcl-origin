from urllib.parse import urlencode

from lib.base import Base
from lib.data.gems import gems
from lib.data.wowhead import get_wowhead_data


class GearItem(Base):
    def __init__(self, data):
        super().__init__(data)
        self.wowhead_data = get_wowhead_data(item_id=self.id)
        wowhead_qs = {
            "domain": "fr.tbc",
            "item": self.id,
        }
        if hasattr(self, "gems"):
            wowhead_qs["gems"] = ":".join(f"{gem['id']}" for gem in self.gems)
        if hasattr(self, "permanentEnchant"):
            wowhead_qs["ench"] = self.permanentEnchant
        self.wowhead_attr = urlencode(wowhead_qs)

    def count_gems(self, color):
        count = 0
        if hasattr(self, "gems"):
            for gem in self.gems:
                gem_i = gems.get(gem["id"])
                if gem_i.color in colors[color]:
                    count += 1
        return count

    def check_meta_gem(self, player_fight):
        if not hasattr(self, "gems"):
            return
        gem = next(
            (
                gem_i
                for gem in self.gems
                if (gem_i := gems.get(gem["id"]))
                and gem_i.color == "meta"
                and hasattr(gem_i, "requires")
            ),
            None,
        )
        if not gem:  # no meta available
            return
        if not gem.requires:
            return
        if gem.requires["rule"] == "count_at_least":
            c = {count["color"]: count["value"] for count in gem.requires["count"]}
            for item in player_fight.gear:
                for color in c.keys():
                    c[color] -= item.count_gems(color)
            if not all(c[color] <= 0 for color in c.keys()):
                player_fight.add_remark(
                    type="meta_not_activated",
                    item_wowhead_attr=f"domain=fr.tbc&item={self.id}",
                    wowhead_attr=f"domain=fr.tbc&item={gem.id}",
                )
        elif gem.requires["rule"] == "more_x_than_y":
            c = {gem.requires["x"]: 0, gem.requires["y"]: 0}
            for item in player_fight.gear:
                c[gem.requires["x"]] += item.count_gems(gem.requires["x"])
                c[gem.requires["y"]] += item.count_gems(gem.requires["y"])
            if c[gem.requires["x"]] <= c[gem.requires["y"]]:
                player_fight.add_remark(
                    type="meta_not_activated",
                    item_wowhead_attr=f"domain=fr.tbc&item={self.id}",
                    wowhead_attr=f"domain=fr.tbc&item={gem.id}",
                )
        else:
            raise Exception(f"rule {gem.requires['rule']} not handled")

    def as_json(self):
        return {k: v for (k, v) in self.__dict__.items() if k not in ("wowhead_data",)}


colors = {
    "blue": ["blue", "purple", "green"],
    "yellow": ["yellow", "orange", "green"],
    "red": ["red", "orange", "purple"],
    "all": ["blue", "red", "yellow"],
}
