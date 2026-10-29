#!/usr/bin/env python3
"""Richtet die Trainingspläne des Trainingsbuchs in PocketBase ein.

Neue Sammlung `trainingsplaene` (ein Datensatz = ein Plan):
    member    Text     Kennung des Mitglieds, dem der Plan gehört
    name      Text     Name des Plans, z. B. "Oberkörper"
    typ       Auswahl  fest (Reihenfolge fix, nur "Gerät besetzt") | flexibel (frei änderbar)
    tage      JSON     [{name, uebungen: [{exercise, sets, reps, gewicht, rir}]}]
    quelle    Auswahl  eigen | coach
    vorlage   Text     Kennung der Coach-Vorlage, aus der der Plan kopiert wurde (später)
Jedes Mitglied sieht und ändert nur die eigenen Pläne.

Neue optionale Felder in `trainingsbuch_entries`:
    plan_id   Text     Plan, nach dem trainiert wurde
    plan_tag  Text     Name des Trainingstags im Plan

Ohne die Sammlung speichert das Trainingsbuch Pläne nur im Browser des Geräts.

Das Skript ist idempotent und ändert nur fehlende Felder und fehlende Sammlungen.

Aufruf
    python3 tools/richte-trainingsplaene-ein.py              # Probelauf
    python3 tools/richte-trainingsplaene-ein.py --schreiben  # ausführen

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
    {'name': 'plan_id', 'type': 'text', 'required': False, 'max': 40},
    {'name': 'plan_tag', 'type': 'text', 'required': False, 'max': 80},
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


PLAENE = 'trainingsplaene'
EIGENE = 'member = @request.auth.id'


def plaene(schreiben):
    """Legt die Sammlung für die Trainingspläne an, falls sie fehlt."""
    try:
        api(f'api/collections/{PLAENE}')
        print(f'= {PLAENE} ist bereits angelegt')
        return
    except PBFehler as e:
        if e.status != 404:
            if e.status in (401, 403):
                print(f'+ {PLAENE} würde angelegt (kein Lesezugriff auf das Schema im Probelauf)')
                return
            raise
    print(f'+ Sammlung {PLAENE} {"wird" if schreiben else "würde"} angelegt')
    if not schreiben:
        return
    api('api/collections', 'POST', {
        'name': PLAENE,
        'type': 'base',
        'fields': [
            {'name': 'member', 'type': 'text', 'required': True, 'max': 40},
            {'name': 'name', 'type': 'text', 'required': True, 'max': 120},
            {'name': 'typ', 'type': 'select', 'required': True, 'maxSelect': 1, 'values': ['fest', 'flexibel']},
            {'name': 'tage', 'type': 'json', 'required': False, 'maxSize': 200000},
            {'name': 'quelle', 'type': 'select', 'required': False, 'maxSelect': 1, 'values': ['eigen', 'coach']},
            {'name': 'vorlage', 'type': 'text', 'required': False, 'max': 40},
        ],
        'listRule': EIGENE,
        'viewRule': EIGENE,
        'createRule': '@request.auth.id != "" && @request.body.member = @request.auth.id',
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
    else:
        print(f'+ Felder {"werden" if schreiben else "würden"} ergänzt: ' + ', '.join(f['name'] for f in neu))
        if schreiben:
            api(f'api/collections/{sammlung["id"]}', 'PATCH', {'fields': felder + neu})
    plaene(schreiben)
    if schreiben:
        print('Fertig.')


if __name__ == '__main__':
    try:
        main()
    except PBFehler as e:
        sys.exit(f'Fehler: {e}')
