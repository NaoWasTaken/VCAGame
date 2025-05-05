from characters.character import Character

class Assassin(Character):
    def __init__(self, x, y):
        super().__init__("Assassin", x, y, 32, 32, (64, 64, 64))  # Size (Color)
        self.stealth_cooldown = 0 # Initial cooldown, could change this if we want them to not use abilities right away
        self.throw_knives_cooldown = 0 # ""

    def throw_knives(self, target):
        ability_name = "throw_knives"
        cooldown_duration = 15  # Change if we want shorter or longer cd

        if not self.is_on_cooldown(ability_name):
            # Implement throwing knives logic here
            self.start_cooldown(ability_name, cooldown_duration)
        else:
            pass # Cooldown visual logic

    def stealth(self):
        ability_name = "stealth"
        cooldown_duration = 30  # Change to whatever

        if not self.is_on_cooldown(ability_name):
            # Implement stealth logic here
            self.start_cooldown(ability_name, cooldown_duration)
        else:
            pass # Cooldown visual logic