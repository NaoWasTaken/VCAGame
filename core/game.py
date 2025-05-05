import pygame
from characters.mage import Mage # Will import all later, testing everything now as mage

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.running = True
        self.player = Mage(screen.get_width() // 2 - 16, screen.get_height() // 2 - 16) # Starting as mage to test
        # We will initialize game state and objects here

    def handle_input(self, event):
        # These are examples, process events like key presses and mouse clicks
        if event.type == pygame.QUIT:
            self.running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
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
        self.player.draw(self.screen) # Draw player
        # Draw game elements here


        pygame.display.flip() #Display Update