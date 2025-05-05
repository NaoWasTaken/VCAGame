import pygame
from characters.character import Character
import random

class Enemy(Character):
    def __init__(self, x, y):
        super().__init__("Enemy", x, y, 32, 32, (255, 0, 0)) # Size (Color)
        self.speed = 1
        self.movement_timer = 0
        self.movement_interval = random.randint(30, 90)  # Moves every x frames
        self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]) # Initial random direction

    def update(self, player):
        # Get the direction vector towards the player
        direction_x = player.rect.x - self.rect.x
        direction_y = player.rect.y - self.rect.y

        # Normalize the direction vector (get a unit vector)
        distance = (direction_x**2 + direction_y**2)**0.5
        if distance > 0:
            direction_x /= distance
            direction_y /= distance

        # Move towards the player
        self.move(direction_x, direction_y)

    def attack(self, target):
        print(f"{self.name} attacks {target.name}!")
        # Add attack logic here