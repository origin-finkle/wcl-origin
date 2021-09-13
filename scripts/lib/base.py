class Base(object):
    def __init__(self, data):
        for (k, v) in data.items():
            setattr(self, k, v)

    def is_restricted(self, player, fight):
        if hasattr(self, "restricted_fights"):
            if fight.name not in self.restricted_fights:
                return True
        if hasattr(self, "restricted_classes"):
            from .talents import Class

            if not any(player.is_(Class(c)) for c in self.restricted_classes):
                return True
        if hasattr(self, "restricted_roles"):
            from .talents import Role

            if not any(fight.is_(Role(r)) for r in self.restricted_roles):
                return True
        if hasattr(self, "restricted_specializations"):
            from .talents import Specialization

            if not any(
                fight.is_(Specialization(s)) for s in self.restricted_specializations
            ):
                return True
        if hasattr(self, "invalid") and self.invalid:
            return True
        return False

    def as_json(self):
        return self.__dict__
