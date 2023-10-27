import pygame
import random

pygame.init()

# Window dimensions
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480

# Dimensions of the dragon sprite
DRAGON_WIDTH = 135
DRAGON_HEIGHT = 150
BOSS_WIDTH = 135
BOSS_HEIGHT = 165
DEMON_WIDTH = 130
DEMON_HEIGHT = 140
FIREBALL_WIDTH = 50
FIREBALL_HEIGHT = 48

# Speeds of sprites
DRAGON_SPEED = 5
BOSS_SPEED = 6
DEMON_SPEED = -7
FIREBALL_SPEED = 7

ANIMATION_INTERVAL = 200
DEMON_SPAWN_INTERVAL = 150

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
dragon_group = pygame.sprite.GroupSingle()
boss_group = pygame.sprite.GroupSingle()
demon_group = pygame.sprite.Group()
fireball_group = pygame.sprite.Group()


class Dragon(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.frame_list = init_animation_frames('dragon.png', DRAGON_WIDTH, DRAGON_HEIGHT, 5)
        self.current_frame_index = 0
        self.last_time_frame_updated = pygame.time.get_ticks()
        self.image = self.frame_list[0]
        self.mask = pygame.mask.from_surface(self.image)
        self.x_pos = 0
        self.y_pos = 0
        self.rect = pygame.Rect(self.x_pos, self.y_pos, DRAGON_WIDTH, DRAGON_HEIGHT)

    def update(self):
        """
        Updates the dragon's position based on user input and ensures it stays within boundaries.
        :return: None
        """
        for event in pygame.event.get(eventtype=pygame.KEYDOWN):
            if event.key == pygame.K_SPACE:
                fireball_group.add(Fireball(self.x_pos, self.y_pos))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.y_pos -= DRAGON_SPEED
        if keys[pygame.K_s]:
            self.y_pos += DRAGON_SPEED

        # TODO: Restrict the dragon's position within the window boundaries

        # Set the rectangle position
        self.rect.y = self.y_pos


class Boss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.frame_list = init_animation_frames('boss.png', BOSS_WIDTH, BOSS_HEIGHT, 4)
        self.current_frame_index = 0
        self.last_time_frame_updated = pygame.time.get_ticks()
        self.image = self.frame_list[0]
        self.mask = pygame.mask.from_surface(self.image)
        self.x_pos = WINDOW_WIDTH - BOSS_WIDTH
        self.y_pos = 0
        self.rect = pygame.Rect(self.x_pos, self.y_pos, BOSS_WIDTH, BOSS_HEIGHT)
        self.direction = 1
        self.last_time_spawn = pygame.time.get_ticks()

    def update(self):
        """
        Updates the boss's position, direction, and spawns objects.
        :return: None
        """
        self.y_pos += self.direction * BOSS_SPEED
        self.rect.y = self.y_pos

        # Change direction if the boss hits the top or bottom boundary
        # direction = 1 is down, -1 is up
        if self.rect.top <= 0:
            self.direction = 1
        elif self.rect.bottom >= WINDOW_HEIGHT:
            self.direction = -1

        self.spawn_objects()

    def spawn_objects(self):
        """
        Spawns demons or babies based on a random number. Demons have a higher weighting
        :return: None
        """
        num = random.randrange(150)
        if num <= 1:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_time_spawn > DEMON_SPAWN_INTERVAL:
                self.last_time_spawn = current_time
                demon_group.add(Demon(self.x_pos, self.y_pos))


class Projectile(pygame.sprite.Sprite):
    def __init__(self, image, rect, speed):
        super().__init__()
        self.image = image
        self.rect = rect
        self.mask = pygame.mask.from_surface(image)
        self.speed = speed

    def update(self):
        """
        Updates the position of the projectile and removes it if it goes off-screen.
        :return: None
        """
        self.rect.x += self.speed

        if not (WINDOW_WIDTH >= self.rect.x >= 0 - self.rect.width):
            self.kill()


class Fireball(Projectile):
    def __init__(self, x_pos, y_pos):
        self.x_pos = x_pos + (DRAGON_WIDTH + DRAGON_WIDTH * 0.74) // 2 - FIREBALL_WIDTH // 2
        self.y_pos = y_pos + (DRAGON_HEIGHT - DRAGON_WIDTH * 0.67) // 2 - FIREBALL_HEIGHT // 2
        self.rect = pygame.Rect(self.x_pos, self.y_pos, FIREBALL_WIDTH, FIREBALL_HEIGHT)
        super().__init__(fireball_image, self.rect, FIREBALL_SPEED)


class Demon(Projectile):
    def __init__(self, x_pos, y_pos):
        self.x_pos = x_pos + BOSS_WIDTH // 2 - DEMON_WIDTH // 2
        self.y_pos = y_pos + BOSS_HEIGHT // 2 - DEMON_HEIGHT // 2
        self.rect = pygame.Rect(self.x_pos, self.y_pos, DEMON_WIDTH, DEMON_HEIGHT)
        self.frame_list = init_animation_frames("demon.png", DEMON_WIDTH, DEMON_HEIGHT, 4)
        self.current_frame_index = 0
        self.last_time_frame_updated = pygame.time.get_ticks()
        super().__init__(self.frame_list[0], self.rect, DEMON_SPEED)


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


def animate_sprite(obj):
    """
    Animates the sprite by updating its image based on the current frame.
    :param obj: The sprite being displayed
    :return: None
    """
    current_time = pygame.time.get_ticks()
    if current_time - obj.last_time_frame_updated >= ANIMATION_INTERVAL:
        obj.current_frame_index += 1
        obj.last_time_frame_updated = current_time
        if obj.current_frame_index >= len(obj.frame_list):
            obj.current_frame_index = 0

        obj.image = obj.frame_list[obj.current_frame_index]


def check_collisions():
    """
    Checks for collisions between the fireball and demon
    :return: None
    """
    if pygame.sprite.groupcollide(fireball_group, demon_group, True, True, pygame.sprite.collide_mask):
        print("COLLISION")


def main():
    # Initialize animation frames and variables for dragon, boss, and demon
    # Create boss and dragon sprites
    dragon = Dragon()
    dragon_group.add(dragon)

    boss = Boss()
    boss_group.add(boss)

    running = True
    clock = pygame.time.Clock()
    # Main game loop
    while running:
        # Set frame rate
        clock.tick(60)

        # Handle events in game
        for event in pygame.event.get(exclude=pygame.KEYDOWN):
            if event.type == pygame.QUIT:
                running = False

        # Display background image
        window.blit(background_image, (0, 0))

        # Update all sprites
        dragon.update()
        boss.update()
        demon_group.update()
        fireball_group.update()
         
        print("hello")

        # Animate the dragon, boss, and demons
        animate_sprite(dragon)
        animate_sprite(boss)
        for demon_sprite in demon_group.sprites():
            animate_sprite(demon_sprite)

        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()