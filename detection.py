import cv2
import os
import sounddevice as sd
import numpy as np
import time

# Verzeichnis der Marker-Bilder
markers_dir = "/Users/skottie/PycharmProjects/BME3 Holokick/markers"
marker_files = [f for f in os.listdir(markers_dir) if f.startswith("marker_")]
marker_images = {os.path.splitext(f)[0]: cv2.imread(os.path.join(markers_dir, f), cv2.IMREAD_GRAYSCALE) for f in
                 marker_files}
if markers_dir is None:
    print(f"Fehler: Marker-Bild konnte nicht geladen werden.")


# Grenzwert für Lautstärke
volume_threshold = 40.0

# Pause nach jeder Verarbeitung (in Sekunden)
photo_cooldown = 1

# Zeitpunkt der letzten Verarbeitung
last_photo_time = 0

# Webcam-Setup
cap = cv2.VideoCapture(0)

def analyze_frame(frame):
    # Spiegle das Bild horizontal
    flipped_frame = cv2.flip(frame, 1)

    # Konvertiere das Bild in Graustufen
    gray_frame = cv2.cvtColor(flipped_frame, cv2.COLOR_BGR2GRAY)

    # Optional: Glätten des Bildes
    gray_frame = cv2.GaussianBlur(gray_frame, (5, 5), 0)

    # Erkannte Marker
    detected_markers = []

    # Verwende Template Matching für jeden Marker
    for marker_name, marker_image in marker_images.items():
        res = cv2.matchTemplate(gray_frame, marker_image, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        # Definiere einen Schwellenwert für das Matching
        if max_val > 0.5:  # 80% Übereinstimmung
            detected_markers.append(marker_name)

    # Debug-Ausgabe der erkannten Marker
    print(f"Erkannte Marker: {detected_markers}")

    # Entscheide basierend auf den erkannten Markern
    if all(f"marker_{i}" in detected_markers for i in range(4)):  # Marker_0 bis Marker_3
        if "marker_4" in detected_markers:
            print("Ziel nicht getroffen")
        else:
            print("Ziel getroffen")
    else:
        print("Markers wurden nicht vollständig erkannt")


# Callback-Funktion für das Mikrofon-Streaming
def audio_callback(indata, frames, callback_time, status):
    global last_photo_time

    # Berechne die Lautstärke des Mikrofonsignals
    volume_norm = np.linalg.norm(indata) * 10

    # Lautstärke überschreitet den Schwellenwert und die Abklingzeit ist vorbei
    if volume_norm > volume_threshold and (time.time() - last_photo_time) > photo_cooldown:
        print(f"Lautstärke überschritten: {volume_norm:.2f}")

        # Ein Bild von der Webcam aufnehmen
        ret, frame = cap.read()
        if ret:
            # Bild analysieren
            analyze_frame(frame)

            # Aktualisiere den Zeitpunkt der letzten Verarbeitung
            last_photo_time = time.time()


# Mikrofonüberwachung starten
def start_microphone_monitoring():
    # Sample-Rate für das Mikrofon (hier 44100 Hz)
    samplerate = 44100
    # 1-Kanal (Mono) Mikrofonüberwachung
    with sd.InputStream(callback=audio_callback, channels=1, samplerate=samplerate):
        print("Mikrofonüberwachung gestartet. Drücke 'Strg+C', um zu beenden.")
        while True:
            # Endlosschleife, um das Mikrofon weiter zu überwachen
            sd.sleep(5000)


try:
    start_microphone_monitoring()
except KeyboardInterrupt:
    print("Programm beendet.")
finally:
    # Webcam und alle Fenster freigeben
    cap.release()
    cv2.destroyAllWindows()
