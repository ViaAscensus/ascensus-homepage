#!/usr/bin/env python3
"""Legt die PocketBase-Collection `trainingsbuch_motivation` an und füllt sie.

Die Collection enthält die Motivationssätze, die das Trainingsbuch nach
"Training beenden" in der Zusammenfassung zeigt (trainingsbuch.html, Funktion
pickMotivation). Ohne die Collection nutzt die Seite eingebaute Standardsätze.

Felder
    satz    Text, Pflicht, höchstens 200 Zeichen
    gruppe  Auswahl, Pflicht: rekord | normal | pause
              rekord  Training mit mindestens einem neuen Rekord
              normal  Training ohne Rekord
              pause   Training nach mehr als 7 Tagen Abstand zum letzten Training

API-Regeln
    list / view   jeder angemeldete Nutzer (@request.auth.id != "")
    create / update / delete   gesperrt (null) - nur Superuser, also Patrick in
                               der PocketBase-Oberfläche oder dieses Skript

Das Skript ist idempotent: Eine vorhandene Collection bekommt nur die fehlenden
Felder, die Regeln und den Index; Sätze, die es schon gibt (gleicher Text in
gleicher Gruppe), werden nicht doppelt angelegt. Eigene Sätze und Änderungen
bleiben unberührt.

Aufruf
    python3 tools/richte-trainingsbuch-motivation-ein.py              # Probelauf
    python3 tools/richte-trainingsbuch-motivation-ein.py --schreiben  # ausführen

Zugang (Schema anlegen darf nur ein Superuser, das api_clients-Konto reicht nicht)
  Das Skript fragt beim Start nach E-Mail und Passwort des PocketBase-Superusers:
    E-Mail [patrick@ascensus.fit]:   Enter übernimmt die Vorgabe
    Passwort:                        wird verdeckt eingegeben
  Beim Probelauf genügt ein leeres Passwort: Dann prüft das Skript nichts gegen
  PocketBase und zeigt nur, was es anlegen würde.
  Wer es ohne Nachfrage braucht, kann PB_EMAIL und PB_PASSWORD setzen oder ein
  Superuser-Token über PB_TOKEN (pur, ohne "Bearer"-Präfix wie bei den anderen
  Werkzeugen). PB_URL überschreibt die Adresse (Standard https://pb.ascensus.fit).

Voraussetzung: PocketBase ab Version 0.23 (Collection `_superusers`, `fields`).
"""
import getpass
import json
import os
import sys
import urllib.error
import urllib.request

PB = os.environ.get('PB_URL', 'https://pb.ascensus.fit').rstrip('/')
NAME = 'trainingsbuch_motivation'
GRUPPEN = ['rekord', 'normal', 'pause']

FELDER = [
    {'name': 'satz', 'type': 'text', 'required': True, 'min': 1, 'max': 200},
    {'name': 'gruppe', 'type': 'select', 'required': True, 'maxSelect': 1, 'values': GRUPPEN},
]

REGELN = {
    'listRule': '@request.auth.id != ""',
    'viewRule': '@request.auth.id != ""',
    'createRule': None,
    'updateRule': None,
    'deleteRule': None,
}

INDEX = f'CREATE INDEX idx_{NAME}_gruppe ON {NAME} (gruppe)'

# Startsammlung (identisch mit MOTIVATION_DEFAULT in trainingsbuch.html)
SAETZE = {
    'rekord': [
        'Neuer Bestwert, du Maschine!',
        'Rekord geknackt, das hat richtig gerumst!',
        'Mehr Gewicht als je zuvor, das ist Next Level.',
        'Heute hast du dich selbst überholt, stark!',
        'Neue Bestmarke, die Hantel hatte keine Chance.',
        'Boom, Rekord! So macht man das.',
        'Dein altes Ich schaut gerade neidisch zu.',
        'Neuer Rekord, gönn dir den Moment!',
    ],
    'normal': [
        'Training im Kasten, so wird das gemacht!',
        'Wieder eins geschafft, einfach dranbleiben.',
        'Du hast geliefert, wie immer.',
        'Eisen gestemmt, Haken dran.',
        'Kein Rekord heute, aber du warst da, und das zählt.',
        'Stark durchgezogen, Konstanz schlägt alles.',
        'Schweiß fließt, Fortschritt kommt, weiter so!',
        'Wieder eine Einheit mehr auf dem Konto.',
    ],
    'pause': [
        'Willkommen zurück, die Hanteln haben dich vermisst!',
        'Comeback geschafft, der schwerste Schritt ist getan.',
        'Pause vorbei, jetzt geht\'s wieder los!',
        'Schön, dass du wieder dabei bist, auf geht\'s!',
        'Der Neustart zählt mehr als die Pause davor.',
        'Zurück im Spiel, mach da weiter, wo du aufgehört hast.',
        'Du bist wieder da, und das ist die Hauptsache.',
        'Starker Wiedereinstieg, jetzt wird\'s wieder rund.',
    ],
}

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


