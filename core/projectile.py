import pygame
import math

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y, damage, owner, dungeon):
        super().__init__()
        self.image = pygame.Surface((10, 10))  # Simple square for now
        self.image.fill((255, 255, 0))  # Yellow color
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.damage = damage
        self.owner = owner  # Owner of projectile
        self.dungeon = dungeon

        # Calculates direction and velocity
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx * dx + dy * dy)
        if distance > 0:
            self.speed_x = dx / distance * 5  # Adjust speed as needed
            self.speed_y = dy / distance * 5
        else:
            self.speed_x = 0
            self.speed_y = 0

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Check for wall collision
        tile_x = self.rect.x // self.dungeon.tile_size
        tile_y = self.rect.y // self.dungeon.tile_size

        if 0 <= tile_x < self.dungeon.width_tiles and 0 <= tile_y < self.dungeon.height_tiles:
            if self.dungeon.tiles[tile_y][tile_x] == 1: #Checks for wall
                self.kill()
                return

        # Checks if projectile off screen
        if self.rect.x < 0 or self.rect.x > pygame.display.get_surface().get_width() or \
           self.rect.y < 0 or self.rect.y > pygame.display.get_surface().get_height():
            self.kill()  # Removes projectile if off screen

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class VoidHoleProjectile(pygame.sprite.Sprite):
    def __init__(self, caster_center_pos, target_mouse_pos, owner, 
                 travel_speed=7, configured_max_travel_range=400,
                 lifetime_seconds=8, pull_radius=150, damage_radius=75, dps=20, pull_strength=1.5):
        super().__init__()
        
        self.owner = owner
        self.start_pos = pygame.math.Vector2(caster_center_pos)
        self.pos = pygame.math.Vector2(caster_center_pos)

        self.state = "traveling" # Initial state
        self.travel_speed = travel_speed
        vector_to_mouse = pygame.math.Vector2(target_mouse_pos) - self.start_pos
        distance_to_mouse = vector_to_mouse.length()

        self.actual_target_destination = pygame.math.Vector2(self.start_pos)
        self.total_distance_to_travel = 0
        
        if distance_to_mouse == 0:
            self.velocity = pygame.math.Vector2(0, 0)
            self._transition_to_active_phase()
        else:
            if distance_to_mouse <= configured_max_travel_range:
                self.actual_target_destination = pygame.math.Vector2(target_mouse_pos)
                self.total_distance_to_travel = distance_to_mouse
            else:
                self.actual_target_destination = self.start_pos + vector_to_mouse.normalize() * configured_max_travel_range
                self.total_distance_to_travel = configured_max_travel_range

            self.velocity = (self.actual_target_destination - self.start_pos).normalize() * self.travel_speed
        
        self.distance_traveled = 0


        self.travel_image = pygame.Surface([20, 20], pygame.SRCALPHA)
        pygame.draw.circle(self.travel_image, (100, 80, 180), (10, 10), 10)
        self.image = self.travel_image
        self.rect = self.image.get_rect(center=caster_center_pos)

        self.aoe_lifetime_seconds = lifetime_seconds
        self.aoe_activation_time = 0 
        self.pull_radius = pull_radius
        self.damage_radius = damage_radius
        self.dps = dps
        self.pull_strength = pull_strength
        self.damage_interval = 1000  # milliseconds
        self.last_damage_application_time = 0
        self.is_active_effect = False 

        # If not meant to travel
        if self.velocity.length_squared() == 0:
            self._transition_to_active_phase()

    def _transition_to_active_phase(self):
        if self.state == "active":
            return

        print(f"Void Hole projectile activating at {self.rect.center}")
        self.state = "active"
        self.is_active_effect = True
        self.aoe_activation_time = pygame.time.get_ticks()
        self.last_damage_application_time = self.aoe_activation_time # Start DPS timer

        # Change visual to the actual void hole
        self.active_image = pygame.Surface([40, 40], pygame.SRCALPHA) 
        pygame.draw.circle(self.active_image, (20, 0, 40), (20, 20), 20) 
        self.image = self.active_image
        current_center = self.rect.center 
        self.rect = self.image.get_rect(center=current_center)

    def update(self, enemies_list, dungeon_tiles, tile_size):
        current_time = pygame.time.get_ticks()

        if self.state == "traveling":
            self.pos += self.velocity
            self.rect.center = round(self.pos.x), round(self.pos.y)
            self.distance_traveled += self.velocity.length()

            for r_idx, row in enumerate(dungeon_tiles):
                for c_idx, tile_val in enumerate(row):
                    if tile_val == 1:
                        wall_rect = pygame.Rect(c_idx * tile_size, r_idx * tile_size, tile_size, tile_size)
                        if self.rect.colliderect(wall_rect):
                            self._transition_to_active_phase()
                            break
                if self.state == "active": break

            if self.state == "traveling" and self.distance_traveled >= self.total_distance_to_travel:
                self._transition_to_active_phase()

        elif self.state == "active":
            if not self.is_active_effect:
                self.kill()
                return

            if current_time - self.aoe_activation_time > (self.aoe_lifetime_seconds * 1000):
                self.is_active_effect = False
                self.kill()
                print("Void Hole effect expired.")
                return

            for enemy in enemies_list:
                if not enemy.alive: continue
                enemy_pos_vec = pygame.math.Vector2(enemy.rect.center)
                void_hole_center_vec = pygame.math.Vector2(self.rect.center)
                distance_vector = void_hole_center_vec - enemy_pos_vec
                distance = distance_vector.length()
                
                if 0 < distance < self.pull_radius:
                    move_vector = distance_vector.normalize() * self.pull_strength
                    # Store original position for collision rollback (ESSENTIAL)
                    original_ex, original_ey = enemy.rect.x, enemy.rect.y
                    enemy.rect.x += move_vector.x
                    # TODO: Check X collision for enemy with dungeon_tiles, if collision: enemy.rect.x = original_ex
                    enemy.rect.y += move_vector.y
                    # TODO: Check Y collision for enemy with dungeon_tiles, if collision: enemy.rect.y = original_ey

            if current_time - self.last_damage_application_time >= self.damage_interval:
                self.last_damage_application_time = current_time
                damage_this_tick = self.dps
                for enemy in enemies_list:
                    if not enemy.alive: continue
                    if pygame.math.Vector2(self.rect.center).distance_to(enemy.rect.center) < self.damage_radius:
                        enemy.take_damage(damage_this_tick)
        
        # If it somehow got into a bad state or needs to be cleaned up
        elif not self.is_active_effect and self.state != "traveling":
            self.kill()

    def draw_debug(self, surface):
        if self.state == "active":
            # Pull Radius
            s_pull = pygame.Surface((self.pull_radius * 2, self.pull_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(s_pull, (100, 100, 100, 80), (self.pull_radius, self.pull_radius), self.pull_radius)
            surface.blit(s_pull, (self.rect.centerx - self.pull_radius, self.rect.centery - self.pull_radius))
            # Damage Radius
            s_damage = pygame.Surface((self.damage_radius * 2, self.damage_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(s_damage, (200, 0, 0, 80), (self.damage_radius, self.damage_radius), self.damage_radius)
            surface.blit(s_damage, (self.rect.centerx - self.damage_radius, self.rect.centery - self.damage_radius))

class FireballProjectile(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y, damage, owner, dungeon,
                 aoe_radius=200, aoe_damage_factor=0.5):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill((255, 100, 0))
        self.rect = self.image.get_rect(center=(x,y))
        
        self.pos = pygame.math.Vector2(x, y)

        self.damage = damage
        self.owner = owner
        self.dungeon = dungeon

        self.aoe_radius = aoe_radius
        self.aoe_damage = int(damage * aoe_damage_factor)

        dx = target_x - self.pos.x
        dy = target_y - self.pos.y
        distance = math.sqrt(dx**2 + dy**2)
        
        self.speed = 5
        if distance > 0:
            self.velocity = pygame.math.Vector2(dx / distance * self.speed, dy / distance * self.speed)
        else:
            self.velocity = pygame.math.Vector2(0, 0)

    def update(self):
        self.pos += self.velocity
        self.rect.center = round(self.pos.x), round(self.pos.y)

        tile_x_center = self.rect.centerx // self.dungeon.tile_size
        tile_y_center = self.rect.centery // self.dungeon.tile_size

        if not (0 <= tile_x_center < self.dungeon.width_tiles and \
                0 <= tile_y_center < self.dungeon.height_tiles):
            self.kill()
            return

        if self.dungeon.tiles[tile_y_center][tile_x_center] == 1:
            print(f"Fireball hit wall at {self.rect.center}")
            self.is_exploding_on_impact = True
            self.kill() 
            return

        screen_rect = pygame.display.get_surface().get_rect()
        if not screen_rect.colliderect(self.rect):
            self.is_exploding_on_impact = False
            self.kill()

    def explode(self, all_enemies_list, impact_position):
        print(f"Fireball exploding at {impact_position} with AoE radius {self.aoe_radius} for {self.aoe_damage} damage.")
        aoe_hit_count = 0
        for enemy in all_enemies_list:
            if not enemy.alive:
                continue

            distance = pygame.math.Vector2(impact_position).distance_to(enemy.rect.center)
            if distance < self.aoe_radius:
                print(f"  AoE hit: {enemy.name} at distance {distance:.2f}")
                enemy.take_damage(self.aoe_damage)
                aoe_hit_count +=1
        if aoe_hit_count > 0:
            print(f"  AoE hit {aoe_hit_count} additional targets.")