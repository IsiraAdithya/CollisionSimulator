import pygame
import pymunk
import pymunk.pygame_util

# Initialize Pygame
pygame.init()

# Set up display
width, height = 800, 600
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Box Collision Simulator")

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# Physics setup
space = pymunk.Space()
space.gravity = (0, 900)  # Adding gravity to the simulation

# Create walls
def create_wall(space, start, end):
    wall_body = pymunk.Body(body_type=pymunk.Body.STATIC)
    wall_shape = pymunk.Segment(wall_body, start, end, 1.0)
    wall_shape.elasticity = 1.0
    space.add(wall_body, wall_shape)

# Left, right, top walls
create_wall(space, (50, 50), (50, height - 50))
create_wall(space, (width - 50, 50), (width - 50, height - 50))
create_wall(space, (50, 50), (width - 50, 50))

# Create floor at the bottom of the screen
create_wall(space, (50, height - 10), (width - 50, height - 10))

# Create box
def create_box(space, mass, size, position, velocity):
    body = pymunk.Body(mass, pymunk.moment_for_box(mass, (size, size)))
    body.position = position
    body.velocity = velocity
    shape = pymunk.Poly.create_box(body, (size, size))
    shape.elasticity = 0.5  # Adding some damping for more realistic collisions
    shape.collision_type = 1
    space.add(body, shape)
    return shape

# Create GUI for user input
font = pygame.font.Font(None, 36)
input_boxes = {
    'mass1': {'rect': pygame.Rect(120, 10, 140, 32), 'text': '', 'value': None, 'label': 'Mass 1:'},
    'velocity1': {'rect': pygame.Rect(400, 10, 140, 32), 'text': '', 'value': None, 'label': 'Velocity 1:'},
    'mass2': {'rect': pygame.Rect(120, 60, 140, 32), 'text': '', 'value': None, 'label': 'Mass 2:'},
    'velocity2': {'rect': pygame.Rect(400, 60, 140, 32), 'text': '', 'value': None, 'label': 'Velocity 2:'}
}
selected_box = None
boxes_created = False

# Start button
start_button = pygame.Rect(600, 20, 100, 40)
simulation_started = False

# Collision counter
collision_count = 0

# Collision handler
def collision_handler(arbiter, space, data):
    global collision_count
    collision_count += 1
    return True

space.add_collision_handler(1, 1).post_solve = collision_handler

# Draw options
draw_options = pymunk.pygame_util.DrawOptions(window)

# Main loop
running = True
clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if start_button.collidepoint(event.pos) and not boxes_created:
                # Collect user input values and create boxes
                try:
                    mass1 = float(input_boxes['mass1']['text'])
                    velocity1 = float(input_boxes['velocity1']['text'])
                    mass2 = float(input_boxes['mass2']['text'])
                    velocity2 = float(input_boxes['velocity2']['text'])
                    box1 = create_box(space, mass1, 50, (300, height - 60), (velocity1, 0))
                    box2 = create_box(space, mass2, 50, (500, height - 60), (-velocity2, 0))
                    boxes_created = True
                    simulation_started = True
                except ValueError:
                    # Handle invalid input values
                    pass
            for key, box in input_boxes.items():
                if box['rect'].collidepoint(event.pos):
                    selected_box = key
        elif event.type == pygame.KEYDOWN:
            if selected_box is not None:
                if event.key == pygame.K_RETURN:
                    try:
                        input_boxes[selected_box]['value'] = float(input_boxes[selected_box]['text'])
                        selected_box = None
                    except ValueError:
                        input_boxes[selected_box]['text'] = ''  # Clear invalid input
                elif event.key == pygame.K_BACKSPACE:
                    input_boxes[selected_box]['text'] = input_boxes[selected_box]['text'][:-1]
                else:
                    input_boxes[selected_box]['text'] += event.unicode

    # Clear the screen
    window.fill(WHITE)

    # Draw input boxes with labels
    for key, box in input_boxes.items():
        label_surface = font.render(box['label'], True, BLACK)
        label_rect = label_surface.get_rect(midright=(box['rect'].x - 10, box['rect'].y + box['rect'].height // 2))
        window.blit(label_surface, label_rect)
        txt_surface = font.render(box['text'], True, BLACK)
        window.blit(txt_surface, (box['rect'].x + 5, box['rect'].y + 5))
        pygame.draw.rect(window, BLACK, box['rect'], 2)

    # Draw start button
    pygame.draw.rect(window, GREEN, start_button)
    start_text = font.render("Start", True, BLACK)
    window.blit(start_text, (start_button.x + 20, start_button.y + 5))

    # Display collision count
    collision_text = font.render(f"Collisions: {collision_count}", True, BLACK)
    window.blit(collision_text, (10, height - 40))

    # Step the physics simulation if started
    if simulation_started:
        space.step(1 / 60.0)
        # Draw objects
        space.debug_draw(draw_options)

    # Update the display
    pygame.display.flip()

    # Limit frame rate
    clock.tick(60)

pygame.quit()