from hashlib import sha256
from .base import Base


class Remark(Base):
    def __init__(self, data):
        super().__init__(data)
        self.compute_uuid()

    def compute_uuid(self):
        uuid = [self.type]
        for attr in (
            "wowhead_attr",
            "item_wowhead_attr",
            "spell_wowhead_attr",
            "slot",
            "fight",
        ):
            if hasattr(self, attr) and (v := getattr(self, attr)):
                uuid.append(v)
        self.uuid = ":".join(uuid)
