import pygame
from core.game import Game

# Initialize pygame
pygame.init()

base_width = 1920
base_height = 1080

info = pygame.display.Info()
screen_width = info.current_w
screen_height = info.current_h

screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
pygame.display.set_caption("My Roguelike Game")

# Initialize Game class from core/game.py
game = Game(screen)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        game.handle_input(event)
        if not game.running:
            running = False

    game.update()
    game.render()

pygame.quit()

pygame.quit()