from characters.character import Character

class Assassin(Character):
    def __init__(self, x, y):
        super().__init__("Archer", x, y, 32, 32, (0, 128, 0))  # Size (Color)
        self.piercing_arrow_cooldown = 0 # Initial cooldown, could change this if we want them to not use abilities right away
        self.smoke_bomb_cooldown = 0 # ""

    def piercing_arrow(self, target):
        ability_name = "piercing_arrow"
        cooldown_duration = 15  # Change if we want shorter or longer cd

        if not self.is_on_cooldown(ability_name):
            # Implement piercing arrow logic here
            self.start_cooldown(ability_name, cooldown_duration)
        else:
            pass # Cooldown visual logic

    def smoke_bomb(self):
        ability_name = "smoke_bomb"
        cooldown_duration = 30  # Change to whatever

        if not self.is_on_cooldown(ability_name):
            # Implement smoke bomb logic here
            self.start_cooldown(ability_name, cooldown_duration)
        else:
            pass # Cooldown visual logic