from abilities.ability import Ability
from core.projectile import Projectile
import pygame 

class FireballAbility(Ability):
    def __init__(self):
        super().__init__(name="fireball", cooldown_duration=900) # 15 Seconds
        self.damage = 30  # Example damage for the fireball

    def activate(self, caster, target=None, game_context=None):
        target_position = target # Assuming target passed is the position

        if not target_position:
            print(f"{self.name}: Requires a target position to be cast.")
            return

        if not game_context:
            print(f"{self.name}: Requires game context to operate.")
            return
            
        print(f"{caster.name} casts Fireball towards {target_position}!")
        
        # Create and launch the projectile
        projectile = Projectile(
            caster.rect.centerx,
            caster.rect.centery,
            target_position[0],
            target_position[1],
            self.damage,
            caster,
            game_context.dungeon
        )

        game_context.projectiles.add(projectile) # Add to the games projectile group

        self.start_caster_cooldown(caster)

class HealthSpellAbility(Ability):
    def __init__(self):
        super().__init__(name="heal", cooldown_duration=1800) # 30 Seconds
        self.heal_amount = 20

    def activate(self, caster, target=None, game_context=None):
        if hasattr(caster, 'max_health'):
            if caster.health >= caster.max_health:
                print(f"{caster.name} is already at full health.")
                self.start_caster_cooldown(caster)
                return

            caster.health += self.heal_amount
            if caster.health > caster.max_health:
                caster.health = caster.max_health
            print(f"{caster.name} casts Health Spell and heals for {self.heal_amount}, now at {caster.health}/{caster.max_health} HP.")
            
        self.start_caster_cooldown(caster)