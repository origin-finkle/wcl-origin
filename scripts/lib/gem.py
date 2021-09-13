from .base import Base


class Gem(Base):
    def __init__(self, data):
        super().__init__(data)
        if not hasattr(self, "color"):
            raise Exception(f"Gem {self.name} has no color")

    def is_restricted(self, player, fight):
        if self.quality < 3:
            return True
        return super().is_restricted(player=player, fight=fight)
