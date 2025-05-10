from characters.character import Character
from abilities.mage_ability import FireballAbility, HealthSpellAbility, VoidHoleAbility, LightningStormAbility
import pygame

class Mage(Character):
    def __init__(self, x, y):
        super().__init__("Mage", x, y, 32, 32, (128, 0, 128)) # Size (Color)
        self.abilities = {}  # To store instances of known ability objects
        self.unlocked_abilities = [] #Store usable abilities
        self._learn_initial_abilities()

    def _learn_initial_abilities(self):
        self.learn_ability(FireballAbility())
        self.learn_ability(HealthSpellAbility())
        # EVERYTHING UNDER HERE GETS DELETED THIS IS FOR TESTING ONLY
        self.learn_ability(VoidHoleAbility())
        self.learn_ability(LightningStormAbility())

    def learn_ability(self, ability_instance):
        # Adds ability instance
        if ability_instance.name in self.abilities:
            print(f"{self.name} already knows {ability_instance.name}.")
            return

        self.abilities[ability_instance.name] = ability_instance
        print(f"{self.name} learned {ability_instance.name}!")

        if ability_instance.name not in self.unlocked_abilities:
            self.unlocked_abilities.append(ability_instance.name)

    def use_ability(self, ability_name, target=None, game_context=None):
        # Attempts to use ability name
        if ability_name in self.unlocked_abilities and ability_name in self.abilities:
            ability = self.abilities[ability_name]
            #Check cooldowns
            if ability.is_usable(self):
                ability.activate(self, target=target, game_context=game_context)
        elif ability_name not in self.abilities:
            print(f"Ability '{ability_name}' is unknown.")
        else: # Known but not unlocked
            print(f"Ability '{ability_name}' is not unlocked.")

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

        if self.max_health > 0:
            health_percentage = self.health / self.max_health
        else:
            health_percentage = 0

        bar_height = 7
        bar_y_offset = 10

        background_bar_x = self.rect.x
        background_bar_y = self.rect.y - bar_y_offset
        background_bar_width = self.rect.width
        background_bar_height = bar_height
        
        background_bar_rect = pygame.Rect(
            background_bar_x, 
            background_bar_y, 
            background_bar_width, 
            background_bar_height
        )

        current_health_width = background_bar_width * health_percentage
        health_fill_rect = pygame.Rect(
            background_bar_x, 
            background_bar_y, 
            current_health_width, 
            background_bar_height
        )

        background_color = (50, 50, 50)
        if health_percentage < 0.3:
            health_color = (255, 0, 0)
        elif health_percentage < 0.6:
            health_color = (255, 255, 0)
        else:
            health_color = (0, 255, 0)

        # Draw the health bar
        pygame.draw.rect(surface, background_color, background_bar_rect)
        if current_health_width > 0:
             pygame.draw.rect(surface, health_color, health_fill_rect)