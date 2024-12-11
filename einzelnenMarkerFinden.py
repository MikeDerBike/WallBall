import cv2
import os
import np
from pyzbar.pyzbar import decode

# Verzeichnis der QR-Code-Bilder
qr_codes_dir = "/Users/skottie/PycharmProjects/BME3 Holokick/markers"
qr_code_files = [f for f in os.listdir(qr_codes_dir) if f.endswith(".png") or f.endswith(".jpg")]

# Lade und dekodiere die QR-Codes aus dem Ordner
stored_qr_codes = {}
for file_name in qr_code_files:
    file_path = os.path.join(qr_codes_dir, file_name)
    image = cv2.imread(file_path)
    if image is not None:
        decoded_objects = decode(image)
        if decoded_objects:
            # Speichere den ersten gefundenen QR-Code und seinen Inhalt
            qr_content = decoded_objects[0].data.decode("utf-8")
            stored_qr_codes[qr_content] = file_name
        else:
            print(f"Keine QR-Codes im Bild {file_name} gefunden.")

# Prüfe, ob QR-Codes geladen wurden
if not stored_qr_codes:
    print("Keine QR-Codes im Ordner gefunden. Beende das Programm.")
    exit(1)

print("QR-Codes geladen:")
for content, file_name in stored_qr_codes.items():
    print(f"QR-Code-Inhalt: '{content}' aus Datei: {file_name}")

# Webcam-Setup
cap = cv2.VideoCapture(0)

def analyze_frame(frame):
    """Sucht nach QR-Codes in einem Frame und vergleicht sie mit gespeicherten QR-Codes."""
    detected_qr_codes = decode(frame)

    for qr_code in detected_qr_codes:
        qr_content = qr_code.data.decode("utf-8")
        if qr_content in stored_qr_codes:
            print(f"Bekannter QR-Code erkannt! Inhalt: '{qr_content}' aus Datei: {stored_qr_codes[qr_content]}")
            # Optional: QR-Code umrahmen und anzeigen
            points = qr_code.polygon
            if len(points) > 4:  # QR-Code kann mehr als 4 Punkte haben (Polygon)
                hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
                points = hull
            points = [(int(point.x), int(point.y)) for point in points]
            for i in range(len(points)):
                cv2.line(frame, points[i], points[(i + 1) % len(points)], (0, 255, 0), 3)
            # Text anzeigen
            cv2.putText(frame, f"Erkannt: {qr_content}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            return True  # Erkennung erfolgreich
    return False  # Kein bekannter QR-Code gefunden

print("Starte QR-Code-Erkennung. Drücke 'q', um das Programm zu beenden.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Fehler beim Zugriff auf die Kamera.")
        break

    # Suche im Frame nach QR-Codes
    found = analyze_frame(frame)

    # Zeige den Frame im Fenster
    cv2.imshow("QR-Code-Erkennung", frame)

    # Beende das Programm mit 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
