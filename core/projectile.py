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
