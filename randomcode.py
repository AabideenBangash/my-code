import pygame
import random
import math

# Define the coordinates for each piece of the tangram
tangram_shapes = [
    [(0, 0), (100, 0), (50, 50)],            # Large triangle 1
    [(0, 0), (50, 0), (25, 25)],             # Small triangle 1
    [(0, 0), (50, 0), (25, -25)],            # Small triangle 2
    [(0, 0), (50, 0), (25, 25), (0, 50)],    # Square
    [(0, 0), (50, 0), (75, 25), (25, 25)],   # Parallelogram
    [(0, 0), (50, 50), (100, 0)],            # Large triangle 2
    [(0, 0), (50, 0), (25, 25)],             # Medium triangle
]

# Colors for the shapes
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
    screen.fill((255, 255, 255))  # Clear the canvas before generating a new tangram
    placed_shapes = []
    unused_shapes = tangram_shapes.copy()
    unused_colors = colors.copy()
    
    # Place the first shape in the center
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
            
            # Try to connect to a random placed shape
            connected_shape = random.choice(placed_shapes)
            connection_point = random.choice(connected_shape)
            
            # Translate the new shape to connect at the chosen point
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
            # If we couldn't place a shape after max attempts, start over
            return generate_tangram(screen, canvas_width, canvas_height)

    # Check if all shapes and colors have been used
    if not unused_shapes and not unused_colors:
        return  # Tangram generation successful
    else:
        # If not all shapes or colors were used, start over
        return generate_tangram(screen, canvas_width, canvas_height)

if __name__ == "__main__":
    def main():
        pygame.init()
        canvas_width = 600
        canvas_height = 600
        screen = pygame.display.set_mode((canvas_width, canvas_height))
        pygame.display.set_caption("Tangram Generator")

        running = True
        generate_tangram(screen, canvas_width, canvas_height)
        pygame.display.flip()
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        generate_tangram(screen, canvas_width, canvas_height)
                        pygame.display.flip()

        pygame.quit()

    main()
