import pygame
import random
import sys
import math

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
LEFT_RIGHT_MARGIN = 100  # Erweiterter Sicherheitsabstand für links und rechts
TOP_BOTTOM_MARGIN = 80   # Sicherheitsabstand für oben (inkl. Schrift) und unten
TEXT_HEIGHT = 50         # Bereich, den die Schrift oben beansprucht
game_over = False

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
        # Ball startet nur innerhalb des sicheren Bereichs
        return (
            random.randint(LEFT_RIGHT_MARGIN + self.radius, LEFT_RIGHT_MARGIN + MOVEMENT_AREA_WIDTH - self.radius),
            random.randint(TOP_BOTTOM_MARGIN + TEXT_HEIGHT + self.radius, TOP_BOTTOM_MARGIN + TEXT_HEIGHT + MOVEMENT_AREA_HEIGHT - self.radius)
        )

    def set_speed(self):
        angle = random.uniform(0, 2 * math.pi)
        speed = BALL_SPEED
        return speed * math.cos(angle), speed * math.sin(angle)

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

    def is_clicked(self, pos):
        distance = math.sqrt((pos[0] - self.x) ** 2 + (pos[1] - self.y) ** 2)
        return distance <= self.radius

    def move(self):
        # Bewege den Ball innerhalb der sicheren Fläche
        self.x += self.dx
        self.y += self.dy

        # Prallt an den virtuellen Grenzen der sicheren Fläche ab
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
    global game_over, bullseye
    clock = pygame.time.Clock()

    # Lade den Retro-Font
    font = pygame.font.Font('PressStart2P-Regular.ttf', 28)

    # Erstelle das erste Bullseye
    bullseye = HoloKick()

    while True:
        screen.fill(BLACK)

        # Ereignisse
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                if bullseye.is_clicked(event.pos):
                    bullseye = HoloKick()
                else:
                    game_over = True

            if event.type == pygame.KEYDOWN:
                if game_over and event.key == pygame.K_r:
                    game_over = False
                    bullseye = HoloKick()
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        bullseye.move()
        bullseye.draw()

        # Welcome-Text anzeigen
        welcome_text = font.render("Welcome to Wall Ball", True, WHITE)
        screen.blit(welcome_text, (SCREEN_WIDTH // 2 - welcome_text.get_width() // 2, 10))

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