def hole_collection():
    try:
        return api(f'api/collections/{NAME}')
    except PBFehler as e:
        if e.status == 404:
            return None
        raise


def fehlende_felder(vorhanden):
    namen = {f['name'] for f in vorhanden}
    return [f for f in FELDER if f['name'] not in namen]


def main():
    schreiben = '--schreiben' in sys.argv[1:]
    print(('AUSFÜHREN' if schreiben else 'PROBELAUF (nichts wird geschrieben, --schreiben zum Ausführen)')
          + f' gegen {PB}')

    if schreiben:
        anmelden(pflicht=True)
    else:
        # Der Probelauf liest nur; ohne Zugang meldet er, was zu tun wäre.
        try:
            anmelden(pflicht=False)
        except PBFehler as e:
            print(f'Anmeldung nicht möglich ({e}); Probelauf ohne Zugang.')

    try:
        sammlung = hole_collection()
    except PBFehler as e:
        if e.status in (401, 403):
            sammlung = None
            print('Kein Lesezugriff auf das Schema (Superuser nötig) - Probelauf nimmt an, dass die Collection fehlt.')
        else:
            raise

    if sammlung is None:
        print(f'+ Collection {NAME} {"wird" if schreiben else "würde"} angelegt: Felder satz, gruppe; '
              'Regeln: lesen für Angemeldete, schreiben nur Superuser')
        if schreiben:
            sammlung = api('api/collections', 'POST', {
                'name': NAME, 'type': 'base', 'fields': FELDER,
                'indexes': [INDEX], **REGELN,
            })
            print(f'  angelegt (id {sammlung.get("id")})')
    else:
        felder = sammlung.get('fields', [])
        neu = fehlende_felder(felder)
        aenderungen = {}
        if neu:
            aenderungen['fields'] = felder + neu
            print(f'+ fehlende Felder würden ergänzt: {", ".join(f["name"] for f in neu)}')
        for regel, soll in REGELN.items():
            if sammlung.get(regel) != soll:
                aenderungen[regel] = soll
                print(f'+ Regel {regel}: {sammlung.get(regel)!r} -> {soll!r}')
        if INDEX.split(' ON ')[0] not in ' '.join(sammlung.get('indexes', [])):
            aenderungen['indexes'] = sammlung.get('indexes', []) + [INDEX]
            print('+ Index auf gruppe würde ergänzt')
        if not aenderungen:
            print(f'= Collection {NAME} ist bereits wie vorgesehen')
        elif schreiben:
            api(f'api/collections/{sammlung["id"]}', 'PATCH', aenderungen)
            print('  Collection aktualisiert')

    # Sätze ergänzen
    vorhanden = set()
    if sammlung is not None and (schreiben or token):
        seite = 1
        while True:
            antwort = api(f'api/collections/{NAME}/records?perPage=200&page={seite}')
            vorhanden |= {(r.get('gruppe'), r.get('satz')) for r in antwort.get('items', [])}
            if seite >= antwort.get('totalPages', 1):
                break
            seite += 1

    angelegt = 0
    for gruppe, saetze in SAETZE.items():
        for satz in saetze:
            if (gruppe, satz) in vorhanden:
                continue
            angelegt += 1
            if schreiben:
                api(f'api/collections/{NAME}/records', 'POST', {'satz': satz, 'gruppe': gruppe})
    print(f'{"+ " if angelegt else "= "}{angelegt} Sätze {"angelegt" if schreiben else "würden angelegt"}'
          f' (von {sum(len(v) for v in SAETZE.values())} in der Startsammlung)')

    if schreiben:
        print('\nFertig. Neue oder geänderte Sätze pflegst Du in der PocketBase-Oberfläche '
              f'unter Collections > {NAME}.')


if __name__ == '__main__':
    try:
        main()
    except PBFehler as e:
        sys.exit(f'Fehler: {e}')
