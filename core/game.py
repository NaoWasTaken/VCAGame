import pygame
import random
from characters.mage import Mage
from core.dungeon import Dungeon
from characters.enemies import Enemy # Ensure this is the updated Enemy class
from core.projectile import Projectile, VoidHoleProjectile, FireballProjectile, LightningProjectile

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.running = True
        self.tile_size = 32
        self.dungeon = Dungeon(screen.get_width(), screen.get_height(), self.tile_size)

        self.player = Mage(0, 0) 
        player_start_x, player_start_y = self.find_spawn_location()
        if player_start_x is not None and player_start_y is not None:
            self.player.rect.topleft = (player_start_x, player_start_y)
        else:
            self.player.rect.topleft = (screen.get_width() // 2, screen.get_height() // 2)
            print("Warning: Player spawn location not found, defaulting to center.")

        # Initialize enemies
        self.enemies = []
        self.next_enemy_id = 0 
        self.spawn_enemies(5) 
        
        # Projectile and effects groups
        self.projectiles = pygame.sprite.Group() 
        self.active_aoe_effects = pygame.sprite.Group() 

        # Game state variables
        self.player_damage_cooldown = 0
        self.player_damage_cooldown_duration = 60

        print("Game initialized.")

    def find_spawn_location(self):
        center_x_tile = self.dungeon.width_tiles // 2
        center_y_tile = self.dungeon.height_tiles // 2
        search_radius = 0

        while True:
            for i_offset in range(-search_radius, search_radius + 1):
                for j_offset in range(-search_radius, search_radius + 1):
                    if abs(i_offset) < search_radius and abs(j_offset) < search_radius and search_radius > 0:
                        continue

                    check_y_tile = center_y_tile + i_offset
                    check_x_tile = center_x_tile + j_offset

                    if 0 <= check_y_tile < self.dungeon.height_tiles and \
                       0 <= check_x_tile < self.dungeon.width_tiles:
                        if self.dungeon.tiles[check_y_tile][check_x_tile] == 1: 
                            return check_x_tile * self.dungeon.tile_size, check_y_tile * self.dungeon.tile_size
            
            search_radius += 1
            if search_radius > max(self.dungeon.width_tiles, self.dungeon.height_tiles): 
                print("Warning: Could not find player spawn location after extensive search.")
                return None, None 
        return None, None 

    def spawn_enemies(self, num_enemies):
        for _ in range(num_enemies):
            spawn_x, spawn_y = self.find_valid_spawn_location_for_enemy()
            if spawn_x is not None and spawn_y is not None:
                new_enemy = Enemy(x=spawn_x, y=spawn_y, enemy_id=self.next_enemy_id) 
                self.enemies.append(new_enemy) 
                self.next_enemy_id += 1
                print(f"Spawned {new_enemy.name} at ({spawn_x}, {spawn_y})")
            else:
                print("Warning: Could not find a valid spawn location for an enemy.")

    def find_valid_spawn_location_for_enemy(self):
        max_attempts = 100
        for _ in range(max_attempts):
            random_x_tile = random.randint(0, self.dungeon.width_tiles - 1)
            random_y_tile = random.randint(0, self.dungeon.height_tiles - 1)
            
            if self.dungeon.tiles[random_y_tile][random_x_tile] == 1: 
                spawn_x = random_x_tile * self.dungeon.tile_size
                spawn_y = random_y_tile * self.dungeon.tile_size
                
                min_dist_from_player = self.tile_size * 4 
                player_pos = pygame.math.Vector2(self.player.rect.center)
                enemy_spawn_pos = pygame.math.Vector2(spawn_x + self.tile_size / 2, spawn_y + self.tile_size / 2)
                
                if player_pos.distance_to(enemy_spawn_pos) > min_dist_from_player:
                    return spawn_x, spawn_y
        return None, None 

    def handle_input(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False
        
        if not self.player.alive: 
            return 
        
        if event.type == pygame.KEYDOWN:
            mouse_pos = pygame.mouse.get_pos() 
            if event.key == pygame.K_z:
                self.player.use_ability(ability_name="fireball", target=mouse_pos, game_context=self)
            elif event.key == pygame.K_x:
                self.player.use_ability(ability_name="heal", game_context=self) 
            elif event.key == pygame.K_c:
                self.player.use_ability(ability_name="void_hole", target=mouse_pos, game_context=self)
            elif event.key == pygame.K_v:
                self.player.use_ability(ability_name="lightning_storm", target=mouse_pos, game_context=self)
                
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: 
                mouse_pos = pygame.mouse.get_pos()
                basic_projectile = Projectile(
                    x=self.player.rect.centerx,
                    y=self.player.rect.centery,
                    target_x=mouse_pos[0],
                    target_y=mouse_pos[1],
                    damage=10, 
                    owner=self.player,
                    dungeon=self.dungeon
                )
                self.projectiles.add(basic_projectile)
                print(f"DEBUG: Player basic attack projectile created towards {mouse_pos}")


    def update(self):
        if not self.running:
            return

        keys = pygame.key.get_pressed()

        if self.player.alive:
            dx, dy = 0, 0
            left = keys[pygame.K_a] or keys[pygame.K_LEFT]
            right = keys[pygame.K_d] or keys[pygame.K_RIGHT]
            up = keys[pygame.K_w] or keys[pygame.K_UP]
            down = keys[pygame.K_s] or keys[pygame.K_DOWN]

            movement_vector = pygame.math.Vector2(right - left, down - up)
            if movement_vector.length_squared() > 0:
                movement_vector.scale_to_length(self.player.speed)
                dx, dy = movement_vector.x, movement_vector.y

            original_player_x = self.player.rect.x
            original_player_y = self.player.rect.y

            self.player.rect.x += dx
            for y_tile in range(self.dungeon.height_tiles):
                for x_tile in range(self.dungeon.width_tiles):
                    if self.dungeon.tiles[y_tile][x_tile] == 0:
                        wall_rect = pygame.Rect(x_tile * self.tile_size, y_tile * self.tile_size, self.tile_size, self.tile_size)
                        if self.player.rect.colliderect(wall_rect):
                            if dx > 0:
                                self.player.rect.right = wall_rect.left
                            elif dx < 0:
                                self.player.rect.left = wall_rect.right
                            dx = 0
                            break
                if dx == 0 and self.player.rect.x != original_player_x :
                    break 

            self.player.rect.y += dy
            for y_tile in range(self.dungeon.height_tiles):
                for x_tile in range(self.dungeon.width_tiles):
                    if self.dungeon.tiles[y_tile][x_tile] == 0:
                        wall_rect = pygame.Rect(x_tile * self.tile_size, y_tile * self.tile_size, self.tile_size, self.tile_size)
                        if self.player.rect.colliderect(wall_rect):
                            if dy > 0:
                                self.player.rect.bottom = wall_rect.top
                            elif dy < 0:
                                self.player.rect.top = wall_rect.bottom
                            dy = 0
                            break
                if dy == 0 and self.player.rect.y != original_player_y:
                    break

            self.player.update_cooldowns()

        for projectile in list(self.projectiles): 
            if not projectile.alive(): 
                self.projectiles.remove(projectile) 
                continue
            
            last_known_center = projectile.rect.center 

            if isinstance(projectile, VoidHoleProjectile):
                projectile.update(self.enemies, self.dungeon.tiles, self.dungeon.tile_size)
            else:
                projectile.update() 

            if not projectile.alive():
                if isinstance(projectile, FireballProjectile): 
                    if hasattr(projectile, 'is_exploding_on_impact') and projectile.is_exploding_on_impact:
                        print(f"DEBUG Game.update: Fireball (killed by its update) - exploding at {last_known_center}")
                        projectile.explode(self.enemies, last_known_center)
                self.projectiles.remove(projectile) 
                continue 
            
            if not isinstance(projectile, (LightningProjectile, VoidHoleProjectile)):
                enemies_hit = pygame.sprite.spritecollide(projectile, self.enemies, False, pygame.sprite.collide_rect)
                if enemies_hit:
                    target_enemy = enemies_hit[0] 
                    if target_enemy.alive:
                        print(f"DEBUG Game.update: GENERIC projectile ({type(projectile).__name__}) hit {target_enemy.name}")
                        target_enemy.take_damage(projectile.damage)
                    
                    if isinstance(projectile, FireballProjectile):
                        print(f"DEBUG Game.update: Fireball (hit enemy via spritecollide) - exploding at {target_enemy.rect.center}")
                        projectile.explode(self.enemies, target_enemy.rect.center)
                    
                    if not isinstance(projectile, FireballProjectile) or not projectile.is_exploding_on_impact:
                         projectile.kill() 

        for effect in list(self.active_aoe_effects): 
            if not effect.alive():
                self.active_aoe_effects.remove(effect)
                continue

            if isinstance(effect, VoidHoleProjectile): 
                effect.update(self.enemies, self.dungeon.tiles, self.dungeon.tile_size)
            
            if not effect.alive(): 
                self.active_aoe_effects.remove(effect)

        for enemy in list(self.enemies): 
            if enemy.alive:
                enemy.update(self.player, self.dungeon, self.enemies)
            else: 
                if enemy in self.enemies: 
                    self.enemies.remove(enemy)
                    print(f"DEBUG: Removed dead {enemy.name} from game enemy list.")

        if self.player.alive:
            if self.player_damage_cooldown > 0:
                self.player_damage_cooldown -= 1
            else:
                for enemy in self.enemies: 
                    if enemy.alive and self.player.rect.colliderect(enemy.rect):
                        print(f"DEBUG: Player collided with {enemy.name}")
                        self.player.take_damage(enemy.damage) 
                        self.player_damage_cooldown = self.player_damage_cooldown_duration
                        if not self.player.alive: 
                            print("GAME OVER - Player has been defeated.")
                        break 

    def render(self):
        self.screen.fill((10, 10, 20)) 
        
        self.dungeon.draw(self.screen)
        
        if self.player.alive:
            self.player.draw(self.screen)
            
        for enemy in self.enemies: 
            if enemy.alive: 
                enemy.draw(self.screen)
        
        self.projectiles.draw(self.screen) 

        self.active_aoe_effects.draw(self.screen)
        for effect in self.active_aoe_effects: 
            if hasattr(effect, 'draw_debug'):
                effect.draw_debug(self.screen)
        
        pygame.display.flip()
