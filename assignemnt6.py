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
BB_D_WIDTH = 150
BB_D_HEIGHT = 160

# Speeds of sprites
DRAGON_SPEED = 5
BOSS_SPEED = 6
DEMON_SPEED = -7
FIREBALL_SPEED = 7
BB_D_SPEED = -7

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
fireball_mask = pygame.mask.from_surface(fireball_image)

# Create groups
dragon_group = pygame.sprite.GroupSingle()
boss_group = pygame.sprite.GroupSingle()
demon_group = pygame.sprite.Group()
fireball_group = pygame.sprite.Group()
bb_d_group = pygame.sprite.Group()

class Dragon(pygame.sprite.Sprite):
    def __init__(self, image, x_pos, y_pos):
        super().__init__()
        self.image = image
        self.mask = pygame.mask.from_surface(image)
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


class Boss(pygame.sprite.Sprite):
    def __init__(self, image, x_pos, y_pos):
        super().__init__()
        self.image = image
        self.mask = pygame.mask.from_surface(image)
        self.rect = pygame.Rect(x_pos, y_pos, BOSS_WIDTH, BOSS_HEIGHT)
        self.x_pos = x_pos
        self.y_pos = y_pos
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
            if current_time - self.last_time_spawn > 150:
                self.last_time_spawn = current_time
                create_projectile((self.x_pos, self.y_pos), demon_dict)
                create_projectile((self.x_pos, self.y_pos), baby_dict)

class Projectile(pygame.sprite.Sprite):
    def __init__(self, image, width, height, x_pos, y_pos, speed):
        super().__init__()
        self.image = image
        self.mask = pygame.mask.from_surface(image)
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


def check_collisions():
    """
    Checks for collisions between the fireball and demon
    :return: None
    """
    global score, lives

    # Check for collisions between fireball and demon groups
    fireball_demon_collisions = pygame.sprite.groupcollide(fireball_group, demon_group, True, True,
                                                           pygame.sprite.collide_mask)
    if fireball_demon_collisions:
        score += 10 * len(fireball_demon_collisions)

    # Check for collisions between dragon and bb_dragon groups
    dragon_bb_dragon_collisions = pygame.sprite.groupcollide(dragon_group, bb_d_group, True, True,
                                                            pygame.sprite.collide_mask)
    if dragon_bb_dragon_collisions:
        score += 5

    fireball_bb_dragon_collisions = pygame.sprite.groupcollide(fireball_group, bb_d_group, True, True,
                                                             pygame.sprite.collide_mask)
    if fireball_bb_dragon_collisions:
        score -= 20

    # Check for collisions between dragon and demon groups
    dragon_demon_collisions = pygame.sprite.groupcollide(dragon_group, demon_group, False, True,
                                                         pygame.sprite.collide_mask)
    if dragon_demon_collisions:
        lives -= 1

score = 0
lives = 3
font = pygame.font.Font(None, 30)


def draw_score():
    # Render the score and lives text
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    lives_text = font.render(f"Lives: {lives}", True, (255, 255, 255))

    # Blit the text onto the screen
    window.blit(score_text, (270, 10))
    window.blit(lives_text, (270, 50))


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

demon_dict = {
    "group": demon_group,
    "image": init_animation_frames("demon.png", DEMON_WIDTH, DEMON_HEIGHT, 1)[0],
    "image": init_animation_frames("baby.png", BB_D_WIDTH, BB_D_HEIGHT, 1)[0],
    "emitter_width": BOSS_WIDTH,
    "emitter_height": BOSS_HEIGHT,
    "width": DEMON_WIDTH,
    "height": DEMON_HEIGHT,
    "speed": DEMON_SPEED
}

baby_dict = {
    "group": bb_d_group,
    "image": init_animation_frames("baby.png", BB_D_WIDTH, BB_D_HEIGHT, 1)[0],
    "emitter_width": BOSS_WIDTH,
    "emitter_height": BOSS_HEIGHT,
    "width": BB_D_WIDTH,
    "height": BB_D_HEIGHT,
    "speed": BB_D_SPEED
}
def main():
    global score, lives
    # Initialize animation frames and variables for dragon, boss, and demon
    animation_frames_dragon = init_animation_frames(
        'dragon.png', DRAGON_WIDTH, DRAGON_HEIGHT, 5)
    current_frame_dragon = 0
    last_time_dragon = pygame.time.get_ticks()

    animation_frames_boss = init_animation_frames(
        'boss.png', BOSS_WIDTH, BOSS_HEIGHT, 4)
    current_frame_boss = 0
    last_time_boss = pygame.time.get_ticks()

    animation_frames_demon = init_animation_frames(
        'demon.png', DEMON_WIDTH, DEMON_HEIGHT, 4)
    current_frame_demon = 0
    last_time_demon = pygame.time.get_ticks()

    # Create boss and dragon sprites
    dragon = Dragon(animation_frames_dragon[0], 0, 0)
    dragon_group.add(dragon)

    boss = Boss(animation_frames_boss[0], WINDOW_WIDTH - BOSS_WIDTH, 0)
    boss_group.add(boss)

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
        boss.update()
        demon_group.update()
        fireball_group.update()
        bb_d_group.update()

        # Draw all sprites
        dragon_group.draw(window)
        boss_group.draw(window)
        demon_group.draw(window)
        fireball_group.draw(window)
        bb_d_group.draw(window)

        check_collisions()
        draw_score()  # Display the score and lives on the screen

        # Check for game over
        if lives <= 0:
            running = False

        # Animate the dragon, boss, and demons
        last_time_dragon, current_frame_dragon = animate_sprite(animation_frames_dragon,
                                                                last_time_dragon,
                                                                current_frame_dragon,
                                                                dragon)

        last_time_boss, current_frame_boss = animate_sprite(animation_frames_boss,
                                                            last_time_boss,
                                                            current_frame_boss,
                                                            boss)

        for demon_sprite in demon_group.sprites():
            last_time_demon, current_frame_demon = animate_sprite(animation_frames_demon,
                                                                  last_time_demon,
                                                                  current_frame_demon,
                                                                  demon_sprite)

        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()