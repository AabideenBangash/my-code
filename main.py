from Game import Game
import pygame
pygame.init()

SCREEN_SIZE = (1100, 750)

screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("Tangram")

Tangram = Game(screen)
Tangram.run_game()

pygame.quit()
