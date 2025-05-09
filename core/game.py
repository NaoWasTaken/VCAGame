import pygame
import random
from characters.mage import Mage # Will import all later, testing everything now as mage
from core.dungeon import Dungeon
from characters.enemies import Enemy
from core.projectile import Projectile, VoidHoleProjectile, FireballProjectile # Ensure VoidHoleProjectile is imported

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.running = True
        # We will initialize game state and objects here
        self.tile_size = 32
        self.dungeon = Dungeon(screen.get_width(), screen.get_height(), self.tile_size)
        self.player = Mage(0, 0) # Initialize player with a default position first, otherwise find_spawn_location breaks T-T
        self.player_start_x, self.player_start_y = self.find_spawn_location()
        self.player.rect.topleft = (self.player_start_x, self.player_start_y)
        self.enemies = []  # List of enemies
        self.spawn_enemies(5) # Can add spawn logic later
        self.projectiles = pygame.sprite.Group() # Sprites for projectiles
        self.player_damage_cooldown = 0
        self.active_aoe_effects = pygame.sprite.Group() # Void hole

    def find_spawn_location(self): # Necessary, otherwise player can spawn in walls LOL
        center_x = self.dungeon.width_tiles // 2
        center_y = self.dungeon.height_tiles // 2
        search_radius = 0

        while True:
            for i in range(max(0, center_y - search_radius), min(self.dungeon.height_tiles, center_y + search_radius + 1)):
                for j in range(max(0, center_x - search_radius), min(self.dungeon.width_tiles, center_x + search_radius + 1)):
                    if self.dungeon.tiles[i][j] == 0:
                        spawn_x = j * self.dungeon.tile_size
                        spawn_y = i * self.dungeon.tile_size
                        return spawn_x, spawn_y
            search_radius += 1
            if search_radius > max(self.dungeon.width_tiles, self.dungeon.height_tiles):
                break  # Prevents infinite loops later on
        return self.screen.get_width() // 2 - self.tile_size // 2, self.screen.get_height() // 2 - self.tile_size // 2
    
    def spawn_enemies(self, num_enemies):
        for _ in range(num_enemies):
            spawn_x, spawn_y = self.find_valid_spawn_location()
            if spawn_x is not None and spawn_y is not None:
                self.enemies.append(Enemy(spawn_x, spawn_y))

    def find_valid_spawn_location(self): # Enemy spawns
        attempts = 0
        max_attempts = 100  # Prevent infinite loops
        while attempts < max_attempts:
            random_x_tile = random.randint(0, self.dungeon.width_tiles - 1)
            random_y_tile = random.randint(0, self.dungeon.height_tiles - 1)
            if self.dungeon.tiles[random_y_tile][random_x_tile] == 0:  # Checks for floor tile
                spawn_x = random_x_tile * self.dungeon.tile_size
                spawn_y = random_y_tile * self.dungeon.tile_size
                # Ensure player rect is valid before calculating distance
                if hasattr(self.player, 'rect') and self.player.rect:
                    if pygame.math.Vector2(spawn_x, spawn_y).distance_to(self.player.rect.topleft) > self.tile_size * 3: # Makes sure enemy doesn't spawn on top of player
                        return spawn_x, spawn_y
                else: # Fallback if player rect isn't ready (should ideally not happen here)
                    return spawn_x, spawn_y 
            attempts += 1
        return None, None # Failed to find a valid spawn location

    def handle_input(self, event):
        # Check if player quits
        if event.type == pygame.QUIT:
            self.running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False
        
        # Process other inputs only if the player is alive
        if not self.player.alive:
            return 
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z:
                mouse_position = pygame.mouse.get_pos() 
                print("DEBUG: 'Z' key pressed for Fireball.")
                self.player.use_ability(
                    ability_name="fireball",
                    target=mouse_position,
                    game_context=self
                )
            if event.key == pygame.K_x:
                print("DEBUG: 'X' key pressed for Heal.")
                self.player.use_ability(
                    ability_name="heal",
                    game_context=self
                )
            if event.key == pygame.K_c:
                mouse_position = pygame.mouse.get_pos()
                print("DEBUG: 'C' key pressed for Void Hole.")
                self.player.use_ability(
                    ability_name="void_hole",
                    target=mouse_position,
                    game_context=self
                )
                
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Left mouse click (basic attack)
                target_x, target_y = pygame.mouse.get_pos()
                print("DEBUG: Left Mouse Button pressed for basic projectile.")
                projectile = Projectile(
                    self.player.rect.centerx,
                    self.player.rect.centery,
                    target_x,
                    target_y,
                    10,  # Basic attack damage
                    self.player,
                    self.dungeon
                )
                self.projectiles.add(projectile)

    def update(self):
        keys = pygame.key.get_pressed()
        player = self.player
        dungeon = self.dungeon
        tile_size = dungeon.tile_size

        if self.player.alive:
            dx = 0
            dy = 0
            
            left = keys[pygame.K_a] or keys[pygame.K_LEFT]
            right = keys[pygame.K_d] or keys[pygame.K_RIGHT]
            up = keys[pygame.K_w] or keys[pygame.K_UP]
            down = keys[pygame.K_s] or keys[pygame.K_DOWN]
            
            direction = pygame.math.Vector2(right - left, down - up)
            if direction.length_squared() > 0:
                direction.scale_to_length(player.speed)
                dx, dy = direction

            # Player collision detection
            player.rect.x += dx
            for y_idx in range(dungeon.height_tiles):
                for x_idx in range(dungeon.width_tiles):
                    if dungeon.tiles[y_idx][x_idx] == 1:
                        wall_rect = pygame.Rect(x_idx * tile_size, y_idx * tile_size, tile_size, tile_size)
                        if player.rect.colliderect(wall_rect):
                            if dx > 0:
                                player.rect.right = wall_rect.left
                            elif dx < 0:
                                player.rect.left = wall_rect.right
                            break 
                else: 
                    continue
                break

            player.rect.y += dy
            for y_idx in range(dungeon.height_tiles):
                for x_idx in range(dungeon.width_tiles):
                    if dungeon.tiles[y_idx][x_idx] == 1:
                        wall_rect = pygame.Rect(x_idx * tile_size, y_idx * tile_size, tile_size, tile_size)
                        if player.rect.colliderect(wall_rect):
                            if dy > 0:
                                player.rect.bottom = wall_rect.top
                            elif dy < 0:
                                player.rect.top = wall_rect.bottom
                            break
                else:
                    continue
                break
            
            player.update_cooldowns()

        projectiles_to_process = list(self.projectiles) 
        for projectile in projectiles_to_process:
            if not projectile.alive():
                continue
            last_known_center = projectile.rect.center
            projectile.update() 
            
            if not projectile.alive(): 
                if isinstance(projectile, FireballProjectile): 
                    if hasattr(projectile, 'is_exploding_on_impact') and projectile.is_exploding_on_impact:
                        print(f"DEBUG Game.update: Fireball hit a wall (killed by update) - exploding at {last_known_center}")
                        projectile.explode(self.enemies, last_known_center) 
                continue 
                
            enemies_hit_by_projectile = pygame.sprite.spritecollide(projectile, self.enemies, False, pygame.sprite.collide_rect)
            if enemies_hit_by_projectile:
                main_target_enemy = enemies_hit_by_projectile[0]
                if main_target_enemy.alive:
                    print(f"DEBUG Game.update: Projectile directly hit {main_target_enemy.name} for {projectile.damage} damage.")
                    main_target_enemy.take_damage(projectile.damage)
                if isinstance(projectile, FireballProjectile): 
                    impact_location = main_target_enemy.rect.center 
                    print(f"DEBUG Game.update: Fireball hit an enemy - exploding at {impact_location}")
                    projectile.explode(self.enemies, impact_location) 
                projectile.kill()

        if hasattr(self, 'active_aoe_effects'):
            print(f"DEBUG Game.update: Updating active_aoe_effects. Count: {len(self.active_aoe_effects)}") 
            for effect in list(self.active_aoe_effects):
                print(f"DEBUG Game.update: Processing AOE effect: {type(effect).__name__} at {effect.rect.center if hasattr(effect, 'rect') else 'N/A'}") 
                
                if isinstance(effect, VoidHoleProjectile): 
                     print(f"DEBUG Game.update: VoidHole state: {effect.state if hasattr(effect, 'state') else 'N/A'}, is_active_effect_flag: {effect.is_active_effect if hasattr(effect, 'is_active_effect') else 'N/A'}")

                if hasattr(effect, 'update'):
                    print(f"DEBUG Game.update: Calling update for AOE effect: {type(effect).__name__}") 
                    effect.update(self.enemies, self.dungeon.tiles, self.dungeon.tile_size)
        else:
            print("DEBUG Game.update: self.active_aoe_effects group does NOT exist.") 

        for enemy in self.enemies:
            if enemy.alive:
                enemy.update(self.player, self.dungeon, self.enemies)

        self.enemies = [enemy for enemy in self.enemies if enemy.alive]

        if player.alive:
            if self.player_damage_cooldown <= 0:
                for enemy in self.enemies:
                    if player.rect.colliderect(enemy.rect):
                        player.take_damage(enemy.damage)
                        self.player_damage_cooldown = 50 
                        if not player.alive: 
                            print("GAME OVER - Mage has been defeated.")
                        break
        if self.player_damage_cooldown > 0:
            self.player_damage_cooldown -= 1

    def render(self):
        self.screen.fill((0, 0, 0)) 
        self.dungeon.draw(self.screen)
        if self.player.alive:
            self.player.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen)
        
        self.projectiles.draw(self.screen) 

        if hasattr(self, 'active_aoe_effects'):
            print(f"DEBUG Game.render: Drawing active_aoe_effects. Count: {len(self.active_aoe_effects)}") 
            if len(self.active_aoe_effects) > 0:
                first_effect = self.active_aoe_effects.sprites()[0]
                rect_info = first_effect.rect if hasattr(first_effect, 'rect') else 'No Rect'
                image_info = first_effect.image if hasattr(first_effect, 'image') else 'No Image'
                if image_info is not None and hasattr(image_info, 'get_size'):
                    image_info_str = f"Surface {image_info.get_size()}"
                elif image_info is None:
                    image_info_str = "Image is None"
                else:
                    image_info_str = "Image is not a Surface"

                print(f"DEBUG Game.render: First AOE effect rect: {rect_info}, image: {image_info_str}") 
            self.active_aoe_effects.draw(self.screen) 
        else:
            print("DEBUG Game.render: self.active_aoe_effects group does NOT exist for drawing.") 
        
        pygame.display.flip()
