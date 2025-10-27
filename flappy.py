# flappy.py
import pygame
import sys
import random
import os

# ------------ Config -------------
WIDTH, HEIGHT = 432, 768
FPS = 60

GRAVITY = 0.45
JUMP_STRENGTH = -9.5
PIPE_SPEED = 3
PIPE_GAP = 180
PIPE_DISTANCE = 300  # distance between consecutive pipes (x distance)
BIRD_SIZE = 34

FONT_NAME = "freesansbold.ttf"
HIGHSCORE_FILE = "highscore.txt"

# Colors
WHITE = (255, 255, 255)
BG_COLOR = (135, 206, 235)  # sky blue
BIRD_COLOR = (255, 223, 0)  # yellow
PIPE_COLOR = (34, 139, 34)  # green
GROUND_COLOR = (222, 184, 135)

# ------------ Helpers -------------
def load_highscore():
    try:
        with open(HIGHSCORE_FILE, "r") as f:
            return int(f.read().strip() or 0)
    except Exception:
        return 0

def save_highscore(value):
    try:
        with open(HIGHSCORE_FILE, "w") as f:
            f.write(str(value))
    except Exception:
        pass

# ------------ Game Objects -------------
class Bird:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel = 0.0
        self.width = BIRD_SIZE
        self.height = BIRD_SIZE
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.alive = True
        self.rot = 0

    def update(self):
        self.vel += GRAVITY
        self.y += self.vel
        # rotation for effect
        self.rot = max(min(-self.vel * 3, 25), -90)
        self.rect.topleft = (int(self.x), int(self.y))

    def jump(self):
        self.vel = JUMP_STRENGTH

    def draw(self, surface):
        # simple bird: circle (head) + small wing
        center = (int(self.x + self.width / 2), int(self.y + self.height / 2))
        pygame.draw.ellipse(surface, BIRD_COLOR, self.rect)
        # eye
        eye_r = max(2, self.width // 10)
        eye_pos = (center[0] + self.width // 6, center[1] - self.height // 6)
        pygame.draw.circle(surface, (0, 0, 0), eye_pos, eye_r)

class Pipe:
    def __init__(self, x, gap_y):
        self.x = x
        self.gap_y = gap_y  # y position of top of gap
        self.width = 80
        self.passed = False

    def update(self):
        self.x -= PIPE_SPEED

    def offscreen(self):
        return self.x + self.width < 0

    def collides_with(self, bird_rect):
        # top pipe rect
        top_rect = pygame.Rect(self.x, 0, self.width, self.gap_y)
        bottom_rect = pygame.Rect(self.x, self.gap_y + PIPE_GAP, self.width, HEIGHT - (self.gap_y + PIPE_GAP))
        return bird_rect.colliderect(top_rect) or bird_rect.colliderect(bottom_rect)

    def draw(self, surface):
        top_rect = pygame.Rect(int(self.x), 0, self.width, int(self.gap_y))
        bottom_rect = pygame.Rect(int(self.x), int(self.gap_y + PIPE_GAP), self.width, HEIGHT - int(self.gap_y + PIPE_GAP))
        pygame.draw.rect(surface, PIPE_COLOR, top_rect)
        pygame.draw.rect(surface, PIPE_COLOR, bottom_rect)
        # add simple caps
        cap_h = 10
        pygame.draw.rect(surface, PIPE_COLOR, (self.x - 1, self.gap_y - cap_h, self.width + 2, cap_h))

# ------------ Main Game -------------
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Flappy (Python) — Subham's Clone")
    clock = pygame.time.Clock()
    font_big = pygame.font.Font(FONT_NAME, 48)
    font_small = pygame.font.Font(FONT_NAME, 22)

    highscore = load_highscore()

    def new_game():
        bird = Bird(WIDTH * 0.2, HEIGHT * 0.45)
        pipes = []
        # create initial pipes spaced out
        start_x = WIDTH + 100
        for i in range(3):
            gap_y = random.randint(120, HEIGHT - 300)
            pipes.append(Pipe(start_x + i * PIPE_DISTANCE, gap_y))
        score = 0
        ground_y = HEIGHT - 80
        game_over = False
        return bird, pipes, score, ground_y, game_over

    bird, pipes, score, ground_y, game_over = new_game()
    spawn_timer = 0

    running = True
    show_start_text = True

    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game_over:
                        bird, pipes, score, ground_y, game_over = new_game()
                        show_start_text = True
                    else:
                        bird.jump()
                        show_start_text = False
                if event.key == pygame.K_ESCAPE:
                    running = False
                    break
            if event.type == pygame.MOUSEBUTTONDOWN:
                if game_over:
                    bird, pipes, score, ground_y, game_over = new_game()
                    show_start_text = True
                else:
                    bird.jump()
                    show_start_text = False

        if not running:
            break

        # Update game only if not game over
        if not game_over:
            bird.update()

            # spawn pipes
            spawn_timer += 1
            if spawn_timer > PIPE_DISTANCE // PIPE_SPEED:
                spawn_timer = 0
                gap_y = random.randint(120, HEIGHT - 300)
                pipes.append(Pipe(WIDTH + 40, gap_y))

            # update pipes and check collisions/passing
            for p in pipes:
                p.update()
                if not p.passed and p.x + p.width < bird.x:
                    p.passed = True
                    score += 1
                if p.collides_with(bird.rect):
                    game_over = True

            # remove offscreen pipes
            pipes = [p for p in pipes if not p.offscreen()]

            # ground collision
            if bird.y + bird.height >= ground_y:
                bird.y = ground_y - bird.height
                game_over = True
            if bird.y < -50:
                # flew off top
                bird.y = -50
                bird.vel = 0

        # Draw everything
        screen.fill(BG_COLOR)

        # background simple gradient/rect
        pygame.draw.rect(screen, BG_COLOR, (0, 0, WIDTH, HEIGHT))

        # pipes
        for p in pipes:
            p.draw(screen)

        # ground
        ground_rect = pygame.Rect(0, ground_y, WIDTH, HEIGHT - ground_y)
        pygame.draw.rect(screen, GROUND_COLOR, ground_rect)

        # bird
        bird.draw(screen)

        # score
        score_surf = font_big.render(str(score), True, WHITE)
        score_rect = score_surf.get_rect(center=(WIDTH // 2, 100))
        screen.blit(score_surf, score_rect)

        # highscore
        if score > highscore:
            highscore = score
            save_highscore(highscore)

        hs_surf = font_small.render(f"HIGH: {highscore}", True, WHITE)
        screen.blit(hs_surf, (10, 10))

        # instructions or game over
        if show_start_text and not game_over:
            info = font_small.render("Press SPACE / Click to flap — Avoid the pipes!", True, WHITE)
            info_r = info.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(info, info_r)

        if game_over:
            over = font_big.render("GAME OVER", True, (220, 20, 60))
            over_r = over.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
            screen.blit(over, over_r)

            sub = font_small.render("Press SPACE / Click to restart", True, WHITE)
            sub_r = sub.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))
            screen.blit(sub, sub_r)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
