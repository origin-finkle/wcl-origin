import enum

from .base import Base


class Role(enum.Enum):
    Tank = "Tank"
    Heal = "Heal"
    Melee = "Melee"
    Ranged = "Ranged"
    Magic = "Magic"
    Physical = "Physical"


class Class(enum.Enum):
    Paladin = "Paladin"
    Rogue = "Rogue"
    Warrior = "Warrior"
    Shaman = "Shaman"
    Druid = "Druid"
    Priest = "Priest"
    Warlock = "Warlock"
    Mage = "Mage"
    Hunter = "Hunter"
    Unknown = "Unknown"


class Specialization(enum.Enum):
    RetributionPaladin = "RetributionPaladin"
    HolyPaladin = "HolyPaladin"
    ProtectionPaladin = "ProtectionPaladin"
    CombatRogue = "CombatRogue"
    AssassinationRogue = "AssassinationRogue"
    SubtletyRogue = "SubtletyRogue"
    ArmsWarrior = "ArmsWarrior"
    FuryWarrior = "FuryWarrior"
    ProtectionWarrior = "ProtectionWarrior"
    EnhancementShaman = "EnhancementShaman"
    ElementalShaman = "ElementalShaman"
    RestorationShaman = "RestorationShaman"
    BalanceDruid = "BalanceDruid"
    CatDruid = "CatDruid"
    BearDruid = "BearDruid"
    FeralDruid = "FeralDruid"
    RestorationDruid = "RestorationDruid"
    DisciplinePriest = "DisciplinePriest"
    HolyPriest = "HolyPriest"
    ShadowPriest = "ShadowPriest"
    AfflictionWarlock = "AfflictionWarlock"
    DemonologyWarlock = "DemonologyWarlock"
    DestructionWarlock = "DestructionWarlock"
    ArcaneMage = "ArcaneMage"
    FireMage = "FireMage"
    FrostMage = "FrostMage"
    SurvivalHunter = "SurvivalHunter"
    MarksmanshipHunter = "MarksmanshipHunter"
    BeastMasteryHunter = "BeastMasteryHunter"
    Unknown = "Unknown"


