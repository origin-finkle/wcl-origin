from .base import Base
from .player_fight import PlayerFight


class Player(Base):
    def __init__(self, data):
        super().__init__(data)
        self.fights = {}

    def get_fight(self, name):
        if name not in self.fights:
            self.fights[name] = PlayerFight(name=name)
        return self.fights[name]

    def benefits_from_windfury_totem(self, player_fight):
        if self.is_warrior() or self.is_rogue():
            return True
        if self.is_shaman():
            return player_fight.looks_like_enhancement_shaman()
        if self.is_paladin():
            return player_fight.looks_like_retribution_paladin()
        return False

    def is_shaman(self):
        return self.subType == "Shaman"

    def is_warrior(self):
        return self.subType == "Warrior"

    def is_rogue(self):
        return self.subType == "Rogue"

    def is_paladin(self):
        return self.subType == "Paladin"

    def participated_to_fight(self, name):
        return name in self.fights
