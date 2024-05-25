# BOOM Backend

Moin Jungs, da wir das Repo eh nur intern verwenden werde ich es mal verwenden, um zu erklären, worauf man bei der Entwicklung so achten muss.

## Setup

1. Github Repo clonen (Ich vertrau darauf, dass ihr das packt, ohne das ich jetzt hier einen Command hinpacke)
2. Einmalig beim Einrichten eine virtuelle Umgebung erstellen (falls ihr euch selbst hasst, könnt ihr auch alle Packages global installieren. Dafür:
    1. ```python3 -m venv venv```
    2. ```source venv/bin/activate``` (das auch jedes Mal machen, wenn ihr entwickeln wollt)
3. Dependencies installieren ```pip3 install -r requirements.txt``` oder halt mit pip falls ihr auf Windows seid (am besten jedes mal wenn ihr gepulled habt, falls packages hinzugefügt wurden)
4. .env Datei hinzufügen, also im gecloneten Ordner neue Datei mit namen .env und dann reinpasten, die sollte ungefähr das folgende Format haben
```
DJANGO_ENV=development
SECRET_KEY=29LGXbhV6pR1yke5pOySpd7VrlDZu2bHm1xjPqP1oe-b5ayRsUkeOKZU1cirCm63p30
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:8000
```

Das sollte es eigentlich sogar gewesen sein. Habe das jetzt einfach mal runtergeschrieben, ohne zu checken, ob tatsächlic alles richtig ist, wenn was Quatsch ist oder fehlt, müsst ihr sagen

## Testen

Wir haben uns ja noch nicht für eine Testing Library entschieden (falls wir das mit dem Testn überhaupt so ernst nehmen wollen), ich glaube sowas wie pytest bietet sich an, weil Django Integration. Sollten wir irgendwann mal Tests haben, machh ```python3 manage.py test```oder bei Windows stattdessen mit ```python```. Ansonsten wird auch bei Pushes oder Pull Requests getestet. 
Ansonsten zum Ausprobieren einfach einen lokalen Test-Server aufsetzen. Dafür müsst jhr die folgenden Schritte befolgen.
1. ```python3 manage.py makemigrations``` (um die Datenbankänderungen zu synchronisieren)
2. ```python3 manage.py migrate``` (um dle Änderungen auf die lokale Datenbank anzuwenden)
3. ```python3 manage.py collectstatic``` (höchstwahrscheinlich nicht immer nötig, aber schadet nicht)
4. ```python3 manage.py runserver```, dann läuft unter ```127.0.0.1:8000```ein Testserver und an den kann man dann einfach testweise die API requests schicken und gucken, was passiert. 

Falls es sonst och irgendwelche offenen Punkte gibt, schreibt die oder wenn es angemessen ist, öffnet ein Issue.

