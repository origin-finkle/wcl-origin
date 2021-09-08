from .base import Base


class Consumable(Base):
    def is_battle_elixir(self):
        return "battle_elixir" in self.types

    def is_guardian_elixir(self):
        return "guardian_elixir" in self.types

    def is_food(self):
        return "food" in self.types
