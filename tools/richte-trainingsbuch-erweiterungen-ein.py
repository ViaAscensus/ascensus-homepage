#!/usr/bin/env python3
"""Richtet Notizen und Körperwerte des Trainingsbuchs in PocketBase ein.

Neue Sammlung `uebung_notizen` (eine Notiz je Mitglied und Übung):
    member    Text    Kennung des Mitglieds
    uebung    Text    Name der Übung in Kleinbuchstaben
    notiz     Text    die Notiz (bis 500 Zeichen)

Neue Sammlung `koerperwerte` (ein Eintrag je Mitglied und Tag):
    member        Text    Kennung des Mitglieds
    datum         Text    Tag im Format JJJJ-MM-TT
    gewicht       Zahl    Körpergewicht in kg
    bauch, huefte, brust, oberarm, oberschenkel   Zahl   Umfänge in cm

Jedes Mitglied sieht und ändert nur die eigenen Datensätze. Ohne die Sammlungen
speichert das Trainingsbuch Notizen und Körperwerte nur im Browser des Geräts.

Das Skript ist idempotent und legt nur fehlende Sammlungen an.

Aufruf
    python3 tools/richte-trainingsbuch-erweiterungen-ein.py              # Probelauf
    python3 tools/richte-trainingsbuch-erweiterungen-ein.py --schreiben  # ausführen

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
EIGENE = 'member = @request.auth.id'
ANLEGEN = '@request.auth.id != "" && @request.body.member = @request.auth.id'

SAMMLUNGEN = {
    'uebung_notizen': [
        {'name': 'member', 'type': 'text', 'required': True, 'max': 40},
        {'name': 'uebung', 'type': 'text', 'required': True, 'max': 200},
        {'name': 'notiz', 'type': 'text', 'required': True, 'max': 500},
    ],
    'koerperwerte': [
        {'name': 'member', 'type': 'text', 'required': True, 'max': 40},
        {'name': 'datum', 'type': 'text', 'required': True, 'max': 10},
        {'name': 'gewicht', 'type': 'number', 'required': False, 'min': 0},
        {'name': 'bauch', 'type': 'number', 'required': False, 'min': 0},
        {'name': 'huefte', 'type': 'number', 'required': False, 'min': 0},
        {'name': 'brust', 'type': 'number', 'required': False, 'min': 0},
        {'name': 'oberarm', 'type': 'number', 'required': False, 'min': 0},
        {'name': 'oberschenkel', 'type': 'number', 'required': False, 'min': 0},
    ],
}

token = os.environ.get('PB_TOKEN')
STANDARD_EMAIL = 'patrick@ascensus.fit'


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


def sammlung(name, felder, schreiben):
    """Legt eine Sammlung mit Besitzer-Regeln an, falls sie fehlt."""
    try:
        api(f'api/collections/{name}')
        print(f'= {name} ist bereits angelegt')
        return
    except PBFehler as e:
        if e.status != 404:
            if e.status in (401, 403):
                print(f'+ {name} würde angelegt (kein Lesezugriff auf das Schema im Probelauf)')
                return
            raise
    print(f'+ Sammlung {name} {"wird" if schreiben else "würde"} angelegt')
    if not schreiben:
        return
    api('api/collections', 'POST', {
        'name': name,
        'type': 'base',
        'fields': felder,
        'listRule': EIGENE,
        'viewRule': EIGENE,
        'createRule': ANLEGEN,
        'updateRule': EIGENE,
        'deleteRule': EIGENE,
    })


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
    for name, felder in SAMMLUNGEN.items():
        sammlung(name, felder, schreiben)
    if schreiben:
        print('Fertig.')


if __name__ == '__main__':
    try:
        main()
    except PBFehler as e:
        sys.exit(f'Fehler: {e}')
