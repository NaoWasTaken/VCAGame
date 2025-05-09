import pygame
from characters.character import Character
import random
import math

class Enemy(Character):
    def __init__(self, x, y):
        super().__init__("Enemy", x, y, 32, 32, (255, 0, 0)) # Size (Color)
        self.speed = 1
        self.movement_timer = 0
        self.movement_interval = random.randint(30, 90)  # Moves every x frames
        self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]) # Initial random direction
        self.health = 30  # Initial health
        self.max_health = 30 # Store max health
        self.damage = 10  #Enemy damage value
        self.target_x = None
        self.target_y = None

    def update(self, player, dungeon, enemies):
        direction_x = player.rect.x - self.rect.x
        direction_y = player.rect.y - self.rect.y
        distance = (direction_x**2 + direction_y**2)**0.5
        if distance > 0:
            direction_x /= distance
            direction_y /= distance

        original_x = self.rect.x
        original_y = self.rect.y

        moved = False

        # General Pathfinding? (DEFINITLEY needs refined)
        self.rect.x += direction_x * self.speed
        collision = self.check_collision(dungeon, enemies)
        if collision:
            self.rect.x = original_x
            self.rect.x += self.speed if direction_y > 0 else -self.speed
            if not self.check_collision(dungeon, enemies):
                moved = True
            else:
                self.rect.x = original_x

        if not moved:
            self.rect.y += direction_y * self.speed
            collision = self.check_collision(dungeon, enemies)
            if collision:
                self.rect.y = original_y
                self.rect.y += self.speed if direction_x > 0 else -self.speed
                if not self.check_collision(dungeon, enemies):
                    moved = True
                else:
                    self.rect.y = original_y

    def check_collision(self, dungeon, enemies):
        for y in range(dungeon.height_tiles):
            for x in range(dungeon.width_tiles):
                if dungeon.tiles[y][x] == 1:
                    wall_rect = pygame.Rect(x * dungeon.tile_size, y * dungeon.tile_size, dungeon.tile_size, dungeon.tile_size)
                    if self.rect.colliderect(wall_rect):
                        return True
        # Check for collision with other enemies
        for other_enemy in enemies:
            if other_enemy != self and self.rect.colliderect(other_enemy.rect):
                return True
        return False
    
    def draw(self, surface): # Make this better with Chara's art
           pygame.draw.rect(surface, (255,0,0), self.rect)
           # draw health bar
           health_bar_width = (self.health / self.max_health) * self.rect.width
           pygame.draw.rect(surface, (0,255,0), (self.rect.x, self.rect.y - 5, health_bar_width, 5))

    def attack(self, target):
        print(f"{self.name} attacks {target.name}!")
        # Add attack logic here

    def take_damage(self, damage):
        self.health -= damage
        print(f"{self.name} took {damage} damage!")
        if self.health <= 0:
            self.health = 0 # Prevent negative health display
            self.kill()
            self.alive = False
            print(f"{self.name} has died!")