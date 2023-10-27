import pygame

pygame.init()

# Window dimensions
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480

# Create the window
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("EvilClutches")

# Load static images
background_image = pygame.image.load('Background.bmp').convert_alpha()


def main():
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

        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()
