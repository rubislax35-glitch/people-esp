# People ESP

Eine Python/Kivy-App für Android: Live-Kamerabild, Umschaltung zwischen Rück- und Frontkamera sowie ein ESP-Schalter, der erkannte Personen mit Rahmen markiert.

## GitHub-APK-Download

Der Workflow in `.github/workflows/android.yml` baut das Android-APK auf GitHub Actions. Nach dem Hochladen des Projekts:

1. Öffne **Actions** und starte **Build Android APK** (oder warte auf den Build nach einem Push).
2. Öffne den fertigen Lauf und lade unter **Artifacts** `people-esp-apk` herunter.
3. Übertrage die APK auf dein Android-Handy, öffne sie und bestätige die Installation. Erlaube danach den Kamerazugriff.

Wenn ein Tag wie `v0.1.0` gepusht wird, hängt der Workflow die APK zusätzlich an eine GitHub Release-Seite an.

## Bedienung

- **Rückkamera / Frontkamera** wechselt zwischen Kamera 0 und 1.
- **ESP AN** schaltet die lokale Personen-Erkennung und die Boxen ein.
- Die Erkennung nutzt OpenCVs eingebauten HOG-Personendetektor. Sie identifiziert keine Personen.
- Kamera-Bilder werden nur im Arbeitsspeicher verarbeitet und nicht gespeichert oder gesendet.

## Projekt

- `main.py`: Python-App
- `buildozer.spec`: Android-Paket- und Kameraeinstellungen
- `.github/workflows/android.yml`: APK-Build und Veröffentlichung

Der APK-Build läuft auf GitHub Actions (Linux) und braucht deshalb kein WSL auf deinem PC. Der erste Build lädt Android SDK/NDK und Python-for-Android-Abhängigkeiten. Die App ist aktuell Android-only.
