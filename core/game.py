import pygame
from characters.mage import Mage # Will import all later, testing everything now as mage
from core.dungeon import Dungeon

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.running = True
        # We will initialize game state and objects here
        self.player = Mage(screen.get_width() // 2 - 16, screen.get_height() // 2 - 16)
        self.tile_size = 32  # Keep this consistent with Dungeon
        self.dungeon = Dungeon(screen.get_width(), screen.get_height(), self.tile_size)

    def handle_input(self, event):
        # Check if player quits
        if event.type == pygame.QUIT:
            self.running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q: # push q to quit for now
                self.running = False

    def update(self):
        # Gets pressed keys
        keys = pygame.key.get_pressed()

        # Movement
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.player.move(-1, 0)
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.player.move(1, 0)
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.player.move(0, -1)
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.player.move(0, 1)

        # Abilities
        if keys[pygame.K_z]:
            self.player.cast_fireball(self.player)
        if keys[pygame.K_x]:
            self.player.cast_healthspell()

        self.player.update_cooldowns()

        # Update cooldowns
        self.player.update_cooldowns()

    def render(self):
        # Draw everything on the screen
        self.screen.fill((0, 0, 0))  # Clear screen
        # Draw game elements here
        self.dungeon.draw(self.screen) # Draw Dungeon (Important that this is first)
        self.player.draw(self.screen) # Draw player

        pygame.display.flip() #Display Update