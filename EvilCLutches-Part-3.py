import pygame

pygame.init()

# Window dimensions
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480

# Dimensions of the dragon sprite
DRAGON_WIDTH = 135
DRAGON_HEIGHT = 150

# Speeds of sprites
DRAGON_SPEED = 5

ANIMATION_SPEED = 200

# Colors
BLACK = (0, 0, 0)

# Create the window
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("EvilClutches")

# Load static images
background_image = pygame.image.load('Background.bmp').convert_alpha()

dragon_group = pygame.sprite.GroupSingle()


class Dragon(pygame.sprite.Sprite):
    def __init__(self, image, x_pos, y_pos):
        super().__init__()
        self.image = image
        self.rect = pygame.Rect(x_pos, y_pos, DRAGON_WIDTH, DRAGON_HEIGHT)
        self.x_pos = x_pos
        self.y_pos = y_pos

    def update(self):
        """
        Updates the dragon's position based on user input and ensures it stays within boundaries.
        :return: None
        """
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.y_pos -= DRAGON_SPEED
        if keys[pygame.K_s]:
            self.y_pos += DRAGON_SPEED

        # TODO: Restrict the dragon's position within the window boundaries

        # Set the rectangle position
        self.rect.y = self.y_pos


def init_animation_frames(file_name, frame_width, frame_height, frame_count):
    """
    Separates the frames of the animation and puts them into a list.
    :param file_name: The name of the image file
    :param frame_width: the width interval to cut the sprite sheet
    :param frame_height: The height to cut the sprite sheet
    :param frame_count: The number of frames in the sprite sheet
    :return: List of the frames from the sprite sheet
    """
    sprite_sheet_image = pygame.image.load(file_name).convert_alpha()

    animation_frames = []

    for frame in range(frame_count):
        frame_surface = pygame.Surface((frame_width, frame_height)).convert_alpha()
        frame_surface.blit(sprite_sheet_image, (0, 0), ((frame * frame_width), 0, frame_width, frame_height))
        frame_surface.set_colorkey(BLACK)

        animation_frames.append(frame_surface)

    return animation_frames


def animate_sprite(frame_list, last_time, current_frame, obj):
    """
    Animates the sprite by updating its image based on the current frame.
    :param frame_list: The list of frames from the sprite sheet
    :param last_time: The last time the image was updated
    :param current_frame: The index of the current frame being displayed
    :param obj: The sprite being displayed
    :return: last_time, current_frame
    """
    current_time = pygame.time.get_ticks()
    if current_time - last_time >= ANIMATION_SPEED:
        current_frame += 1
        last_time = current_time
        if current_frame >= len(frame_list):
            current_frame = 0

        obj.image = frame_list[current_frame]

    return last_time, current_frame


def main():
    # Initialize animation frames and variables for dragon
    animation_frames_dragon = init_animation_frames(
        'dragon.png', DRAGON_WIDTH, DRAGON_HEIGHT, 5)
    current_frame_dragon = 0
    last_time_dragon = pygame.time.get_ticks()

    dragon = Dragon(animation_frames_dragon[0], 0, 0)
    dragon_group.add(dragon)

    running = True
    clock = pygame.time.Clock()
    # Main game loop
    while running:
        # Set frame rate
        clock.tick(60)

        # Handle events in game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Display background image
        window.blit(background_image, (0, 0))

        # Update Dragon position
        dragon.update()

        # Draw Dragon
        dragon_group.draw(window)

        # Animate the Dragon
        last_time_dragon, current_frame_dragon = animate_sprite(animation_frames_dragon,
                                                                last_time_dragon,
                                                                current_frame_dragon,
                                                                dragon)

        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()
