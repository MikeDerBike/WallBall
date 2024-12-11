import pygame
import cv2
import numpy as np
import random
import math
from queue import Queue
import sys
import time

# Farben für die Konsole
RESET_COLOR = "\033[0m"
RED_COLOR = "\033[91m"
GREEN_COLOR = "\033[92m"

# Konfigurationen
SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 800
BALL_RADIUS = 30
BASE_BALL_SPEED = 3
LEFT_RIGHT_MARGIN = 100
TOP_BOTTOM_MARGIN = 50
TEXT_HEIGHT = 50
WHITE_THRESHOLD_HIT = 0.35
CAMERA_INDEX = 1  # Kamera-Index

# Farben für das Spiel
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


# Signal Queue
signal_queue = Queue()


# Spielklasse
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Wall Ball")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font('freesansbold.ttf', 28)
        self.level = 1
        self.ball = self.WallBall(self.level)

    class WallBall:
        def __init__(self, level):
            self.radius = BALL_RADIUS
            self.x, self.y = self.set_initial_position()
            self.color = WHITE
            self.dx, self.dy = self.set_speed(level)

        def set_initial_position(self):
            return (
                random.randint(LEFT_RIGHT_MARGIN + BALL_RADIUS, SCREEN_WIDTH - LEFT_RIGHT_MARGIN - BALL_RADIUS),
                random.randint(TOP_BOTTOM_MARGIN + TEXT_HEIGHT + BALL_RADIUS,
                               SCREEN_HEIGHT - TOP_BOTTOM_MARGIN - BALL_RADIUS)
            )

        def set_speed(self, level):
            speed = BASE_BALL_SPEED + level * 0.5
            angle = random.uniform(0, 2 * math.pi)
            return speed * math.cos(angle), speed * math.sin(angle)

        def draw(self, screen):
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

        def move(self):
            self.x += self.dx
            self.y += self.dy

            if self.x - self.radius < LEFT_RIGHT_MARGIN:
                self.x = LEFT_RIGHT_MARGIN + self.radius
                self.dx *= -1
            if self.x + self.radius > SCREEN_WIDTH - LEFT_RIGHT_MARGIN:
                self.x = SCREEN_WIDTH - LEFT_RIGHT_MARGIN - self.radius
                self.dx *= -1
            if self.y - self.radius < TOP_BOTTOM_MARGIN + TEXT_HEIGHT:
                self.y = TOP_BOTTOM_MARGIN + TEXT_HEIGHT + self.radius
                self.dy *= -1
            if self.y + self.radius > SCREEN_HEIGHT - TOP_BOTTOM_MARGIN:
                self.y = SCREEN_HEIGHT - TOP_BOTTOM_MARGIN - self.radius
                self.dy *= -1

    def update(self):
        self.screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Prüfe auf Treffer-Signal
        if not signal_queue.empty():
            signal = signal_queue.get()
            if signal == "HIT":
                self.level += 1
                print(f"Level erhöht! Aktuelles Level: {self.level}")
                self.ball = self.WallBall(self.level)

        self.ball.move()
        self.ball.draw(self.screen)

        # Level anzeigen
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, 10))

        pygame.display.flip()
        self.clock.tick(60)


# Kameradetektion Klasse
class CameraDetection:
    def __init__(self):
        self.camera = cv2.VideoCapture(CAMERA_INDEX)
        if not self.camera.isOpened():
            print(f"Fehler: Kamera konnte nicht geöffnet werden. Kamera-Index: {CAMERA_INDEX}")
            sys.exit()

    def update(self):
        ret, frame = self.camera.read()
        if not ret:
            print("Fehler: Konnte kein Bild lesen.")
            return

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Weiß maskieren
        lower_white = np.array([0, 0, 200])
        upper_white = np.array([180, 30, 255])
        white_mask = cv2.inRange(hsv, lower_white, upper_white)

        # Konturen finden
        contours, _ = cv2.findContours(white_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        large_contours = [c for c in contours if cv2.contourArea(c) > 500]

        # Weißanteil berechnen
        white_pixels = sum(cv2.contourArea(c) for c in large_contours)
        total_pixels = white_mask.size
        white_percentage = white_pixels / total_pixels

        # Treffer-Erkennung basierend auf Weißanteil
        if white_percentage == 0:
            print(f"{GREEN_COLOR}**Treffer!** Kein Weißanteil erkannt.{RESET_COLOR}")
            signal_queue.put("HIT")
        elif white_percentage >= WHITE_THRESHOLD_HIT:
            print(f"{RED_COLOR}Kein Treffer. Weißanteil: {white_percentage:.2%}{RESET_COLOR}")

        cv2.imshow("Live-Ansicht", frame)
        cv2.imshow("Weißmaske", white_mask)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Videodetektion beendet.")
            self.camera.release()
            cv2.destroyAllWindows()
            sys.exit()


# Hauptfunktion
def main():
    game = Game()
    camera = CameraDetection()

    last_camera_update = time.time()
    camera_update_interval = 0.03  # Aktualisiere die Kamera alle 30 ms

    while True:
        current_time = time.time()

        # Aktualisiere die Kameradetektion in festgelegten Intervallen
        if current_time - last_camera_update >= camera_update_interval:
            camera.update()
            last_camera_update = current_time

        # Aktualisiere das Spiel
        game.update()


if __name__ == "__main__":
    main()
