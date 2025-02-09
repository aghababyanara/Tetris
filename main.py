import pygame
import random
import sys

import pygame.examples

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)

# Init pygame
pygame.init()

# Screen dimessions
SCREEN_WIDTH, SCREEN_HEIGHT = 360, 600
GRID_SIZE = 30
COLUMNS = SCREEN_WIDTH // GRID_SIZE
ROWS = SCREEN_HEIGHT // GRID_SIZE

# Game screen and font
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris Game")
font = pygame.font.Font(None, 36)

# Tetris shapes
SHAPES = [
    [[1, 1, 1, 1]],  # I shape
    [[1, 1], [1, 1]],  # O shape
    [[0, 1, 0], [1, 1, 1]],  # T shape
    [[1, 1, 0], [0, 1, 1]],  # S shape
    [[0, 1, 1], [1, 1, 0]],  # Z shape
    [[1, 0, 0], [1, 1, 1]],  # L shape
    [[0, 0, 1], [1, 1, 1]],  # J shape
]

# Global Variables
board = [[0] * COLUMNS for _ in range(ROWS)]
current_piece = None
reserved_current_piece = None
current_pos = [0, 0]
score = 0
game_speed = 500


def rotate_shape_clockwise(shape):
    return [list(row) for row in zip(*reversed(shape))]


def rotate_all_variants(shape):
    variants = [shape]
    for _ in range(3):
        shape = rotate_shape_clockwise(shape)
        variants.append(shape)
    return variants


class Tetromino:
    def __init__(self, shape):
        self.shape_variants = rotate_all_variants(shape)
        self.color = random.choice([RED, GREEN, BLUE, CYAN, MAGENTA, YELLOW])
        self.rotation = 0

    def get_shape(self):
        return self.shape_variants[self.rotation]

    def rotate(self):
        self.rotation = (self.rotation + 1) % len(self.shape_variants)


def draw_board():
    screen.fill(WHITE)

    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))

    for row in range(ROWS):
        for col in range(COLUMNS):
            if board[row][col]:
                pygame.draw.rect(
                    screen,
                    board[row][col],
                    (
                        col * GRID_SIZE,
                        row * GRID_SIZE,
                        GRID_SIZE,
                        GRID_SIZE
                    )
                )

    if current_piece:
        shape = current_piece.get_shape()
        for row in range(len(shape)):
            for col in range(len(shape[row])):
                if shape[row][col]:
                    x = current_pos[1] + col
                    y = current_pos[0] + row
                    if 0 <= y < ROWS and 0 <= x < COLUMNS:
                        pygame.draw.rect(
                            screen,
                            current_piece.color,
                            (
                                x * GRID_SIZE,
                                y * GRID_SIZE,
                                GRID_SIZE,
                                GRID_SIZE,
                            )
                        )


def check_collision(pos, shape):
    for row in range(len(shape)):
        for col in range(len(shape[row])):
            if shape[row][col]:
                x = pos[1] + col
                y = pos[0] + row
                if x < 0 or x >= COLUMNS or y >= ROWS or board[y][x]:
                    return True
    return False


def lock_piece():
    global current_piece, current_pos, score
    shape = current_piece.get_shape()
    for row in range(len(shape)):
        for col in range(len(shape[row])):
            if shape[row][col]:
                x = current_pos[1] + col
                y = current_pos[0] + row
                board[y][x] = current_piece.color

    clear_lines()
    current_piece = None


def clear_lines():
    global score
    full_lines = [row for row in range(ROWS) if all(board[row])]
    for row in full_lines:
        del board[row]
        board.insert(0, [0] * COLUMNS)
    score += len(full_lines)


