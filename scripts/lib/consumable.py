class Consumable(object):
    def __init__(self, data):
        for (k, v) in data.items():
            setattr(self, k, v)

    def is_restricted(self, player, fight):
        if hasattr(self, "restricted_fights"):
            if fight["name"] not in self.restricted_fights:
                return True
        if hasattr(self, "invalid") and self.invalid:
            return True
        return False

    def is_battle_elixir(self):
        return "battle_elixir" in self.types

    def is_guardian_elixir(self):
        return "guardian_elixir" in self.types

    def is_food(self):
        return "food" in self.types
