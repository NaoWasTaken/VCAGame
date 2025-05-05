from characters.character import Character

class Mage(Character):
    def __init__(self, x, y):
        super().__init__("Mage", x, y, 32, 32, (128, 0, 128)) # Size (Color)
        self.fireball.cooldown = 0 # Initial cooldown, could change this if we want them to not use abilities right away
        self.heal_cooldown = 0 # ""

    def cast_fireball(self, target):
        fireball_name = "fireball"
        cooldown_duration = 15 # Change if we want shorter or longer cd

        if not self.is_on_cooldown(fireball_name):
            # Implement fireball logic here
            self.start_cooldown(fireball_name, cooldown_duration)
        else:
            pass # Cooldown visual logic

    def cast_healthspell(self):
        heal_name = heal_name
        cooldown_duration = 30 # Change to whatever

        if not self.is_on_cooldown(heal_name):
            heal_amount = 20 # Change if we want more or less healing
            self.health += heal_amount
            # Heal visual logic goes here
            self.start_cooldown(heal_name, cooldown_duration)
        else:
            pass # Cooldown visual logic