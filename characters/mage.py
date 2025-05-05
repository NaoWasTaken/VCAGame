from characters.character import Character

class Mage(Character):
    def __init__(self, x, y):
        super().__init__("Mage", x, y, 32, 32, (128, 0, 128)) # Size (Color)

    def cast_fireball(self, target):
        fireball_name = "fireball"
        cooldown_duration = 900 # Change if we want shorter or longer cd

        if not self.is_on_cooldown(fireball_name):
            print(f"{self.name} casts Fireball on {target.name}!") # Placeholder for fireball logic
            self.start_cooldown(fireball_name, cooldown_duration)
        else:
            print("Ability is on cooldown")
            pass # Cooldown visual logic

    def cast_healthspell(self):
        heal_name = "heal"  # Corrected line: Assign "heal" to heal_name
        cooldown_duration = 1800 # Change to whatever

        if not self.is_on_cooldown(heal_name):
            heal_amount = 20 # Change if we want more or less healing
            self.health += heal_amount
            print(f"{self.name} casts Health Spell and heals for {heal_amount}.") # Placeholder for heal visual logic
            self.start_cooldown(heal_name, cooldown_duration)
        else:
            print("Ability is on cooldown")
            pass # Cooldown visual logic