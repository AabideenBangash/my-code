import pygame
from math import sin, cos


class Tan(pygame.sprite.Sprite):

    def __init__(self, points: list[tuple[float, float]], shape_size: tuple[float, float], color: tuple[int, int, int]):
        super().__init__()
        self.image = pygame.surface.Surface(shape_size, pygame.SRCALPHA)

        pygame.draw.polygon(self.image, color, points)
        self.rect = self.image.get_rect()

        # Store the variable in case they are needed later on
        self.points = points
        self.shape_size = shape_size
        self.color = color

        self.been_scaled = False
        self.mask = pygame.mask.from_surface(self.image)
        self.edges = []
        self.compute_edges()

        self.was_colored = True
        self.old_points = self.points.copy()
        self.old_center = self.rect.center
        self.old_size = self.image.get_size()

    def draw(self, screen: pygame.surface.Surface, screen1: pygame.surface, offset: tuple[float, float]) -> None:
        surface = screen if self.been_scaled else screen1
        pos = (self.rect[0] - offset[0], self.rect[1] - offset[1]) if self.been_scaled else self.rect
        surface.blit(self.image, pos)

    def set_position(self, left: float, top: float):
        self.rect.top = top
        self.rect.left = left

    def scale(self, scaling_factor: float):
        if not self.been_scaled:
            self.points = list(map(lambda point: (point[0]*scaling_factor, point[1]*scaling_factor), self.points))
            new_size = self.image.get_size()
            new_size = (new_size[0]*scaling_factor, new_size[1]*scaling_factor)
            self.image = pygame.surface.Surface(new_size, pygame.SRCALPHA)
            pygame.draw.polygon(self.image, self.color, self.points)
            old_center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = old_center
            self.been_scaled = True
            self.shape_size = new_size
            self.mask = pygame.mask.from_surface(self.image)

    def zoom(self, zoom_factor: float):
        if self.been_scaled:
            self.points = list(map(lambda point: (point[0]*zoom_factor, point[1]*zoom_factor), self.points))
            new_size = self.image.get_size()
            new_size = (new_size[0]*zoom_factor, new_size[1]*zoom_factor)
            self.image = pygame.surface.Surface(new_size, pygame.SRCALPHA)
            pygame.draw.polygon(self.image, self.color, self.points)
            old_center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = old_center
            self.been_scaled = True
            self.shape_size = new_size
            self.mask = pygame.mask.from_surface(self.image)

    def make_black(self):
        if self.been_scaled:
            self.was_colored = False
            self.image = pygame.surface.Surface(self.shape_size)
            self.image.fill((255, 255, 255))
            self.image.set_colorkey((255, 255, 255))
            pygame.draw.polygon(self.image, (0, 0, 0), self.points)
            self.mask = pygame.mask.from_surface(self.image)

    def make_colored(self):
        if self.been_scaled:
            self.was_colored = True
            self.image = pygame.surface.Surface(self.shape_size)
            self.image.fill((0, 0, 0))
            self.image.set_colorkey((0, 0, 0))
            pygame.draw.polygon(self.image, self.color, self.points)
            self.mask = pygame.mask.from_surface(self.image)


    def rotate(self, angle: int):
        old_center = self.rect.center

        x_min = self.points[0][0]
        y_min = self.points[0][1]

        new_coordinates = list(map(lambda old_coord: ((old_coord[0] - x_min)*cos(angle) - (old_coord[1] - y_min)*sin(angle), (old_coord[1] - y_min)*cos(angle) + (old_coord[0] - x_min)*sin(angle)), self.points))
        x_min = min(list(map(lambda coord: coord[0], new_coordinates)))
        x_max = max(list(map(lambda coord: coord[0], new_coordinates)))
        y_min = min(list(map(lambda coord: coord[1], new_coordinates)))
        y_max = max(list(map(lambda coord: coord[1], new_coordinates)))
        if x_min < 0:
            new_coordinates = list(map(lambda old_coord: (old_coord[0] + abs(x_min), old_coord[1]), new_coordinates))
        if y_min < 0:
            new_coordinates = list(map(lambda old_coord: (old_coord[0], old_coord[1] + abs(y_min)), new_coordinates))

        self.image = pygame.surface.Surface((abs(x_min - x_max), abs(y_max - y_min)), pygame.SRCALPHA)
        #self.image.fill((80, 80, 80))
        self.rect = self.image.get_rect()
        self.rect.center = old_center
        pygame.draw.polygon(self.image, self.color, new_coordinates)
        self.points = new_coordinates.copy()
        self.shape_size = self.rect.size
        self.mask = pygame.mask.from_surface(self.image)

    def flip(self):
        old_center = self.rect.center
        new_coordinates = [(self.shape_size[0] - point[0], point[1]) for point in self.points]
        self.image = pygame.surface.Surface(self.shape_size, pygame.SRCALPHA)
        pygame.draw.polygon(self.image, self.color, new_coordinates)
        self.rect = self.image.get_rect()
        self.rect.center = old_center
        self.points = new_coordinates.copy()
        self.mask = pygame.mask.from_surface(self.image)

    def compute_edges(self):
        for i in range(len(self.points) - 1):
            new_edge = (self.points[i+1][0] - self.points[i][0], self.points[i+1][1] - self.points[i][1])
            self.edges.append(new_edge)
        # Add the last node, joins the last point to the last point
        size = len(self.points)-1
        new_edge = (self.points[size][0] - self.points[0][0], self.points[size][1] - self.points[0][1])
        self.edges.append(new_edge)

    def compute_edge_distance_to_center(self, edge: tuple[float, float]) -> tuple[float, float]:
        x_coord = edge[0]/2
        y_coord = edge[1]/2
        x_dist = self.rect.centerx + x_coord
        y_dist = self.rect.centery + y_coord
        ans = (x_dist, y_dist)

        return ans

    def make_red(self):
        self.image = pygame.surface.Surface(self.shape_size)
        self.image.fill((255, 255, 255))
        self.image.set_colorkey((255, 255, 255))
        pygame.draw.polygon(self.image, (255, 0, 0), self.points)
        self.mask = pygame.mask.from_surface(self.image)

    def restore_color(self):
        if self.was_colored:
            self.make_colored()
        else:
            self.make_black()

    def scale_for_testing(self, value):
        self.old_points = self.points.copy()
        self.old_center = self.rect.center
        self.old_size = self.image.get_size()
        self.points = list(map(lambda point: (point[0] * value, point[1] * value), self.points))
        new_size = self.image.get_size()
        new_size = (new_size[0] * value, new_size[1] * value)
        self.image = pygame.surface.Surface(new_size, pygame.SRCALPHA)
        pygame.draw.polygon(self.image, self.color, self.points)
        old_center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = old_center
        self.been_scaled = True
        self.shape_size = new_size
        self.mask = pygame.mask.from_surface(self.image)

    def restore_size(self):
        self.points = self.old_points.copy()
        new_size = self.old_size
        self.image = pygame.surface.Surface(new_size, pygame.SRCALPHA)
        pygame.draw.polygon(self.image, self.color, self.points)
        self.rect = self.image.get_rect()
        self.rect.center = self.old_center
        self.been_scaled = True
        self.shape_size = new_size
        self.mask = pygame.mask.from_surface(self.image)