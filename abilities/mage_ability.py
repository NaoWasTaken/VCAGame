from abilities.ability import Ability
from core.projectile import Projectile
from core.projectile import VoidHoleProjectile, FireballProjectile
import pygame 

class FireballAbility(Ability):
    def __init__(self):
        super().__init__(name="fireball", cooldown_duration=900)
        self.damage = 30
        self.aoe_radius = 120
        self.aoe_damage_factor = 0.8

    def activate(self, caster, target=None, game_context=None):
        target_position = target

        if not target_position:
            print(f"{self.name}: Requires a target position to be cast.")
            return

        if not game_context:
            print(f"{self.name}: Requires game context to operate.")
            return
            
        print(f"{caster.name} casts Fireball towards {target_position}!")
        
        fireball_projectile = FireballProjectile(
            x=caster.rect.centerx,
            y=caster.rect.centery,
            target_x=target_position[0],
            target_y=target_position[1],
            damage=self.damage,
            owner=caster,
            dungeon=game_context.dungeon,
            aoe_radius=self.aoe_radius,
            aoe_damage_factor=self.aoe_damage_factor
        )

        game_context.projectiles.add(fireball_projectile)
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

class VoidHoleAbility(Ability):
    def __init__(self):
        super().__init__(name="void_hole", cooldown_duration=1800)
        self.projectile_lifetime_seconds = 10
        self.projectile_pull_radius = 500
        self.projectile_damage_radius = 60
        self.projectile_dps = 20
        self.projectile_pull_strength = 1.2
        self.projectile_travel_speed = 4 
        self.projectile_max_travel_range = 700

    def activate(self, caster, target=None, game_context=None):
        target_mouse_pos = target

        if not target_mouse_pos:
            print(f"{self.name}: Requires a target mouse position.")
            return
        if not game_context:
            print(f"{self.name}: Requires game context.")
            return
            
        print(f"{caster.name} shoots a Void Hole projectile towards {target_mouse_pos}!")
        
        void_hole_projectile = VoidHoleProjectile(
            caster_center_pos=caster.rect.center,
            target_mouse_pos=target_mouse_pos,
            owner=caster,
            travel_speed=self.projectile_travel_speed,
            configured_max_travel_range=self.projectile_max_travel_range, 
            lifetime_seconds=self.projectile_lifetime_seconds,
            pull_radius=self.projectile_pull_radius,
            damage_radius=self.projectile_damage_radius,
            dps=self.projectile_dps,
            pull_strength=self.projectile_pull_strength
        )
        
        if not hasattr(game_context, 'active_aoe_effects'):
            game_context.active_aoe_effects = pygame.sprite.Group()
        game_context.active_aoe_effects.add(void_hole_projectile)

        self.start_caster_cooldown(caster)