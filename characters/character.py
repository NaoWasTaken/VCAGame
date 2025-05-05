import pygame

class Character(pygame.sprite.Sprite):
    def __init__(self, name, x, y, width, height, color):
        super().__init__()
        self.name = name
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.health = 100 # Base health, we can replace later with whatever we want
        self.speed = 5 # Base Movement speed, again can rework later
        self.cooldowns = {}

    def move(self, dx, dy):
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.kill() # Add actual death logic before this, this just removes the character

    def start_cooldown(self, ability_name, duration):
        self.cooldowns[ability_name] = duration

    def is_on_cooldown(self, ability_name):
        return ability_name in self.cooldowns and self.cooldowns[ability_name] > 0
    
    def update_cooldowns(self):
        for ability in list(self.cooldowns.keys()):
            self.cooldowns[ability] -= 1
            if self.cooldowns[ability] <= 0:
                del self.cooldowns[ability]
    
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
            