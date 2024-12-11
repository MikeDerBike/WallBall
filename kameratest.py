import cv2
import numpy as np
from threading import Thread
from queue import Queue

# Kommunikation: Signal Queue
signal_queue = Queue()

# Konfiguration
camera_index = 1  # Externe Kamera
WHITE_THRESHOLD_HIT = 0.35  # Schwelle für Treffer

# Farben für Konsolenausgabe
RESET_COLOR = "\033[0m"
RED_COLOR = "\033[91m"
GREEN_COLOR = "\033[92m"

def analyze_image_continuously():
    camera = cv2.VideoCapture(camera_index)

    if not camera.isOpened():
        print("Fehler: Kamera konnte nicht geöffnet werden.")
        return

    print("Drücke 'q', um die Videodetektion zu beenden.")

    while True:
        ret, frame = camera.read()
        if not ret:
            print("Fehler: Konnte kein Bild lesen.")
            break

        # Bild in HSV konvertieren
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Weiß maskieren
        lower_white = np.array([0, 0, 200])
        upper_white = np.array([180, 30, 255])
        white_mask = cv2.inRange(hsv, lower_white, upper_white)

        # Konturen finden
        contours, _ = cv2.findContours(white_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        large_contours = [c for c in contours if cv2.contourArea(c) > 500]  # Mindestfläche

        # Weißanteil berechnen
        white_pixels = sum(cv2.contourArea(c) for c in large_contours)
        total_pixels = white_mask.size
        white_percentage = white_pixels / total_pixels

        # Treffer-Erkennung basierend auf Weißanteil
        if white_percentage == 0:  # Kein Weißanteil erkannt
            print(f"{GREEN_COLOR}**Treffer!** Kein Weißanteil erkannt.{RESET_COLOR}")
            signal_queue.put("HIT")
        elif white_percentage >= WHITE_THRESHOLD_HIT:  # Weißanteil 35% oder mehr
            print(f"{RED_COLOR}Kein Treffer. Weißanteil: {white_percentage:.2%}{RESET_COLOR}")

        # Fenster anzeigen
        cv2.imshow("Live-Ansicht", frame)
        cv2.imshow("Weißmaske", white_mask)

        # 'q' zum Beenden überprüfen
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Videodetektion beendet.")
            break

    camera.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":

    analyze_image_continuously()
