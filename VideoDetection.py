import cv2
import numpy as np
import sounddevice as sd
from threading import Lock, Thread
from queue import Queue

# Einstellbare Schwellenwerte
VOLUME_THRESHOLD = 0.2  # Lautstärkeschwellenwert
WHITE_THRESHOLD_HIT = 0.0  # Schwellenwert für "Kein Treffer!" (35% Weißanteil)
WHITE_THRESHOLD_NO_HIT = 0.0007  # Schwellenwert für "Treffer!" (5% Weißanteil)

# Globale Variablen
mask_queue = Queue()
frame_queue = Queue()
camera = cv2.VideoCapture(0)

# Hauptmethode
def analyze_audio_and_image():
    if not camera.isOpened():
        print("Fehler: Kamera konnte nicht geöffnet werden.")
        return

    print("Drücke 'q', um das Programm zu beenden. Sprich laut genug, um die Analyse auszulösen.")

    # Funktion zur Audioverarbeitung
    def audio_callback(indata, frames, time, status):
        if status:
            print(f"Audio-Fehler: {status}")
        # Lautstärke berechnen
        volume = np.sqrt(np.mean(indata ** 2))
        if volume > VOLUME_THRESHOLD:
            if not frame_queue.empty():
                frame = frame_queue.get()
                analyze_frame(frame)

    # Funktion zur Bildverarbeitung und Weißanteilsberechnung
    def analyze_frame(frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Masken für weißen Bereich erstellen
        lower_white = np.array([0, 0, 200])  # Niedrigste Sättigung und hohe Helligkeit für Weiß
        upper_white = np.array([180, 30, 255])  # Maximale Sättigung und Helligkeit für Weiß
        white_mask = cv2.inRange(hsv, lower_white, upper_white)

        # Nur signifikante zusammenhängende weiße Bereiche berücksichtigen
        contours, _ = cv2.findContours(white_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        large_contours = [c for c in contours if cv2.contourArea(c) > 500]  # Mindestfläche

        # Debugging: Konturen zeichnen
        debug_frame = frame.copy()
        cv2.drawContours(debug_frame, large_contours, -1, (0, 255, 0), 2)

        # Weißanteil berechnen
        white_pixels = sum(cv2.contourArea(c) for c in large_contours)
        total_pixels = white_mask.size
        white_percentage = white_pixels / total_pixels

        # Ergebnis und Masken in die Queue schreiben
        mask_queue.put((debug_frame, white_mask, white_percentage))

    # Hauptloop für Kameraanzeige und Masken
    def main_loop():
        while True:
            ret, frame = camera.read()
            if not ret:
                print("Fehler: Konnte kein Bild lesen.")
                break

            # Frame in die Queue legen
            if frame_queue.empty():
                frame_queue.put(frame)

            # Masken anzeigen, falls verfügbar
            if not mask_queue.empty():
                debug_frame, white_mask, white_percentage = mask_queue.get()

                # Zeige Masken und Debug-Frame
                cv2.imshow("Live-Ansicht", frame)
                cv2.imshow("Konturen", debug_frame)
                cv2.imshow("Weißmaske", white_mask)

                # Weißanteil ausgeben und basierend auf den Schwellenwerten entscheiden
                if white_percentage == 0:  # Kein Weißanteil mehr vorhanden
                    print(f"**Treffer!** Kein Weißanteil erkannt.")
                elif white_percentage >= WHITE_THRESHOLD_HIT:  # Weißanteil 35% oder mehr
                    print(f"Kein Treffer! Weißanteil: {white_percentage:.2%}")
                elif white_percentage <= WHITE_THRESHOLD_NO_HIT:  # Weißanteil 5% oder weniger
                    print(f"**Treffer!** Weißanteil: {white_percentage:.2%}")
                else:
                    print(f"Zwischenzustand: Weißanteil: {white_percentage:.2%}")

            # 'q' zum Beenden überprüfen
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Programm beendet.")
                break

        # Ressourcen freigeben
        camera.release()
        cv2.destroyAllWindows()

    # Audiostream in einem Thread starten
    audio_thread = Thread(target=lambda: sd.InputStream(callback=audio_callback).start())
    audio_thread.start()

    # Hauptloop ausführen
    main_loop()

# Methode ausführen
analyze_audio_and_image()
