import pygame
import random
from characters.mage import Mage # Will import all later, testing everything now as mage
from core.dungeon import Dungeon
from characters.enemies import Enemy
from core.projectile import Projectile

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
        self.spawn_enemies(3) # Can add spawn logic later
        self.projectiles = pygame.sprite.Group() # Sprites for projectiles

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
                if pygame.math.Vector2(spawn_x, spawn_y).distance_to(self.player.rect.topleft) > self.tile_size * 3: # Makes sure enemy doesn't spawn on top of player
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
            if event.key == pygame.K_z:
                self.player.cast_fireball(self.player)
            if event.key == pygame.K_x:
                self.player.cast_healthspell()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                target_x, target_y = pygame.mouse.get_pos()
                projectile = Projectile(
                    self.player.rect.centerx,  # Start from player's center
                    self.player.rect.centery,
                    target_x,
                    target_y,
                    10,  # Test damage
                    self.player,
                    self.dungeon
                )
                self.projectiles.add(projectile)  # Add to the sprite group
                #self.player.basic_attack(self.player) # Removed basic attack.

    def update(self):
        keys = pygame.key.get_pressed()
        player = self.player
        dungeon = self.dungeon
        tile_size = dungeon.tile_size

        dx = 0
        dy = 0

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -player.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = player.speed
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -player.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = player.speed

        # Player collision detection
        player.rect.x += dx
        for y in range(dungeon.height_tiles):
            for x in range(dungeon.width_tiles):
                if dungeon.tiles[y][x] == 1:
                    wall_rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)
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
        for y in range(dungeon.height_tiles):
            for x in range(dungeon.width_tiles):
                if dungeon.tiles[y][x] == 1:
                    wall_rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)
                    if player.rect.colliderect(wall_rect):
                        if dy > 0:
                            player.rect.bottom = wall_rect.top
                        elif dy < 0:
                            player.rect.top = wall_rect.bottom
                        break
            else:
                continue
            break

        for enemy in self.enemies:
            enemy.update(self.player, self.dungeon, self.enemies)

        player.update_cooldowns()
        self.projectiles.update()  # Update all projectiles

        # Projectile-enemy collision detection
        for projectile in self.projectiles:
            collisions = pygame.sprite.spritecollide(projectile, self.enemies, False) # dokill=False
            for enemy in collisions:
                enemy.take_damage(projectile.damage)
                projectile.kill()  # Remove projectile after collision

        self.enemies = [enemy for enemy in self.enemies if enemy.health > 0]

    def render(self):
        # Draw everything on the screen
        self.screen.fill((0, 0, 0))  # Clear screen
        # Draw game elements here
        self.dungeon.draw(self.screen) # Draw Dungeon (Important that this is first)
        self.player.draw(self.screen) # Draw player
        for enemy in self.enemies: # Draw enemies
            enemy.draw(self.screen)
        self.projectiles.draw(self.screen)

        pygame.display.flip() #Display Update