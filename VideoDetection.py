import cv2
import numpy as np
from threading import Thread
from queue import Queue


RESET_COLOR = "\033[0m"
RED_COLOR = "\033[91m"
GREEN_COLOR = "\033[92m"


WHITE_THRESHOLD_HIT = 0.35
WHITE_THRESHOLD_NO_HIT = 0.05


mask_queue = Queue()
camera = cv2.VideoCapture(0)


def analyze_image_continuously():
    if not camera.isOpened():
        print("Fehler: Kamera konnte nicht geöffnet werden.")
        return

    print("Drücke 'q', um das Programm zu beenden.")


    def analyze_frame(frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)


        lower_white = np.array([0, 0, 200])
        upper_white = np.array([180, 30, 255])
        white_mask = cv2.inRange(hsv, lower_white, upper_white)


        contours, _ = cv2.findContours(white_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        large_contours = [c for c in contours if cv2.contourArea(c) > 500]  # Mindestfläche


        debug_frame = frame.copy()
        cv2.drawContours(debug_frame, large_contours, -1, (0, 255, 0), 2)


        white_pixels = sum(cv2.contourArea(c) for c in large_contours)
        total_pixels = white_mask.size
        white_percentage = white_pixels / total_pixels


        mask_queue.put((debug_frame, white_mask, white_percentage))

    def main_loop():
        while True:
            ret, frame = camera.read()
            if not ret:
                print("Fehler: Konnte kein Bild lesen.")
                break

            # Frame analysieren
            analyze_frame(frame)

            # Masken anzeigen, falls verfügbar
            if not mask_queue.empty():
                debug_frame, white_mask, white_percentage = mask_queue.get()

                # Zeige Masken und Debug-Frame
                cv2.imshow("Live-Ansicht", frame)
                cv2.imshow("Konturen", debug_frame)
                cv2.imshow("Weißmaske", white_mask)

                # Weißanteil ausgeben und basierend auf den Schwellenwerten entscheiden
                if white_percentage == 0:  # Kein Weißanteil mehr vorhanden
                    print(f"{GREEN_COLOR}**Treffer!** Kein Weißanteil erkannt.{RESET_COLOR}")
                elif white_percentage >= WHITE_THRESHOLD_HIT:  # Weißanteil 35% oder mehr
                    print(f"{RED_COLOR}Kein Treffer! Weißanteil: {white_percentage:.2%}{RESET_COLOR}")
                elif white_percentage <= WHITE_THRESHOLD_NO_HIT:  # Weißanteil 5% oder weniger
                    print(f"{RED_COLOR}**kein Treffer!** Weißanteil: {white_percentage:.2%}{RESET_COLOR}")
                else:
                    print(f"Zwischenzustand: Weißanteil: {white_percentage:.2%}")

            # 'q' zum Beenden überprüfen
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Programm beendet.")
                break

        # Ressourcen freigeben
        camera.release()
        cv2.destroyAllWindows()

    # Hauptloop ausführen
    main_loop()

# Methode ausführen
analyze_image_continuously()
