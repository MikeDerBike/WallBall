import cv2
import numpy as np
from threading import Thread
from queue import Queue

# Setup für die Kommunikation mit dem Spiel
signal_queue = Queue()

RESET_COLOR = "\033[0m"
RED_COLOR = "\033[91m"
GREEN_COLOR = "\033[92m"

WHITE_THRESHOLD_HIT = 0.35  # Schwelle für Treffer
WHITE_THRESHOLD_NO_HIT = 0.05  # Schwelle für "kein Treffer"

# Externe Kamera einrichten
camera_index = 2  # Index für die externe Kamera (bei Bedarf anpassen)
camera = cv2.VideoCapture(camera_index)

def analyze_image_continuously():
    if not camera.isOpened():
        print("Fehler: Kamera konnte nicht geöffnet werden. Bitte überprüfen Sie die Kameraquelle.")
        return

    print("Drücke 'q', um die Videodetektion zu beenden.")

    while True:
        ret, frame = camera.read()
        if not ret:
            print("Fehler: Konnte kein Bild lesen.")
            break

        # Konvertiere das Bild in HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Weiß maskieren
        lower_white = np.array([0, 0, 200])
        upper_white = np.array([180, 30, 255])
        white_mask = cv2.inRange(hsv, lower_white, upper_white)

        # Konturen finden
        contours, _ = cv2.findContours(white_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        large_contours = [c for c in contours if cv2.contourArea(c) > 500]  # Mindestfläche

        # Debug-Frame erstellen
        debug_frame = frame.copy()
        cv2.drawContours(debug_frame, large_contours, -1, (0, 255, 0), 2)

        # Weißanteil berechnen
        white_pixels = sum(cv2.contourArea(c) for c in large_contours)
        total_pixels = white_mask.size
        white_percentage = white_pixels / total_pixels

        # Treffer-Erkennung basierend auf Weißanteil
        if white_percentage == 0:  # Kein Weißanteil erkannt
            print(f"{GREEN_COLOR}**Treffer!** Kein Weißanteil erkannt.{RESET_COLOR}")
            signal_queue.put("HIT")  # Signal an das Spiel senden
        elif white_percentage >= WHITE_THRESHOLD_HIT:  # Weißanteil 35% oder mehr
            print(f"{RED_COLOR}Kein Treffer. Weißanteil: {white_percentage:.2%}{RESET_COLOR}")
        elif white_percentage <= WHITE_THRESHOLD_NO_HIT:  # Weißanteil 5% oder weniger
            print(f"{RED_COLOR}**kein Treffer!** Weißanteil: {white_percentage:.2%}{RESET_COLOR}")
        else:
            print(f"Zwischenzustand: Weißanteil: {white_percentage:.2%}")

        # Zeige das Bild und die Maske an
        cv2.imshow("Live-Ansicht", frame)
        cv2.imshow("Konturen", debug_frame)
        cv2.imshow("Weißmaske", white_mask)

        # 'q' zum Beenden überprüfen
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Videodetektion beendet.")
            break

    # Kamera freigeben und Fenster schließen
    camera.release()
    cv2.destroyAllWindows()

# Videodetektion in einem separaten Thread starten
video_thread = Thread(target=analyze_image_continuously, daemon=True)
video_thread.start()
