import cv2
import os
import numpy as np
import time

# Verzeichnis der Marker-Bilder
markers_dir = "/Users/skottie/PycharmProjects/BME3 Holokick/markers"
marker_files = [f for f in os.listdir(markers_dir) if f.startswith("marker_")]
marker_images = {
    os.path.splitext(f)[0]: cv2.imread(os.path.join(markers_dir, f), cv2.IMREAD_GRAYSCALE)
    for f in marker_files
}

# Validierung der Marker
for marker_name, marker_image in marker_images.items():
    if marker_image is None:
        print(f"Fehler: Marker-Bild {marker_name} konnte nicht geladen werden.")
        exit(1)

# Webcam-Setup
cap = cv2.VideoCapture(0)

def analyze_frame(frame):
    """Analysiert den Frame und erkennt Marker."""
    # Spiegle das Bild horizontal
    flipped_frame = cv2.flip(frame, 1)

    # Konvertiere das Bild in Graustufen
    gray_frame = cv2.cvtColor(flipped_frame, cv2.COLOR_BGR2GRAY)

    # Optionale Glättung
    gray_frame = cv2.GaussianBlur(gray_frame, (5, 5), 0)

    # Erkannte Marker
    detected_markers = []

    # Kopie für Markierungen (zum Debugging)
    debug_frame = flipped_frame.copy()

    for marker_name, marker_image in marker_images.items():
        best_match_value = 0
        best_match_location = None
        best_scale = 1.0

        # Suche den besten Match für jede Skalierung
        for scale in np.linspace(0.5, 1.5, num=10):
            resized_marker = cv2.resize(marker_image, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)

            # Marker darf nicht größer als der Frame sein
            if resized_marker.shape[0] > gray_frame.shape[0] or resized_marker.shape[1] > gray_frame.shape[1]:
                continue

            # Template Matching durchführen
            res = cv2.matchTemplate(gray_frame, resized_marker, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)

            # Besten Matchwert speichern
            if max_val > best_match_value:
                best_match_value = max_val
                best_match_location = max_loc
                best_scale = scale

        # Prüfen, ob der Matchwert über einem Schwellenwert liegt
        if best_match_value > 0.7:  # Schwellenwert für gültige Erkennung
            detected_markers.append(marker_name)

            # Bounding Box des erkannten Markers zeichnen (für Debugging)
            h, w = int(marker_image.shape[0] * best_scale), int(marker_image.shape[1] * best_scale)
            top_left = best_match_location
            bottom_right = (top_left[0] + w, top_left[1] + h)
            cv2.rectangle(debug_frame, top_left, bottom_right, (0, 255, 0), 2)
            cv2.putText(debug_frame, marker_name, (top_left[0], top_left[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Debug-Ausgabe der erkannten Marker
    print(f"Erkannte Marker: {detected_markers}")

    # Anzeige des Bildes mit Debug-Infos
    cv2.imshow("Erkannte Marker", debug_frame)

    # Entscheide basierend auf den erkannten Markern
    if len(detected_markers) == len(marker_images):  # Alle Marker erkannt
        print("Alle Marker erkannt!")
    elif detected_markers:
        print(f"Teilweise erkannte Marker: {detected_markers}")
    else:
        print("Keine Marker erkannt.")


# Hauptfunktion
def main():
    print("Starte Marker-Erkennung. Drücke 'q', um zu beenden.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Fehler beim Zugriff auf die Kamera.")
            break

        # Bild analysieren
        analyze_frame(frame)

        # 'q' zum Beenden
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


try:
    main()
except KeyboardInterrupt:
    print("Programm beendet.")
finally:
    cap.release()
    cv2.destroyAllWindows()
