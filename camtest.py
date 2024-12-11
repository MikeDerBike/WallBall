import cv2

# Öffne die Kamera (Index 0 für die erste Kamera, Index 1 für die zweite Kamera, etc.)
cap = cv2.VideoCapture(0)

# Überprüfe, ob die Kamera erfolgreich geöffnet wurde
if not cap.isOpened():
    print("Fehler: Kamera konnte nicht geöffnet werden.")
    exit()

while True:
    # Lese ein Frame von der Kamera
    ret, frame = cap.read()

    # Wenn das Frame erfolgreich gelesen wurde, zeige es an
    if ret:
        # Zeige das Frame in einem Fenster an
        cv2.imshow('Kamera Vorschau', frame)

    # Breche die Schleife ab, wenn die 'q'-Taste gedrückt wird
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Freigeben der Kamera und Schließen aller OpenCV-Fenster
cap.release()
cv2.destroyAllWindows()
