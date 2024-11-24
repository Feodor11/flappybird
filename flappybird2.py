#This a second version of flappy bird but with coins
import pygame
import random
import sys
import os

# Initialize Pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
GRAVITY = 0.25
FLAP_STRENGTH = -7
PIPE_SPEED = 3
PIPE_GAP = 150
PIPE_FREQUENCY = 1500  # milliseconds
COIN_SIZE = 30  # Increased coin size
COIN_FREQUENCY = 3000  # milliseconds

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
SKY_BLUE = (135, 206, 235)
GOLD = (255, 215, 0)

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Flappy Bird with Coins')
clock = pygame.time.Clock()

# Load images
current_dir = os.path.dirname(os.path.abspath(__file__))
bird_img = pygame.image.load(os.path.join(current_dir, 'assets', 'bird.png'))
bird_img = pygame.transform.scale(bird_img, (40, 30))
pipe_img = pygame.image.load(os.path.join(current_dir, 'assets', 'pipe.png'))
coin_img = pygame.image.load(os.path.join(current_dir, 'assets', 'coin.png'))
coin_img = pygame.transform.scale(coin_img, (COIN_SIZE, COIN_SIZE))  # Resize to fit the game
bg_img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
bg_img.fill(SKY_BLUE)
bg_img = pygame.transform.scale(bg_img, (SCREEN_WIDTH, SCREEN_HEIGHT))


class Bird:
    def __init__(self):
        self.x = 50
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        self.rect = pygame.Rect(self.x, self.y, 40, 30)  # Match image dimensions
        self.angle = 0

    def flap(self):
        self.velocity = FLAP_STRENGTH
        self.angle = 30

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        self.rect.y = self.y
        # Rotate bird based on velocity
        self.angle = max(-30, min(self.angle - 3, 30))

    def draw(self):
        rotated_bird = pygame.transform.rotate(bird_img, self.angle)
        screen.blit(rotated_bird, (self.x, self.y))


class Pipe:
    def __init__(self):
        self.gap_y = random.randint(150, SCREEN_HEIGHT - 150)
        self.x = SCREEN_WIDTH
        self.width = 50
        self.top_height = self.gap_y - PIPE_GAP // 2
        self.bottom_height = SCREEN_HEIGHT - (self.gap_y + PIPE_GAP // 2)
        self.top_rect = pygame.Rect(self.x, 0, self.width, self.top_height)
        self.bottom_rect = pygame.Rect(self.x, self.gap_y + PIPE_GAP // 2, self.width, self.bottom_height)
        self.passed = False

    def update(self):
        self.x -= PIPE_SPEED
        self.top_rect.x = self.x
        self.bottom_rect.x = self.x

    def draw(self):
        top_pipe = pygame.transform.scale(pipe_img, (self.width, self.top_height))
        top_pipe = pygame.transform.flip(top_pipe, False, True)
        screen.blit(top_pipe, (self.x, 0))

        bottom_pipe = pygame.transform.scale(pipe_img, (self.width, self.bottom_height))
        screen.blit(bottom_pipe, (self.x, SCREEN_HEIGHT - self.bottom_height))


class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(self.x, self.y, COIN_SIZE + 10, COIN_SIZE + 10)  # Larger collision box

    def update(self):
        self.x -= PIPE_SPEED
        self.rect.x = self.x

    def draw(self):
        screen.blit(coin_img, (self.x, self.y))


def game_loop():
    bird = Bird()
    pipes = []
    coins = []
    score = 0
    coins_collected = 0
    last_pipe = pygame.time.get_ticks()
    last_coin = pygame.time.get_ticks()
    running = True

    while running:
        current_time = pygame.time.get_ticks()

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird.flap()

        # Spawn new pipes
        if current_time - last_pipe > PIPE_FREQUENCY:
            new_pipe = Pipe()
            pipes.append(new_pipe)
            last_pipe = current_time

            # Add coins near the gap of the pipe (increased spawn rate and better positions)
            if random.random() < 0.8:  # 80% chance to spawn a coin
                coin_x = SCREEN_WIDTH + new_pipe.width
                coin_y = new_pipe.gap_y - PIPE_GAP // 4  # Coin more centered in gap
                coins.append(Coin(coin_x, coin_y))

        # Update game objects
        bird.update()
        for pipe in pipes:
            pipe.update()
            # Score points when passing pipes
            if not pipe.passed and pipe.x + pipe.width < bird.x:
                score += 1
                pipe.passed = True

        for coin in coins:
            coin.update()

        # Check for collisions
        for pipe in pipes:
            if bird.rect.colliderect(pipe.top_rect) or bird.rect.colliderect(pipe.bottom_rect):
                return score, coins_collected

        # Collect coins
        for coin in coins[:]:
            if bird.rect.colliderect(coin.rect):
                coins_collected += 1
                coins.remove(coin)

        # Remove off-screen pipes and coins
        pipes = [pipe for pipe in pipes if pipe.x > -50]
        coins = [coin for coin in coins if coin.x > -50]

        # Check if bird is off screen
        if bird.y < 0 or bird.y > SCREEN_HEIGHT:
            return score, coins_collected

        # Draw everything
        screen.fill(SKY_BLUE)  # Clear screen with sky blue
        for pipe in pipes:
            pipe.draw()
        for coin in coins:
            coin.draw()
        bird.draw()

        # Draw score and coins collected
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {score}', True, WHITE)
        coins_text = font.render(f'Coins: {coins_collected}', True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(coins_text, (10, 40))

        pygame.display.update()
        clock.tick(60)


def main():
    while True:
        score, coins_collected = game_loop()
        # Show game over screen
        screen.fill(SKY_BLUE)
        font = pygame.font.Font(None, 64)
        game_over = font.render('Game Over', True, WHITE)
        score_text = font.render(f'Score: {score}', True, WHITE)
        coins_text = font.render(f'Coins: {coins_collected}', True, WHITE)
        continue_text = font.render('Press SPACE to Continue', True, WHITE)

        screen.blit(game_over, (SCREEN_WIDTH // 2 - game_over.get_width() // 2, 200))
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 300))
        screen.blit(coins_text, (SCREEN_WIDTH // 2 - coins_text.get_width() // 2, 350))
        screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, 400))

        pygame.display.update()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        waiting = False
                    if event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()


if __name__ == "__main__":
    main()