def new_piece():
    global current_piece, current_pos
    current_piece = Tetromino(random.choice(SHAPES))

    current_pos = [0, COLUMNS // 2 - len(current_piece.get_shape()[0]) // 2]

    if check_collision(current_pos, current_piece.get_shape()):
        return False
    return True


def display_message(text, button_texts):
    screen.fill(WHITE)
    message = font.render(text, True, BLACK)
    screen.blit(message, (
        SCREEN_WIDTH // 2 - message.get_width() // 2, SCREEN_HEIGHT // 4)
    )

    buttons = []

    for i, text in enumerate(button_texts):
        button_rect = pygame.Rect(
            SCREEN_WIDTH // 2 - 100,
            SCREEN_HEIGHT // 3 + i * 60,
            200,
            50
        )
        buttons.append((button_rect, text))
        pygame.draw.rect(screen, GREEN, button_rect)
        button_label = font.render(text, True, BLACK)
        screen.blit(button_label, (button_rect.x + 10, button_rect.y + 10))

    pygame.display.flip()
    return buttons


def choose_level():
    buttons = display_message(
        "Select Game Level",
        ["Normal", "Medium", "Hard", "Exit Game"]
    )
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button_rect, text in buttons:
                    if button_rect.collidepoint(event.pos):
                        if text == "Exit Game":
                            pygame.quit()
                            sys.exit()
                        return text.lower()


def game_over_screen():
    buttons = display_message(
        f"Game Over. Your Score {score}",
        ["Play Again", "Exit Game"]
    )
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button_rect, text in buttons:
                    if button_rect.collidepoint(event.pos):
                        if text == "Play Again":
                            return True
                        else:
                            pygame.quit()
                            sys.exit()


def main():
    global current_piece, current_pos, score, game_speed
    running = True
    clock = pygame.time.Clock()

    level = choose_level()
    match level:
        case "normal": game_speed = 500
        case "medium": game_speed = 300
        case "hard": game_speed = 150
        case _: level = "normal"

    fall_time = 0
    key_press_time = {pygame.K_DOWN: 0, pygame.K_LEFT: 0, pygame.K_RIGHT: 0}
    new_piece()

    while running:
        draw_board()
        pygame.display.flip()
        delta_time = clock.tick()
        fall_time += delta_time

        keys = pygame.key.get_pressed()
        if keys[pygame.K_DOWN]:
            key_press_time[pygame.K_DOWN] += delta_time
            if key_press_time[pygame.K_DOWN] > 100:
                key_press_time[pygame.K_DOWN] = 0
                new_pos = [current_pos[0] + 1, current_pos[1]]
                if not check_collision(new_pos, current_piece.get_shape()):
                    current_pos = new_pos
        if keys[pygame.K_LEFT]:
            key_press_time[pygame.K_LEFT] += delta_time
            if key_press_time[pygame.K_LEFT] > 150:
                key_press_time[pygame.K_LEFT] = 0
                new_pos = [current_pos[0], current_pos[1] - 1]
                if not check_collision(new_pos, current_piece.get_shape()):
                    current_pos = new_pos
        if keys[pygame.K_RIGHT]:
            key_press_time[pygame.K_RIGHT] += delta_time
            if key_press_time[pygame.K_RIGHT] > 150:
                key_press_time[pygame.K_RIGHT] = 0
                new_pos = [current_pos[0], current_pos[1] + 1]
                if not check_collision(new_pos, current_piece.get_shape()):
                    current_pos = new_pos

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    current_piece.rotate()
                    new_pos = [current_pos[0], current_pos[1]]
                    if check_collision(new_pos, current_piece.get_shape()):
                        current_piece.rotate()

        if fall_time >= game_speed:
            fall_time = 0
            new_pos = [current_pos[0] + 1, current_pos[1]]
            if not check_collision(new_pos, current_piece.get_shape()):
                current_pos = new_pos
            else:
                lock_piece()
                if not new_piece():
                    if game_over_screen():
                        board[:] = [[0] * COLUMNS for _ in range(ROWS)]
                        score = 0
                        level = choose_level()
                        game_speed = {"normal": 500,
                                      "medium": 300, "hard": 150}[level]
                    else:
                        running = False

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()