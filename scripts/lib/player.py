from .base import Base
from .player_fight import PlayerFight
from .talents import Class, Specialization


class Player(Base):
    def __init__(self, data):
        super().__init__(data)
        self.fights = {}

    def get_fight(self, name):
        if name not in self.fights:
            self.fights[name] = PlayerFight(name=name, player=self)
        return self.fights[name]

    def benefits_from_windfury_totem(self, player_fight):
        return (
            self.is_(Class.Warrior)
            or self.is_(Class.Rogue)
            or player_fight.is_(Specialization.EnhancementShaman)
            or player_fight.is_(Specialization.RetributionPaladin)
        )

    def is_(self, x):
        if not isinstance(x, Class):
            raise TypeError(f"invalid class {x}")
        return self.subType == x.value

    def participated_to_fight(self, name):
        return name in self.fights
