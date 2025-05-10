import pygame
from characters.character import Character
import random
import math

ENEMY_DEFAULT_COLOR = (255, 0, 0)
STUN_OUTLINE_COLOR = (0, 0, 255)
OUTLINE_THICKNESS = 2
HEALTH_BAR_HEIGHT = 5
HEALTH_BAR_Y_OFFSET = 8

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_id, width=30, height=30, health=30, speed=1, damage=10):
        super().__init__()

        self.id = enemy_id
        self.name = f"Enemy_{self.id}"

        self.width = width
        self.height = height

        self.original_image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.original_image.fill(ENEMY_DEFAULT_COLOR)
        
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(topleft=(x, y))
        
        # Stats
        self.health = health
        self.max_health = health
        self.speed = speed
        self.damage = damage
        self.alive = True
        
        # Stun mechanics
        self.stun_timer = 0
        self.is_stunned_by_lightning_visual = False

        self.movement_timer = 0
        self.movement_interval = random.randint(30, 90) 

    def apply_stun(self, duration_frames, is_lightning_stun=False):
        if not self.alive:
            return

        # Apply the longest stun duration if multiple stuns overlap
        self.stun_timer = max(self.stun_timer, duration_frames) 
        print(f"DEBUG: {self.name} stunned for {duration_frames} frames (Total stun timer: {self.stun_timer}). Lightning: {is_lightning_stun}")

        if is_lightning_stun:
            self.is_stunned_by_lightning_visual = True
            self._apply_stun_visual()
        elif self.stun_timer <= 0:
             self._remove_stun_visual()

    def _apply_stun_visual(self):
        if not self.is_stunned_by_lightning_visual:
            pass

        print(f"DEBUG: Applying stun visual for {self.name}")
        outlined_image_width = self.width + OUTLINE_THICKNESS * 2
        outlined_image_height = self.height + OUTLINE_THICKNESS * 2
        
        new_image = pygame.Surface((outlined_image_width, outlined_image_height), pygame.SRCALPHA)

        new_image.blit(self.original_image, (OUTLINE_THICKNESS, OUTLINE_THICKNESS))
 
        pygame.draw.rect(new_image, STUN_OUTLINE_COLOR, new_image.get_rect(), OUTLINE_THICKNESS)
        
        self.image = new_image

        current_center = self.rect.center
        self.rect = self.image.get_rect(center=current_center)

    def _remove_stun_visual(self):
        if self.is_stunned_by_lightning_visual or self.image is not self.original_image:
            print(f"DEBUG: Removing stun visual for {self.name}")
            self.image = self.original_image.copy()
            current_center = self.rect.center
            self.rect = self.image.get_rect(center=current_center)
        self.is_stunned_by_lightning_visual = False

    def update(self, player, dungeon, all_enemies_list):
        if not self.alive:
            return

        if self.stun_timer > 0:
            self.stun_timer -= 1
            if self.stun_timer == 0:
                print(f"DEBUG: {self.name} is no longer stunned (timer reached 0).")
                self._remove_stun_visual()
            return

        direction_x_to_player = player.rect.centerx - self.rect.centerx
        direction_y_to_player = player.rect.centery - self.rect.centery
        
        distance_to_player = math.sqrt(direction_x_to_player**2 + direction_y_to_player**2)

        move_x, move_y = 0, 0
        if distance_to_player > 0:
            move_x = (direction_x_to_player / distance_to_player) * self.speed
            move_y = (direction_y_to_player / distance_to_player) * self.speed

        original_rect_x = self.rect.x
        original_rect_y = self.rect.y

        self.rect.x += move_x
        if self.check_collision(dungeon, all_enemies_list):
            self.rect.x = original_rect_x

        self.rect.y += move_y
        if self.check_collision(dungeon, all_enemies_list):
            self.rect.y = original_rect_y

    def check_collision(self, dungeon, all_enemies_list):
        """
        Checks for collision with walls and other enemies.
        - dungeon: The dungeon object.
        - all_enemies_list: List of all other enemies.
        """
        # Wall collision (more efficient to check nearby tiles, but using existing logic for now)
        # Consider optimizing this if performance becomes an issue.
        for y_tile in range(dungeon.height_tiles):
            for x_tile in range(dungeon.width_tiles):
                if dungeon.tiles[y_tile][x_tile] == 1: # If it's a wall tile
                    wall_rect = pygame.Rect(x_tile * dungeon.tile_size, 
                                            y_tile * dungeon.tile_size, 
                                            dungeon.tile_size, 
                                            dungeon.tile_size)
                    if self.rect.colliderect(wall_rect):
                        return True # Collision with a wall detected
        
        # Collision with other enemies
        for other_enemy in all_enemies_list:
            if other_enemy is not self and other_enemy.alive: # Don't check against self, only alive enemies
                if self.rect.colliderect(other_enemy.rect):
                    return True # Collision with another enemy detected
        return False # No collision detected

    def take_damage(self, amount):
        """Applies damage to the enemy and handles death."""
        if not self.alive:
            return
            
        self.health -= amount
        print(f"DEBUG: {self.name} took {amount} damage! Health: {self.health}/{self.max_health}")
        
        if self.health <= 0:
            self.health = 0 # Prevent negative health
            self.alive = False
            print(f"DEBUG: {self.name} has died!")
            self.kill() # Crucial: Removes sprite from all Pygame groups it's in

    def draw(self, surface):
        """Draws the enemy and its health bar to the given surface."""
        if self.alive:
            # CORRECTED: Draw self.image, which will be the original or the stun-outlined version
            surface.blit(self.image, self.rect)
            
            # Draw health bar above the enemy
            if self.health < self.max_health: # Optionally, only show if not at full health
                # Health bar dimensions and position
                bar_width_เต็ม = self.rect.width 
                bar_current_width = int(bar_width_เต็ม * (self.health / self.max_health))
                
                bar_pos_x = self.rect.left
                bar_pos_y = self.rect.top - HEALTH_BAR_Y_OFFSET # Position above the enemy
                
                # Background of health bar (e.g., dark red for missing health portion)
                pygame.draw.rect(surface, (100, 0, 0), 
                                 (bar_pos_x, bar_pos_y, bar_width_เต็ม, HEALTH_BAR_HEIGHT))
                # Foreground of health bar (green for current health)
                if bar_current_width > 0:
                    pygame.draw.rect(surface, (0, 200, 0), 
                                     (bar_pos_x, bar_pos_y, bar_current_width, HEALTH_BAR_HEIGHT))