specs = {
    Specialization.HolyPaladin: {
        "_has_more_points_in": 0,
        "class": Class.Paladin,
        "role": [Role.Heal],
    },
    Specialization.ProtectionPaladin: {
        "_has_more_points_in": 1,
        "class": Class.Paladin,
        "role": [Role.Tank, Role.Magic],
    },
    Specialization.RetributionPaladin: {
        "_has_more_points_in": 2,
        "class": Class.Paladin,
        "role": [Role.Melee, Role.Physical],
    },
    Specialization.AssassinationRogue: {
        "_has_more_points_in": 0,
        "class": Class.Rogue,
        "role": [Role.Melee, Role.Physical],
    },
    Specialization.CombatRogue: {
        "_has_more_points_in": 1,
        "class": Class.Rogue,
        "role": [Role.Melee, Role.Physical],
    },
    Specialization.SubtletyRogue: {
        "_has_more_points_in": 2,
        "class": Class.Rogue,
        "role": [Role.Melee, Role.Physical],
    },
    Specialization.ArmsWarrior: {
        "_has_more_points_in": 0,
        "class": Class.Warrior,
        "role": [Role.Melee, Role.Physical],
    },
    Specialization.FuryWarrior: {
        "_has_more_points_in": 1,
        "class": Class.Warrior,
        "role": [Role.Melee, Role.Physical],
    },
    Specialization.ProtectionWarrior: {
        "_has_more_points_in": 2,
        "class": Class.Warrior,
        "role": [Role.Tank, Role.Physical],
    },
    Specialization.ElementalShaman: {
        "_has_more_points_in": 0,
        "class": Class.Shaman,
        "role": [Role.Ranged, Role.Magic],
    },
    Specialization.EnhancementShaman: {
        "_has_more_points_in": 1,
        "class": Class.Shaman,
        "role": [Role.Melee, Role.Physical],
    },
    Specialization.RestorationShaman: {
        "_has_more_points_in": 2,
        "class": Class.Shaman,
        "role": [Role.Heal],
    },
    Specialization.BalanceDruid: {
        "_has_more_points_in": 0,
        "class": Class.Druid,
        "role": [Role.Ranged, Role.Magic],
    },
    Specialization.FeralDruid: {
        "_has_more_points_in": 1,
        "class": Class.Druid,
        "role": [Role.Melee, Role.Tank, Role.Physical],
    },
    Specialization.RestorationDruid: {
        "_has_more_points_in": 2,
        "class": Class.Druid,
        "role": [Role.Heal],
    },
    Specialization.DisciplinePriest: {
        "_has_more_points_in": 0,
        "class": Class.Priest,
        "role": [Role.Heal],
    },
    Specialization.HolyPriest: {
        "_has_more_points_in": 1,
        "class": Class.Priest,
        "role": [Role.Heal],
    },
    Specialization.ShadowPriest: {
        "_has_more_points_in": 2,
        "class": Class.Priest,
        "role": [Role.Ranged, Role.Magic],
    },
    Specialization.AfflictionWarlock: {
        "_has_more_points_in": 0,
        "class": Class.Warlock,
        "role": [Role.Ranged, Role.Magic],
    },
    Specialization.DemonologyWarlock: {
        "_has_more_points_in": 1,
        "class": Class.Warlock,
        "role": [Role.Ranged, Role.Magic],
    },
    Specialization.DestructionWarlock: {
        "_has_more_points_in": 2,
        "class": Class.Warlock,
        "role": [Role.Ranged, Role.Magic],
    },
    Specialization.ArcaneMage: {
        "_has_more_points_in": 0,
        "class": Class.Mage,
        "role": [Role.Ranged, Role.Magic],
    },
    Specialization.FireMage: {
        "_has_more_points_in": 1,
        "class": Class.Mage,
        "role": [Role.Ranged, Role.Magic],
    },
    Specialization.FrostMage: {
        "_has_more_points_in": 2,
        "class": Class.Mage,
        "role": [Role.Ranged, Role.Magic],
    },
    Specialization.SurvivalHunter: {
        "_has_more_points_in": 0,
        "class": Class.Hunter,
        "role": [Role.Ranged, Role.Physical],
    },
    Specialization.MarksmanshipHunter: {
        "_has_more_points_in": 1,
        "class": Class.Hunter,
        "role": [Role.Ranged, Role.Physical],
    },
    Specialization.BeastMasteryHunter: {
        "_has_more_points_in": 2,
        "class": Class.Hunter,
        "role": [Role.Ranged, Role.Physical],
    },
    Specialization.Unknown: {
        "_has_more_points_in": 0,
        "class": Class.Unknown,
        "role": [],
    },
}


class Talents(Base):
    def __init__(self, talents, player):
        # no need to init Base
        self.points = [t["id"] for t in talents]
        self.player = player
        self.spec = Specialization.Unknown
        self._guess_spec()

    def _guess_spec(self):
        for spec in specs.keys():
            if self.is_(spec):
                self.spec = spec
                break

    def as_json(self):
        return {k: v for (k, v) in self.__dict__.items() if k not in ("player",)}

    def _has_more_points_in(self, x):
        for i in (0, 1, 2):
            if i == x:
                continue
            if not self.points[x] > self.points[i]:
                return False
        return True

    def is_(self, x):
        if isinstance(x, Specialization):
            data = specs[x]
            if self.is_(data["class"]) and self._has_more_points_in(
                data["_has_more_points_in"]
            ):
                return True
        elif isinstance(x, Class):
            return self.player.subType == x.value
        elif isinstance(x, Role):
            return x in specs[self.spec]["role"]
        return False
