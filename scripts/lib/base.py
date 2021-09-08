class Base(object):
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
