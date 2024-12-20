import pygame
import random
import sys
import math
from queue import Queue

# Kommunikation: Signal aus der Videodetektion
signal_queue = Queue()

pygame.init()

# Bildschirmkonfiguration
SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Wall Ball")

# Farben
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Variablen
BALL_RADIUS = 30
BALL_SPEED = 3
LEFT_RIGHT_MARGIN = 100
TOP_BOTTOM_MARGIN = 50
TEXT_HEIGHT = 50
game_over = False
ball_visible = True
level = 1  # Startlevel

# Sichere Bewegungsfläche des Balls
MOVEMENT_AREA_WIDTH = SCREEN_WIDTH - 2 * LEFT_RIGHT_MARGIN
MOVEMENT_AREA_HEIGHT = SCREEN_HEIGHT - TOP_BOTTOM_MARGIN - TEXT_HEIGHT

# Bullseye-Klasse
class HoloKick:
    def __init__(self):
        self.radius = BALL_RADIUS
        self.x, self.y = self.set_initial_position()
        self.color = WHITE
        self.dx, self.dy = self.set_speed()

    def set_initial_position(self):
        return (
            random.randint(LEFT_RIGHT_MARGIN + self.radius, LEFT_RIGHT_MARGIN + MOVEMENT_AREA_WIDTH - self.radius),
            random.randint(TOP_BOTTOM_MARGIN + TEXT_HEIGHT + self.radius, TOP_BOTTOM_MARGIN + TEXT_HEIGHT + MOVEMENT_AREA_HEIGHT - self.radius)
        )

    def set_speed(self):
        angle = random.uniform(0, 2 * math.pi)
        speed = BALL_SPEED
        return speed * math.cos(angle), speed * math.sin(angle)

    def draw(self):
        if ball_visible:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

    def move(self):
        self.x += self.dx
        self.y += self.dy

        if self.x - self.radius < LEFT_RIGHT_MARGIN:
            self.x = LEFT_RIGHT_MARGIN + self.radius
            self.dx *= -1
        if self.x + self.radius > LEFT_RIGHT_MARGIN + MOVEMENT_AREA_WIDTH:
            self.x = LEFT_RIGHT_MARGIN + MOVEMENT_AREA_WIDTH - self.radius
            self.dx *= -1
        if self.y - self.radius < TOP_BOTTOM_MARGIN + TEXT_HEIGHT:
            self.y = TOP_BOTTOM_MARGIN + TEXT_HEIGHT + self.radius
            self.dy *= -1
        if self.y + self.radius > TOP_BOTTOM_MARGIN + TEXT_HEIGHT + MOVEMENT_AREA_HEIGHT:
            self.y = TOP_BOTTOM_MARGIN + TEXT_HEIGHT + MOVEMENT_AREA_HEIGHT - self.radius
            self.dy *= -1

# Spiel Schleife
def main():
    global game_over, ball_visible, bullseye, level
    clock = pygame.time.Clock()
    font = pygame.font.Font('PressStart2P-Regular.ttf', 28)

    bullseye = HoloKick()

    while True:
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Prüfe auf Treffer-Signal von der Videodetektion
        if not signal_queue.empty():
            signal = signal_queue.get()
            if signal == "HIT":
                level += 1  # Level erhöhen
                bullseye = HoloKick()  # Neuen Ball erstellen
                print(f"Level erhöht! Aktuelles Level: {level}")

        bullseye.move()
        bullseye.draw()

        level_text = font.render(f"Level: {level}", True, WHITE)
        screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, 10))

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
