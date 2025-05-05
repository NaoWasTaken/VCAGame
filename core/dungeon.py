import pygame

class Dungeon:
    def __init__(self, screen_width, screen_height, tile_size=32):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.tile_size = tile_size
        self.width_tiles = screen_width // tile_size
        self.height_tiles = screen_height // tile_size
        self.tiles = self.create_basic_dungeon()

    def create_basic_dungeon(self):
        # Create Dungeon Layout
        layout = []
        for y in range(self.height_tiles):
            row = []
            for x in range(self.width_tiles):
                # Simple hardcode
                if x == 0 or x == self.width_tiles - 1 or y == 0 or y == self.height_tiles - 1 or \
                   (x > self.width_tiles // 4 and x < 3 * self.width_tiles // 4 and y == self.height_tiles // 2):
                    row.append(1)  # Wall
                else:
                    row.append(0)  # Floor
            layout.append(row)
        return layout

    def draw(self, surface):
        for y, row in enumerate(self.tiles):
            for x, tile in enumerate(row):
                tile_rect = pygame.Rect(x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size)
                if tile == 1:  # Wall
                    pygame.draw.rect(surface, (100, 100, 100), tile_rect)
                elif tile == 0:  # Floor
                    pygame.draw.rect(surface, (50, 50, 50), tile_rect)