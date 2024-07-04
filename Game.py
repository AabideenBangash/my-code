import time
import pygame
from Tan import Tan
from Cursor import Cursor
from PIL import Image
from math import pi
import os
import random
import math

class Game:
    def __init__(self, screen: pygame.surface.Surface):
        self.size = screen.get_size()
        self.screen = screen
        
        self.save_dir = "./"
        self.is_random_tangram = False
        self.random_tangram_save_dir = "./random_tangrams/"
        self.pending_save = False

        # Define points representing all the tans, their sizes and colors
        self.tans_information = [
            {"name": "Big Triangle", "points": [(0, 0), (100, 0), (50, 50)], "size": (100, 50), "color": (200, 0, 54), "scaling_factor": 1},
            {"name": "Small Triangle", "points": [(0, 0), (25, 25), (0, 50)], "size": (25, 50), "color": (6, 208, 1), "scaling_factor": 1},
            {"name": "Medium Triangle", "points": [(50, 0), (50, 100), (0, 50)], "size": (50, 100), "color": (53, 114, 239), "scaling_factor": 1},
            {"name": "Parallelogram", "points": [(25, 0), (50, 25), (0, 25)], "size": (50, 25), "color": (239, 156, 102), "scaling_factor": 1},
            {"name": "Square", "points": [(0, 0), (0, 50), (50, 50)], "size": (50, 50), "color": (188, 90, 148), "scaling_factor": 1},
            {"name": "Trapezoid", "points": [(0, 0), (50, 0), (75, 25), (25, 25)], "size": (75, 25), "color": (255, 219, 0), "scaling_factor": 1},
            {"name": "Rhombus", "points": [(25, 0), (50, 25), (25, 50), (0, 25)], "size": (50, 50), "color": (111, 220, 227), "scaling_factor": 1}
        ]

        self.tans_group = pygame.sprite.Group()
        # Create the tans
        self.tan_scaling_factor = 2
        self.tans = list(map(lambda tan_info: Tan(tan_info["points"], tan_info["size"], tan_info["color"]), self.tans_information))
        for tan in self.tans:
            tan.set_position(30 + self.tans.index(tan) * 130, 10)
            self.tans_group.add(tan)

        # Define game control variables
        self.running = True
        self.game_clock = pygame.time.Clock()
        self.FPS = 60
        pygame.event.clear()
        self.events = pygame.event.get()

        # Create a cursor object, used for moving tans around the screen
        self.cursor = Cursor(2)
        self.locked = False
        self.current_tan = None

        # Create the image view
        self.image_view = pygame.surface.Surface((0.55*self.size[0], 0.55*self.size[0]), pygame.SRCALPHA)
        self.image_view_position = self.image_view.get_rect()
        self.image_view_position.left = 0.1*self.size[0]
        self.image_view_position.top = 0.22*self.size[1]
        self.tan_offset = (self.image_view_position.left, self.image_view_position.top)

        # Create the control panel
        self.control_panel = pygame.surface.Surface((0.20 * self.size[0], 0.7 * self.size[1]), pygame.SRCALPHA)
        self.control_panel.fill((230, 230, 230))
        self.control_panel_position = self.control_panel.get_rect()
        self.control_panel_position.left = 0.75*self.size[0]
        self.control_panel_position.top = 0.24*self.size[1]

        # Create the controls that go onto the control panel
        self.icon_size = (60, 60)
        self.icons_list = ['change_color', 'save', 'reset', 'random']
        self.icon_positions = [(10, 10), (100, 10), (10, 100), (100, 100)]
        self.functions = [self.change_color, self.save_as_image, self.reset, self.generate_random_tangram]
        self.icon_width = 60
        self.tan_colored = True
        for i in range(len(self.icons_list)):
            image_icon = pygame.image.load(f'./assets/icons/{self.icons_list[i]}.png').convert_alpha()
            image_icon = pygame.transform.scale(image_icon, self.icon_size)
            pos = image_icon.get_rect()
            pos.left = self.icon_positions[i][0]
            pos.top = self.icon_positions[i][1]
            self.control_panel.blit(image_icon, pos)

        # Create the notification bar
        self.notification_bar = pygame.surface.Surface((0.8*self.size[0], 0.035*self.size[1]), pygame.SRCALPHA)
        self.notification_bar_pos = self.notification_bar.get_rect()
        self.notification_bar_pos.centerx = self.screen.get_rect().centerx
        self.notification_bar_pos.centery = 0.03*self.size[1]
        self.notify = False
        self.notification_timer_A = pygame.time.get_ticks()
        self.notification_timer_B = pygame.time.get_ticks()
        self.notification_timeout = 3*1000

        self.text_renderer = pygame.font.SysFont("Arial", 20)

        self.current_update = self.update
        self.current_render = self.draw

        self.save_dir = "./"
        self.is_random_tangram = False

    def reset(self):
        self.tans_group = pygame.sprite.Group()
        # Create the tans
        self.tan_scaling_factor = 2
        self.tans = list(map(lambda tan_info: Tan(tan_info["points"], tan_info["size"], tan_info["color"]), self.tans_information))
        for tan in self.tans:
            tan.set_position(30 + self.tans.index(tan) * 130, 10)
            self.tans_group.add(tan)
        self.is_random_tangram = False

    def run_game(self):
        while self.running:
            self.events = pygame.event.get()
            for event in self.events:
                if event.type == pygame.QUIT:
                    self.running = False
            self.current_update()
            self.current_render()
            pygame.display.flip()
            self.game_clock.tick(self.FPS)

    def update(self):
        for event in self.events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.save_as_image()
                elif event.key == pygame.K_r:
                    self.current_tan.rotate(-1 * pi / 4)
                elif event.key == pygame.K_f:
                    self.current_tan.flip()
            elif event.type == pygame.MOUSEBUTTONDOWN and not self.locked:
                sprite_list = pygame.sprite.spritecollide(self.cursor, self.tans_group, False, pygame.sprite.collide_mask)
                if sprite_list:
                    sprite_list[0].scale(self.tan_scaling_factor)
                    self.current_tan = sprite_list[0]
                    self.locked = True
                    self.is_random_tangram = False
                else:
                    mouse_pos = pygame.mouse.get_pos()
                    x_coord = mouse_pos[0]
                    y_coord = mouse_pos[1]

                    if self.control_panel_position.left < x_coord < self.control_panel_position.right and self.control_panel_position.top < y_coord < self.control_panel_position.bottom:
                        action = self.determine_control_panel_action(mouse_pos)
                        if action:
                            action()

            elif self.locked and pygame.mouse.get_pressed()[0]:
                self.current_tan.rect.center = self.cursor.rect.center
                self.is_random_tangram = False

            elif self.locked and not pygame.mouse.get_pressed()[0]:
                self.locked = False
        self.cursor.update()

    def draw(self):
        self.screen.fill((0, 0, 0))
        background = pygame.rect.Rect(0, 0, self.size[0], 0.2*self.size[1])
        pygame.draw.rect(self.screen, (30, 30, 30), background)

        self.image_view.fill((255, 255, 255))

        self.screen.blit(self.control_panel, self.control_panel_position)
        for tan in self.tans:
            tan.draw(self.image_view, self.screen, self.tan_offset)
        
        # Draw the image view first
        self.screen.blit(self.image_view, self.image_view_position)
        
        # Then draw the tans on top of the image view
        for tan in self.tans:
            if self.is_random_tangram:
                tan.draw(self.image_view, self.screen, self.tan_offset)
            else:
                tan.draw(self.image_view, self.screen, self.tan_offset)
        
        if self.notify:
            self.notification_timer_B = pygame.time.get_ticks()
            if self.notification_timer_B - self.notification_timer_A > self.notification_timeout:
                self.notify = False
                for tan in self.tans:
                    tan.restore_color()
            self.screen.blit(self.notification_bar, self.notification_bar_pos)

        if self.pending_save:
            self.save_as_image()
            self.pending_save = False

        pygame.display.flip()

    def determine_control_panel_action(self, mouse_pos: tuple[int, int]):
        mouse_position = (mouse_pos[0] - self.control_panel_position.left, mouse_pos[1] - self.control_panel_position.top)

        for i, icon_position in enumerate(self.icon_positions):
            if icon_position[0] < mouse_position[0] < icon_position[0] + self.icon_width and icon_position[1] < mouse_position[1] + self.icon_width:
                return self.functions[i]

    def zoom_in(self):
        new_scale = self.tan_scaling_factor * 1.1
        for tan in self.tans:
            tan.zoom(1/self.tan_scaling_factor)
            tan.zoom(new_scale)
        self.tan_scaling_factor = new_scale

    def zoom_out(self):
        new_scale = self.tan_scaling_factor * 0.9
        for tan in self.tans:
            tan.zoom(1 / self.tan_scaling_factor)
            tan.zoom(new_scale)
        self.tan_scaling_factor = new_scale

    def save_as_image(self):
        if self.is_random_tangram:
            save_dir = self.random_tangram_save_dir
        else:
            save_dir = "./human_tangrams/"

        os.makedirs(save_dir, exist_ok=True)

        
            
    def create_save_path(self, directory):
        images = os.listdir(directory)
        images = [f for f in images if f.startswith('image') and f.endswith('.png')]
        if images:
            indices = [int(f.replace('image', '').replace('.png', '')) for f in images]
            last_index = max(indices)
            self.save_dir = os.path.join(directory, f'image{last_index+1}.png')
        else:
            self.save_dir = os.path.join(directory, 'image0.png')

    def validate_human_tangram(self):
        if not self.has_used_all_pieces():
               return False
        
        touching, message = self.pieces_touching()
        if not touching:
            self.create_notification(message, False)
            return False
        
        if self.check_overlap():
            self.create_notification("Pieces are overlapping too much!", False)
            return False
        
        return True

    def has_used_all_pieces(self) -> bool:
        return len(self.tans) == 7 and all(tan.been_scaled for tan in self.tans)

    def pieces_touching(self):
        graph = {i: set() for i in range(7)}
        for i in range(7):
            for j in range(i + 1, 7):
                if self.tans[i].mask.overlap(self.tans[j].mask, 
                    (self.tans[j].rect.x - self.tans[i].rect.x, 
                     self.tans[j].rect.y - self.tans[i].rect.y)):
                    graph[i].add(j)
                    graph[j].add(i)
        
        visited = set()
        def dfs(node):
            visited.add(node)
            for neighbor in graph[node]:
                if neighbor not in visited:
                    dfs(neighbor)
        
        dfs(0)
        if len(visited) == 7:
            return True, None
        else:
            return False, "All pieces must touch each other!"

    def check_overlap(self):
        for i in range(7):
            for j in range(i + 1, 7):
                overlap_area = self.tans[i].mask.overlap_area(self.tans[j].mask, 
                    (self.tans[j].rect.x - self.tans[i].rect.x, 
                     self.tans[j].rect.y - self.tans[i].rect.y))
                if overlap_area > 100:  
                    return True
        return False
    
    def save_tangram_image(self):
        save_surface = pygame.Surface((400, 400), pygame.SRCALPHA)
        save_surface.fill((255, 255, 255))
        
        min_x = min(tan.rect.left for tan in self.tans)
        min_y = min(tan.rect.top for tan in self.tans)
        max_x = max(tan.rect.right for tan in self.tans)
        max_y = max(tan.rect.bottom for tan in self.tans)
        
        tangram_width = max_x - min_x
        tangram_height = max_y - min_y
        offset_x = (400 - tangram_width) // 2 - min_x
        offset_y = (400 - tangram_height) // 2 - min_y
        
        for tan in self.tans:
            tan_surface = pygame.Surface(tan.image.get_size(), pygame.SRCALPHA)
            tan_surface.blit(tan.image, (0, 0))
            save_surface.blit(tan_surface, (tan.rect.left + offset_x, tan.rect.top + offset_y))
        
        data = pygame.image.tostring(save_surface, 'RGBA')
        img = Image.frombytes('RGBA', (400, 400), data)
        img.save(self.save_dir, 'PNG')
        
        self.create_notification(f"Image saved to {self.save_dir}", True)
        self.notify = True

    def change_color(self):
        for tan in self.tans:
            if self.tan_colored:
                tan.make_black()
            else:
                tan.make_colored()
        self.tan_colored = not self.tan_colored

    def create_notification(self, message: str, is_good: bool):
        color = (50, 255, 50) if is_good else (255, 50, 50)
        self.notification_timer_A = pygame.time.get_ticks()
        self.notification_timer_B = pygame.time.get_ticks()
        word = self.text_renderer.render(message, True, (0, 0, 0))
        word_pos = word.get_rect()
        self.notification_bar = pygame.surface.Surface((1.3*word.get_width(), 1.1*word.get_height()), pygame.SRCALPHA)
        bg_rect = pygame.rect.Rect(0, 0, 1.3*word.get_width(), 1.1*word.get_height())
        pygame.draw.rect(self.notification_bar, color, bg_rect, border_radius=10)
        self.notification_bar_pos = self.notification_bar.get_rect()
        self.notification_bar_pos.centerx = self.screen.get_rect().centerx
        self.notification_bar_pos.centery = 0.03 * self.size[1]
        word_pos.center = self.notification_bar.get_rect().center
        self.notification_bar.blit(word, word_pos)

    def generate_random_tangram(self):
        tangram_shapes = [
        [(0, 0), (100, 0), (50, 50)],            
        [(0, 0), (50, 0), (25, 25)],             
        [(0, 0), (50, 0), (25, -25)],            
        [(0, 0), (50, 0), (25, 25), (0, 50)],    
        [(0, 0), (50, 0), (75, 25), (25, 25)],   
        [(0, 0), (50, 50), (100, 0)],            
        [(0, 0), (50, 0), (25, 25)],             
    ]

        colors = [(255, 0, 0), (0, 0, 255), (0, 255, 0), (255, 255, 0), (128, 0, 128), (255, 165, 0), (255, 192, 203)]

        def rotate_point(point, angle):
            x, y = point
            rad = math.radians(angle)
            return (x * math.cos(rad) - y * math.sin(rad),
                x * math.sin(rad) + y * math.cos(rad))

        def translate_shape(shape, dx, dy):
            return [(x + dx, y + dy) for x, y in shape]

        def rotate_shape(shape, angle):
            return [rotate_point(point, angle) for point in shape]

        def shapes_overlap(shape1, shape2):
            def ccw(A, B, C):
                return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])

            def intersect(A, B, C, D):
                return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)

            for i in range(len(shape1)):
                for j in range(len(shape2)):
                    if intersect(shape1[i], shape1[(i+1) % len(shape1)],
                            shape2[j], shape2[(j+1) % len(shape2)]):
                        return True
            return False

        def is_inside_canvas(shape, width, height):
            for x, y in shape:
                if x < 0 or x > width or y < 0 or y > height:
                    return False
            return True

        def shapes_touch(shape1, shape2):
            for point1 in shape1:
                for point2 in shape2:
                    if math.isclose(point1[0], point2[0], abs_tol=1e-9) and math.isclose(point1[1], point2[1], abs_tol=1e-9):
                        return True
            return False

        def generate_tangram(screen, canvas_width, canvas_height):
            screen.fill((255, 255, 255))  
            placed_shapes = []
            unused_shapes = tangram_shapes.copy()
            unused_colors = colors.copy()
        
            first_shape = random.choice(unused_shapes)
            unused_shapes.remove(first_shape)
            angle = random.choice([0, 90, 180, 270])
            rotated_shape = rotate_shape(first_shape, angle)
            x = canvas_width // 2
            y = canvas_height // 2
            translated_shape = translate_shape(rotated_shape, x, y)
            placed_shapes.append(translated_shape)
            color = random.choice(unused_colors)
            unused_colors.remove(color)
            pygame.draw.polygon(screen, color, translated_shape, 0)
            pygame.draw.polygon(screen, (0, 0, 0), translated_shape, 1)

            while unused_shapes:
                shape = random.choice(unused_shapes)
            
                max_attempts = 10000
                for _ in range(max_attempts):
                    angle = random.choice([0, 90, 180, 270])
                    rotated_shape = rotate_shape(shape, angle)
                
                    connected_shape = random.choice(placed_shapes)
                    connection_point = random.choice(connected_shape)
                
                    dx = connection_point[0] - rotated_shape[0][0]
                    dy = connection_point[1] - rotated_shape[0][1]
                    translated_shape = translate_shape(rotated_shape, dx, dy)
                
                    if is_inside_canvas(translated_shape, canvas_width, canvas_height) and \
                    all(not shapes_overlap(translated_shape, placed) for placed in placed_shapes) and \
                    any(shapes_touch(translated_shape, placed) for placed in placed_shapes):
                        placed_shapes.append(translated_shape)
                        unused_shapes.remove(shape)
                        color = random.choice(unused_colors)
                        unused_colors.remove(color)
                        pygame.draw.polygon(screen, color, translated_shape, 0)
                        pygame.draw.polygon(screen, (0, 0, 0), translated_shape, 1)
                        break
                else:
                    return generate_tangram(screen, canvas_width, canvas_height)

            if not unused_shapes and not unused_colors:
                return placed_shapes, colors  
            else:
                return generate_tangram(screen, canvas_width, canvas_height)

        canvas_width = self.image_view.get_width()
        canvas_height = self.image_view.get_height()
        self.image_view = pygame.surface.Surface((canvas_width, canvas_height), pygame.SRCALPHA)
        placed_shapes, used_colors = generate_tangram(self.image_view, canvas_width, canvas_height)
        self.is_random_tangram = True
        self.pending_save = True  
        self.create_notification("Random Tangram generated!", True)
        self.notify = True
