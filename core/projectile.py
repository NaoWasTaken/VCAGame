import pygame
import math

LIGHTNING_COLOR = (173, 216, 230)
LIGHTNING_WIDTH = 8
LIGHTNING_LENGTH = 15
LIGHTNING_SPEED = 7

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

class LightningProjectile(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y, damage, owner, dungeon, game_context,
                 stun_duration_frames, arc_range, max_arcs,
                 current_arc_count=0, hit_in_chain=None, speed=LIGHTNING_SPEED):
        super().__init__()
        self.owner = owner
        self.dungeon = dungeon
        self.game_context = game_context 
        self.damage = damage
        self.stun_duration_frames = stun_duration_frames
        self.arc_range = arc_range
        self.max_arcs = max_arcs
        self.current_arc_count = current_arc_count
        self.speed = speed

        if hit_in_chain is None:
            self.hit_in_chain = set()
        else:
            self.hit_in_chain = hit_in_chain

        # Visuals
        self.image = pygame.Surface((LIGHTNING_LENGTH, LIGHTNING_WIDTH), pygame.SRCALPHA)
        self.image.fill(LIGHTNING_COLOR) 
        self.original_image = self.image.copy() 
        self.rect = self.image.get_rect(center=(x, y))
        
        self.pos = pygame.math.Vector2(x, y)
        
        direction = pygame.math.Vector2(target_x - x, target_y - y)
        if direction.length_squared() > 0:
            self.velocity = direction.normalize() * self.speed
        else:
            self.velocity = pygame.math.Vector2(0, 0)
            print("DEBUG: LightningProjectile created with zero velocity, killing.")
            self.kill() 

        if self.velocity.length_squared() > 0:
            angle = self.velocity.angle_to(pygame.math.Vector2(1, 0)) 
            self.image = pygame.transform.rotate(self.original_image, -angle) 
            self.rect = self.image.get_rect(center=self.rect.center)
        
        print(f"DEBUG: LightningProjectile CREATED. Arc: {self.current_arc_count}, Target: ({target_x},{target_y}), Vel: {self.velocity}, hit_in_chain: {self.hit_in_chain}")


    def update(self):
        if not self.alive(): return 

        self.pos += self.velocity
        self.rect.center = round(self.pos.x), round(self.pos.y)

        tile_x_center = self.rect.centerx // self.dungeon.tile_size
        tile_y_center = self.rect.centery // self.dungeon.tile_size

        if not (0 <= tile_x_center < self.dungeon.width_tiles and \
                0 <= tile_y_center < self.dungeon.height_tiles):
            print(f"DEBUG: LightningProjectile off dungeon grid at {self.rect.center}, killing.")
            self.kill()
            return

        if self.dungeon.tiles[tile_y_center][tile_x_center] == 1:
            print(f"DEBUG: LightningProjectile hit wall at {self.rect.center}, killing.")
            self.kill() 
            return

        screen_rect = pygame.display.get_surface().get_rect()
        if not screen_rect.colliderect(self.rect):
            print(f"DEBUG: LightningProjectile off screen at {self.rect.center}, killing.")
            self.kill()
            return

        for enemy in self.game_context.enemies:
            if not enemy.alive or not hasattr(enemy, 'id') or not hasattr(enemy, 'apply_stun'):
                continue 

            if self.rect.colliderect(enemy.rect) and enemy.id not in self.hit_in_chain:
                print(f"DEBUG: LightningProjectile attempting to handle_impact with Enemy ID: {enemy.id}")
                self.handle_impact(enemy)
                return

    def handle_impact(self, enemy):
        print(f"DEBUG: LightningProjectile IMPACT with {enemy.name if hasattr(enemy, 'name') else 'enemy'} (ID: {enemy.id}). Arc: {self.current_arc_count + 1}/{self.max_arcs + 1}")

        print(f"DEBUG: Applying {self.damage} damage to Enemy ID: {enemy.id}")
        enemy.take_damage(self.damage)

        if hasattr(enemy, 'apply_stun'):
             enemy.apply_stun(self.stun_duration_frames, is_lightning_stun=True)
        else:
            print(f"Warning: Enemy ID {enemy.id} does not have apply_stun method.")
        
        current_enemy_id = enemy.id
        self.hit_in_chain.add(current_enemy_id)
        print(f"DEBUG: Added Enemy ID {current_enemy_id} to hit_in_chain. Chain: {self.hit_in_chain}")


        # 3. Attempt to arc
        if self.current_arc_count < self.max_arcs:
            print(f"DEBUG: Attempting arc {self.current_arc_count + 1}. Max arcs: {self.max_arcs}")
            next_target = self.find_next_arc_target(enemy.rect.center)
            if next_target:
                print(f"DEBUG: Found next arc target: {next_target.name if hasattr(next_target, 'name') else 'enemy'} (ID: {next_target.id})")
                arc_projectile = LightningProjectile(
                    x=enemy.rect.centerx,
                    y=enemy.rect.centery,
                    target_x=next_target.rect.centerx,
                    target_y=next_target.rect.centery,
                    damage=self.damage,
                    owner=self.owner,
                    dungeon=self.dungeon,
                    game_context=self.game_context,
                    stun_duration_frames=self.stun_duration_frames,
                    arc_range=self.arc_range,
                    max_arcs=self.max_arcs,
                    current_arc_count=self.current_arc_count + 1,
                    hit_in_chain=self.hit_in_chain.copy()
                )
                self.game_context.projectiles.add(arc_projectile)
                print(f"DEBUG: Added arc projectile to group. Projectiles in group: {len(self.game_context.projectiles)}")
            else:
                print(f"DEBUG: No valid arc target found from Enemy ID {current_enemy_id}.")
        else:
            print(f"DEBUG: Max arcs reached ({self.current_arc_count +1 } / {self.max_arcs + 1}). No more arcing.")
        
        print(f"DEBUG: LightningProjectile (Arc {self.current_arc_count}) being killed after impact/arc attempt.")
        self.kill()

    def find_next_arc_target(self, current_enemy_pos_tuple):
        current_enemy_pos = pygame.math.Vector2(current_enemy_pos_tuple)
        closest_enemy = None
        min_distance_sq = self.arc_range ** 2 
        
        print(f"DEBUG find_next_arc_target: Center: {current_enemy_pos}, Arc Range (sq): {min_distance_sq}, Hit in this chain: {self.hit_in_chain}")

        if not hasattr(self.game_context, 'enemies') or self.game_context.enemies is None:
            print("DEBUG find_next_arc_target: game_context.enemies is missing or None.")
            return None

        for potential_target in self.game_context.enemies:
            if not hasattr(potential_target, 'id') or not hasattr(potential_target, 'rect') or not hasattr(potential_target, 'alive'):
                print(f"DEBUG find_next_arc_target: Skipping potential target due to missing attributes: {potential_target}")
                continue

            print(f"DEBUG find_next_arc_target: Checking Enemy ID {potential_target.id}. Alive: {potential_target.alive}. In chain: {potential_target.id in self.hit_in_chain}.")
            
            if not potential_target.alive:
                print(f"DEBUG find_next_arc_target: Enemy ID {potential_target.id} is not alive.")
                continue
            if potential_target.id in self.hit_in_chain:
                print(f"DEBUG find_next_arc_target: Enemy ID {potential_target.id} already in hit_in_chain.")
                continue

            target_pos = pygame.math.Vector2(potential_target.rect.center)
            distance_sq = current_enemy_pos.distance_squared_to(target_pos)
            print(f"DEBUG find_next_arc_target: Enemy ID {potential_target.id} at {target_pos}, dist_sq: {distance_sq}")

            if distance_sq < min_distance_sq:
                min_distance_sq = distance_sq
                closest_enemy = potential_target
                print(f"DEBUG find_next_arc_target: New closest_enemy: ID {closest_enemy.id}, dist_sq: {min_distance_sq}")
        
        if closest_enemy:
            print(f"DEBUG find_next_arc_target: Selected arc target: ID {closest_enemy.id}")
        else:
            print("DEBUG find_next_arc_target: No suitable arc target found.")
        return closest_enemy

    def draw(self, surface):
        surface.blit(self.image, self.rect)