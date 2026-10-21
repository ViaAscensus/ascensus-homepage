#!/usr/bin/env python3
"""Ergänzt `trainingsbuch_entries` um die Felder für Pausenzeiten und Laufband.

Das Trainingsbuch (trainingsbuch.html) schreibt bei jedem Satz mit, wie lange die
Pause davor war: von "Satz beenden" bis zum nächsten "Satz beginnen".

Felder (alle optional, alte Einträge bleiben unverändert)
    training_id   Text     Kennung des Trainings; trennt mehrere Trainings am selben Tag.
                           Einträge ohne Kennung zählen pro Datum als ein Training.
    pause_s       Zahl     gemessene Pause in Sekunden
    pause_typ     Auswahl  satz (gleiche Übung) | wechsel (Wechselzeit zur nächsten Übung)
    pause_soll_s  Zahl     eingestellte Timer-Zeit in Sekunden, gegen die verglichen wird
    dauer_s       Zahl     Laufband: gemessene Dauer in Sekunden
    distanz_km    Zahl     Laufband: eingetragene Distanz in km

`pause_typ` dient als Marker: PocketBase liefert für leere Zahlenfelder alter
Einträge 0, daran ließen sich alte und neue Einträge sonst nicht unterscheiden.
Solange die Felder fehlen, ignoriert PocketBase sie beim Speichern; die Auswertung
zeigt dann "Noch keine Pausenzeiten erfasst".

Das Skript ist idempotent und ändert nur fehlende Felder. Rechte bleiben unberührt.

Aufruf
    python3 tools/richte-trainingsbuch-pausen-ein.py              # Probelauf
    python3 tools/richte-trainingsbuch-pausen-ein.py --schreiben  # ausführen

Zugang: Superuser (E-Mail und Passwort werden abgefragt, oder PB_TOKEN bzw.
PB_EMAIL/PB_PASSWORD; PB_URL überschreibt die Adresse).
"""
import getpass
import json
import os
import sys
import urllib.error
import urllib.request

PB = os.environ.get('PB_URL', 'https://pb.ascensus.fit').rstrip('/')
NAME = 'trainingsbuch_entries'

FELDER = [
    {'name': 'pause_s', 'type': 'number', 'required': False, 'min': 0, 'onlyInt': True},
    {'name': 'pause_typ', 'type': 'select', 'required': False, 'maxSelect': 1, 'values': ['satz', 'wechsel']},
    {'name': 'pause_soll_s', 'type': 'number', 'required': False, 'min': 0, 'onlyInt': True},
    {'name': 'training_id', 'type': 'text', 'required': False, 'max': 40},
    {'name': 'dauer_s', 'type': 'number', 'required': False, 'min': 0, 'onlyInt': True},
    {'name': 'distanz_km', 'type': 'number', 'required': False, 'min': 0},
]

token = os.environ.get('PB_TOKEN')


class PBFehler(Exception):
    def __init__(self, status, text):
        super().__init__(f'HTTP {status}: {text}')
        self.status = status


def api(pfad, methode='GET', body=None):
    daten = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(f'{PB}/{pfad}', data=daten, method=methode)
    r.add_header('Content-Type', 'application/json')
    if token:
        r.add_header('Authorization', token)
    try:
        with urllib.request.urlopen(r, timeout=60) as resp:
            inhalt = resp.read()
            return json.loads(inhalt) if inhalt else {}
    except urllib.error.HTTPError as e:
        raise PBFehler(e.code, e.read().decode('utf-8', 'replace')[:300]) from None


STANDARD_EMAIL = 'patrick@ascensus.fit'


def frage(text, verdeckt=False):
    """Fragt auf dem Terminal nach; ohne Terminal (z. B. Pipe) gilt die Eingabe als leer."""
    try:
        return (getpass.getpass(text) if verdeckt else input(text)).strip()
    except EOFError:
        return ''


def anmelden(pflicht):
    """Fragt E-Mail und Passwort des Superusers ab und meldet an.

    Mit PB_TOKEN oder PB_EMAIL/PB_PASSWORD in der Umgebung gibt es keine Nachfrage.
    Gibt False zurück, wenn der Probelauf bewusst ohne Passwort läuft.
    """
    global token
    if token:
        return True
    email = os.environ.get('PB_EMAIL') or frage(f'E-Mail [{STANDARD_EMAIL}]: ') or STANDARD_EMAIL
    passwort = os.environ.get('PB_PASSWORD') or frage(f'Passwort für {email}: ', verdeckt=True)
    if not passwort:
        if pflicht:
            sys.exit('Ohne Passwort kann nichts angelegt werden.')
        print('Kein Passwort eingegeben: Probelauf ohne Zugang.')
        return False
    antwort = api('api/collections/_superusers/auth-with-password', 'POST',
                  {'identity': email, 'password': passwort})
    token = antwort['token']
    print(f'Angemeldet als {email}')
    return True


def main():
    schreiben = '--schreiben' in sys.argv[1:]
    print(('AUSFÜHREN' if schreiben else 'PROBELAUF (nichts wird geschrieben, --schreiben zum Ausführen)')
          + f' gegen {PB}')
    if schreiben:
        anmelden(pflicht=True)
    else:
        try:
            anmelden(pflicht=False)
        except PBFehler as e:
            print(f'Anmeldung nicht möglich ({e}); Probelauf ohne Zugang.')
    try:
        sammlung = api(f'api/collections/{NAME}')
    except PBFehler as e:
        if e.status in (401, 403):
            print('Kein Lesezugriff auf das Schema (Superuser nötig): Probelauf nimmt an, dass alle Felder fehlen.')
            print('+ würde ergänzen: ' + ', '.join(f['name'] for f in FELDER))
            return
        raise
    felder = sammlung.get('fields', [])
    namen = {f['name'] for f in felder}
    neu = [f for f in FELDER if f['name'] not in namen]
    if not neu:
        print(f'= {NAME} hat alle Felder bereits')
        return
    print(f'+ Felder {"werden" if schreiben else "würden"} ergänzt: ' + ', '.join(f['name'] for f in neu))
    if schreiben:
        api(f'api/collections/{sammlung["id"]}', 'PATCH', {'fields': felder + neu})
        print('Fertig. Ab jetzt speichert das Trainingsbuch Pausen und Laufband-Daten.')


if __name__ == '__main__':
    try:
        main()
    except PBFehler as e:
        sys.exit(f'Fehler: {e}')
