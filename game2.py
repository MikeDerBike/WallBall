import pygame
import random
import sys
import math
from queue import Queue
from threading import Thread
from kameratest import signal_queue  # Importiere die Signal-Queue

# Bildschirmkonfiguration
pygame.init()
SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Wall Ball")

# Farben
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Variablen
BALL_RADIUS = 30
BASE_BALL_SPEED = 3  # Basisgeschwindigkeit des Balls
LEFT_RIGHT_MARGIN = 100
TOP_BOTTOM_MARGIN = 50
TEXT_HEIGHT = 50
game_over = False
ball_visible = True
level = 1

MOVEMENT_AREA_WIDTH = SCREEN_WIDTH - 2 * LEFT_RIGHT_MARGIN
MOVEMENT_AREA_HEIGHT = SCREEN_HEIGHT - TOP_BOTTOM_MARGIN - TEXT_HEIGHT

# Bullseye-Klasse
class HoloKick:
    def __init__(self, level):
        self.radius = BALL_RADIUS
        self.x, self.y = self.set_initial_position()
        self.color = WHITE
        self.dx, self.dy = self.set_speed(level)

    def set_initial_position(self):
        return (
            random.randint(LEFT_RIGHT_MARGIN + self.radius, LEFT_RIGHT_MARGIN + MOVEMENT_AREA_WIDTH - self.radius),
            random.randint(TOP_BOTTOM_MARGIN + TEXT_HEIGHT + self.radius,
                           TOP_BOTTOM_MARGIN + TEXT_HEIGHT + MOVEMENT_AREA_HEIGHT - self.radius)
        )

    def set_speed(self, level):
        # Geschwindigkeit erhöht sich mit dem Level
        speed = BASE_BALL_SPEED + level * 0.5
        angle = random.uniform(0, 2 * math.pi)
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


# Spiel-Schleife
def main():
    global game_over, ball_visible, level

    clock = pygame.time.Clock()
    font = pygame.font.Font('freesansbold.ttf', 28)
    bullseye = HoloKick(level)

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
                level += 1
                bullseye = HoloKick(level)  # Erstelle neuen Ball mit aktualisiertem Level
                print(f"Level erhöht! Aktuelles Level: {level}")

        bullseye.move()
        bullseye.draw()

        # Level anzeigen
        level_text = font.render(f"Level: {level}", True, WHITE)
        screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, 10))

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    # Starte die Videodetektion in einem separaten Thread
    video_thread = Thread(target=lambda: __import__('videodetection').analyze_image_continuously)
    video_thread.start()

    # Starte das Spiel
    main()
