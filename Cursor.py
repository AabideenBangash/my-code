import pygame

class Cursor(pygame.sprite.Sprite):
    def __init__(self, radius: int):
        super().__init__()
        self.image = pygame.surface.Surface((2*radius, 2*radius), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 255, 255), self.image.get_rect().center, radius)
        self.rect = self.image.get_rect()

    def update(self):
        self.rect.center = pygame.mouse.get_pos()

    def draw(self, screen: pygame.surface.Surface):
        screen.blit(self.image, self.rect)