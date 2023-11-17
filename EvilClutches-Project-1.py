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
DEMON_SCALE = 0.5
FIREBALL_WIDTH = 50
FIREBALL_HEIGHT = 48
BABY_WIDTH = 53
BABY_HEIGHT = 55

# Speeds of sprites
DRAGON_SPEED = 5
BOSS_SPEED = 6
DEMON_SPEED = -9
FIREBALL_SPEED = 7
BABY_SPEED = -5

# Intervals
ANIMATION_INTERVAL = 200
BOSS_SPAWN_INTERVAL = 150

# Scoring rules
DEMON_KILLED_SCORE = 100
BABY_KILLED_SCORE = -300
BABY_SAVED_SCORE = 500

score = 0
lives = 3
start_time = 0
end_time = 0
game_over = False

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GAME_OVER_TEXT_COLOR = (200, 0, 0)

#Adding Music
pygame.mixer.init()
pygame.mixer.music.load("Music.mp3")
pygame.mixer.music.play(loops=-1)

# Create the window
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("EvilClutches")

# Load the font
font = pygame.font.Font(None, 36)

# Load static images and masks
background_image = pygame.image.load('Background.bmp').convert_alpha()
fireball_image = pygame.image.load('fireball.png').convert_alpha()
fireball_image = pygame.transform.scale(fireball_image, (64, 64))
baby_image = pygame.image.load('baby.png').convert_alpha()

# Create groups
dragon_group = pygame.sprite.GroupSingle()
boss_group = pygame.sprite.GroupSingle()
demon_group = pygame.sprite.Group()
fireball_group = pygame.sprite.Group()
baby_group = pygame.sprite.Group()

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
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                fireball_group.add(Fireball(self.x_pos, self.y_pos))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.y_pos -= DRAGON_SPEED
        if keys[pygame.K_s]:
            self.y_pos += DRAGON_SPEED

        # TODO: Restrict the dragon's position within the window boundaries
        self.y_pos = max(0, min(self.y_pos, WINDOW_HEIGHT - DRAGON_HEIGHT))

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
        if num <= 2:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_time_spawn > BOSS_SPAWN_INTERVAL:
                self.last_time_spawn = current_time
                if num < 2:
                    demon_group.add(Demon(self.x_pos, self.y_pos))
                    return
                baby_group.add(Baby(self.x_pos, self.y_pos))


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
        self.rect = pygame.Rect(self.x_pos, self.y_pos, DEMON_WIDTH * DEMON_SCALE, DEMON_HEIGHT * DEMON_SCALE)
        self.frame_list = init_animation_frames("demon.png", DEMON_WIDTH, DEMON_HEIGHT, 4)
        self.current_frame_index = 0
        self.last_time_frame_updated = pygame.time.get_ticks()
        super().__init__(self.frame_list[0], self.rect, DEMON_SPEED)

    def update(self):
        self.image = pygame.transform.scale(self.image, (DEMON_WIDTH * DEMON_SCALE, DEMON_HEIGHT * DEMON_SCALE))
        self.mask = self.mask = pygame.mask.from_surface(self.image)
        self.image.set_colorkey(BLACK)
        super().update()


class Baby(Projectile):
    def __init__(self, x_pos, y_pos):
        self.x_pos = x_pos + BOSS_WIDTH // 2 - DEMON_WIDTH // 2
        self.y_pos = y_pos + BOSS_HEIGHT // 2 - DEMON_HEIGHT // 2
        self.rect = pygame.Rect(self.x_pos, self.y_pos, BABY_WIDTH, BABY_HEIGHT)
        super().__init__(baby_image, self.rect, BABY_SPEED)


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
    global score, lives, game_over
    if pygame.sprite.groupcollide(fireball_group, demon_group, True, True, pygame.sprite.collide_mask):
        score += DEMON_KILLED_SCORE
    if pygame.sprite.groupcollide(fireball_group, baby_group, True, True, pygame.sprite.collide_mask):
        score += BABY_KILLED_SCORE
    if pygame.sprite.groupcollide(dragon_group, baby_group, False, True, pygame.sprite.collide_mask):
        score += BABY_SAVED_SCORE
    if pygame.sprite.groupcollide(dragon_group, demon_group, True, True, pygame.sprite.collide_mask):
        lives -= 1
        dragon_group.add(Dragon())
        if lives == 0:
            game_over = True
            end_time = pygame.time.get_ticks()
            score += (end_time - start_time) // 100


def display_score():
    """
    Displays the current score on the screen.
    :return: None
    """
    current_time = pygame.time.get_ticks()
    score_text = font.render(f"Score: {score} + {(current_time - start_time) / 100}", True, WHITE)
    window.blit(score_text, (10, 10))


def display_lives():
    """
    Displays the current lives remaining on the screen.
    :return: None
    """
    lives_text = font.render(f"Lives: {lives}", True, WHITE)
    window.blit(lives_text, (10, 46))


def display_game_over_screen():
    """
    Shows the game over screen
    :return: None
    """
    window.fill(BLACK)
    game_over_text = font.render("YOU DIED", True, GAME_OVER_TEXT_COLOR)
    game_over_text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
    score_text = font.render(f"Your Score: {score}", True, WHITE)
    score_text_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 36))
    restart_text = font.render("Click To Restart", True, WHITE)
    restart_text_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 36*2))

    window.blit(game_over_text, game_over_text_rect)
    window.blit(score_text, score_text_rect)
    window.blit(restart_text, restart_text_rect)


def reset_game():
    """
    Resets the game to the default state for new game
    :return: None
    """
    global game_over, score, lives, start_time, end_time
    game_over = False
    score = 0
    lives = 3
    start_time = pygame.time.get_ticks()
    end_time = 0
    dragon_group.sprite.kill()
    boss_group.sprite.kill()
    for fireball in fireball_group.sprites():
        fireball.kill()
    for demon in demon_group.sprites():
        demon.kill()
    for baby in baby_group.sprites():
        baby.kill()
    dragon_group.add(Dragon())
    boss_group.add(Boss())
    pygame.event.clear()

def main():
    global start_time
    # Initialize animation frames and variables for dragon, boss, and demon
    # Create boss and dragon sprites
    dragon_group.add(Dragon())
    boss_group.add(Boss())

    running = True
    clock = pygame.time.Clock()
    start_time = pygame.time.get_ticks()
    # Main game loop
    while running:
        # Set frame rate
        clock.tick(60)

        # Handle events in game
        for event in pygame.event.get(exclude=pygame.KEYDOWN):
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and game_over:
                reset_game()

        if not game_over:
            # Display background image
            window.blit(background_image, (0, 0))

            # Update all sprites
            dragon_group.update()
            boss_group.update()
            demon_group.update()
            fireball_group.update()
            baby_group.update()

            # Draw all sprites
            dragon_group.draw(window)
            boss_group.draw(window)
            demon_group.draw(window)
            fireball_group.draw(window)
            baby_group.draw(window)

            check_collisions()

            # Animate the dragon, boss, and demons
            animate_sprite(dragon_group.sprite)
            animate_sprite(boss_group.sprite)
            for demon_sprite in demon_group.sprites():
                animate_sprite(demon_sprite)

            display_score()
            display_lives()

        else:
            display_game_over_screen()

        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()
