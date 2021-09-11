class Event:
    def __init__(self, data):
        for (k, v) in data.items():
            setattr(self, k, v)

    @staticmethod
    def new(event):
        if event["type"] == "combatantinfo":
            from .combatantinfo import CombatantInfo

            return CombatantInfo(event)
        elif event["type"] == "cast":
            from .cast import Cast

            return Cast(event)

        elif event["type"] == "applybuff":
            from .applybuff import ApplyBuff

            return ApplyBuff(event)

        raise Exception(f"Event {event['type']} not handled")

    @staticmethod
    def process(event, player, player_fight):
        Event.new(event)._process(player=player, player_fight=player_fight)
