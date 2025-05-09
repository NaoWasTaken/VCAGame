class Ability:
    def __init__(self, name, cooldown_duration, mana_cost=0): # Add other common params
        self.name = name
        self.cooldown_duration = cooldown_duration
        self.mana_cost = mana_cost
        # Add other attributes later

    def is_usable(self, caster):
        if caster.is_on_cooldown(self.name):
            print(f"{self.name} is on cooldown.")
            return False
        return True

    def activate(self, caster, target=None, game_context=None):
        # Placeholder for the ability's effect. Override in subclasses
        raise NotImplementedError("Each ability must implement activate().")

    def start_caster_cooldown(self, caster):
        # Puts ability on CD
        caster.start_cooldown(self.name, self.cooldown_duration)