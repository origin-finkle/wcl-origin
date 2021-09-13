from lib.base import Base


class Enchant(Base):
    def is_restricted(self, player, fight, slot):
        return super().is_restricted(player=player, fight=fight)
