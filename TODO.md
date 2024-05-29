# Server TODO

MUST-DO mit (!) gekennzeichnet

### Struktur
- (!) HTTP-Server-Handler zu Django portieren
- Globale Variablen beibehalten oder durch durchgereichten Parameter ersetzen (der halt immer gleich ist) (falls das mit der Datenbank nicht ohnehin wegfällt)
- Bessere Lösung für CommunicationConstants. Das sollten Konstanten sein, die die Schlüsselworte für die verschiedenen Message-Typen enthalten (damit da alles konsistent zwischen Worker und Server ist). Das es zwei separate (identische) Dateien sind, ist nicht wirklich eine gute Lösung, habe mir bisher aber auch noch keine Gedanken darüber gemacht wie man es stattdesssen macht

### Kommunikation
- regelmäßiges Heart-Beating an Worker
- weitere Befehle an Worker (Task stoppen, Task-Fortschritt (falls nicht vom Worker an Server gesendet), etc.)
- Server-seitige Deregistrierung von Workern

### Funktionalität
- (!!) Interaktion mit Front-End (Tasks entgegennehmen, Download des Ergebnisses anbieten)
- (!) Aufteilung auf mehrere Worker (siehe BlendFile.py -> BlendFile.read(), um Frame Range zu erhalten)
- (!) Zusamenschneiden der Render-Resultate (mit FFMPEG). Wir sollten uns anfangs auf ein Output-Format festlegen, bis ich (Tobi) aus der Blender-Datei auch das Output-Format auslese. Vorschlag für Festlegung bis dahin:
  [Screenshot:Blender Output-Config](TODO/BlenderOutputConfig.png)
- (!) Einstufung der Worker nach Leistung (und Aufteilung daran orientieren). Specs des Workers bei Registrierung übergeben
- Ein Interaktions-Interface wie in loop() beim Worker oder geht das über Django-Admin. Oder kann man sogar eine Python-Befehlszeile einbauen?