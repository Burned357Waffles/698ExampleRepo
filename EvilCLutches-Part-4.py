import pygame

pygame.init()

# Window dimensions
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480

# Dimensions of the dragon sprite
DRAGON_WIDTH = 135
DRAGON_HEIGHT = 150
FIREBALL_WIDTH = 50
FIREBALL_HEIGHT = 48

# Speeds of sprites
DRAGON_SPEED = 5
FIREBALL_SPEED = 7

ANIMATION_SPEED = 200

# Colors
BLACK = (0, 0, 0)

# Create the window
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("EvilClutches")

# Load static images and masks
background_image = pygame.image.load('Background.bmp').convert_alpha()
fireball_image = pygame.image.load('fireball.png').convert_alpha()
fireball_image = pygame.transform.scale(fireball_image, (64, 64))

# Create groups
fireball_group = pygame.sprite.Group()
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


class Projectile(pygame.sprite.Sprite):
    def __init__(self, image, width, height, x_pos, y_pos, speed):
        super().__init__()
        self.image = image
        self.rect = pygame.Rect(x_pos, y_pos, width, height)
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.speed = speed

    def update(self):
        """
        Updates the position of the projectile and removes it if it goes off-screen.
        :return: None
        """
        self.x_pos += self.speed
        self.rect.move_ip(self.speed, 0)

        if not (WINDOW_WIDTH >= self.x_pos >= 0 - self.rect.width):
            self.kill()


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


def create_projectile(position, obj):
    """
    Creates a new projectile (demon, baby, or fireball) at the given position.
    :param position: Position to spawn the object
    :param obj: Dictionary of the object's type
    :return: None
    """
    obj_x = position[0] + obj.get("emitter_width") // 2 - obj.get("width") // 2
    obj_y = position[1] + obj.get("emitter_height") // 2 - obj.get("height") // 2

    new_projectile = Projectile(obj.get("image"),
                                obj.get("width"),
                                obj.get("height"),
                                obj_x,
                                obj_y,
                                obj.get("speed"))

    obj.get("group").add(new_projectile)


# Dictionaries to hold the different values of the projectile types
fireball_dict = {
    "group": fireball_group,
    "image": fireball_image,
    "emitter_width": DRAGON_WIDTH + 100,
    "emitter_height": 50,
    "width": FIREBALL_WIDTH,
    "height": FIREBALL_HEIGHT,
    "speed": FIREBALL_SPEED
}

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
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    create_projectile((dragon.x_pos, dragon.y_pos), fireball_dict)

        # Display background image
        window.blit(background_image, (0, 0))

        # Update all sprites
        dragon.update()
        fireball_group.update()

        # Draw all sprites
        dragon_group.draw(window)
        fireball_group.draw(window)

        # Animate the Dragon
        last_time_dragon, current_frame_dragon = animate_sprite(animation_frames_dragon,
                                                                last_time_dragon,
                                                                current_frame_dragon,
                                                                dragon)

        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()
