class Base(object):
    def __init__(self, data):
        for (k, v) in data.items():
            setattr(self, k, v)

    def is_restricted(self, player, fight):
        from .talents import Specialization, Class, Role, convert_any

        # run the "_not" restrictions before
        # return True only if there's a match, otherwise run next checks
        if hasattr(self, "restricted_specializations_not"):
            if any(
                fight.is_(Specialization(s))
                for s in self.restricted_specializations_not
            ):
                return True

        # run the restrictions after, if there is not any matches, return True
        if hasattr(self, "restricted_any"):
            if not any(fight.is_(convert_any(ra)) for ra in self.restricted_any):
                return True
        if hasattr(self, "restricted_fights"):
            if fight.name not in self.restricted_fights:
                return True
        if hasattr(self, "restricted_classes"):
            if not any(player.is_(Class(c)) for c in self.restricted_classes):
                return True
        if hasattr(self, "restricted_roles"):
            if not any(fight.is_(Role(r)) for r in self.restricted_roles):
                return True
        if hasattr(self, "restricted_specializations"):
            if not any(
                fight.is_(Specialization(s)) for s in self.restricted_specializations
            ):
                return True
        if hasattr(self, "invalid") and self.invalid:
            return True
        return False

    def as_json(self):
        return self.__dict__
