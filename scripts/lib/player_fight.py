from .base import Base
from .remark import Remark


class PlayerFight(Base):
    def __init__(self, name):
        super().__init__(
            {
                "name": name,
                "auras": {},
                "remarks": [],
                "talents": [],
                "casts": {},
            }
        )

    def looks_like_enhancement_shaman(self):
        return (
            self.talents[1]["id"] > self.talents[0]["id"]
            and self.talents[1]["id"] > self.talents[2]["id"]
        )

    def looks_like_retribution_paladin(self):
        return (
            self.talents[2]["id"] > self.talents[0]["id"]
            and self.talents[2]["id"] > self.talents[1]["id"]
        )

    def add_remark(self, type, **kwargs):
        d = {"type": type}
        d.update(kwargs)
        self.remarks.append(Remark(d))
