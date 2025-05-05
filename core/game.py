import pygame
from characters.mage import Mage # Will import all later, testing everything now as mage
from core.dungeon import Dungeon

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

    def handle_input(self, event):
        # Check if player quits
        if event.type == pygame.QUIT:
            self.running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q: # push q to quit for now
                self.running = False

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

        # Move along x-axis and check for collision
        if dx != 0:
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

        # Move along y-axis and check for collision
        if dy != 0:
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

        player.update_cooldowns()

    def render(self):
        # Draw everything on the screen
        self.screen.fill((0, 0, 0))  # Clear screen
        # Draw game elements here
        self.dungeon.draw(self.screen) # Draw Dungeon (Important that this is first)
        self.player.draw(self.screen) # Draw player

        pygame.display.flip() #Display Update