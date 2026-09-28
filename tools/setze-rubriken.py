#!/usr/bin/env python3
"""Setzt die Rubrik (kategorie) der Rezepte, soweit sie aus den Tags folgt.

Das Feld kategorie ist in PocketBase ein Select mit genau fuenf Optionen:
Fruehstueck, Mittag, Abendessen, Snack, Vor dem Training. Nachtisch und
Grundrezept stehen zwar in KATEGORIE in build-rezepte.py, sind in der
Datenbank aber ungueltig - Nachtische landen deshalb unter Snack, was der
Kachel-Filter ohnehin als "Snack & Suesses" fuehrt.

Ableitung, erste Regel gewinnt:

  Tag Fruehstueck                          -> Fruehstueck
  Tag Pre Workout                          -> Vor dem Training
  Tag Nachtisch / Snack / Midday-Snack /
      Getraenk                             -> Snack
  sonst                                    -> Hauptgericht, siehe --haupt

Hauptgerichte bleiben unberuehrt, solange --haupt fehlt: fuer sie gibt es
keine eigene Option, die Entscheidung gehoert dem Betreiber.

  python3 tools/setze-rubriken.py                    # Probelauf
  python3 tools/setze-rubriken.py --schreiben        # nur die ableitbaren
  python3 tools/setze-rubriken.py --schreiben --haupt Mittag
"""
import collections, json, os, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PB = 'https://pb.ascensus.fit/api/collections'
ERLAUBT = {'Fruehstueck', 'Mittag', 'Abendessen', 'Snack', 'Vor dem Training'}


def api(pfad, method='GET', body=None):
    daten = json.dumps(body).encode() if body else None
    r = urllib.request.Request(f'{PB}/{pfad}', data=daten, method=method)
    if os.environ.get('PB_TOKEN'):
        r.add_header('Authorization', os.environ['PB_TOKEN'])
    if body:
        r.add_header('Content-Type', 'application/json')
    with urllib.request.urlopen(r, timeout=60) as resp:
        return json.load(resp)


def alle(coll):
    out, seite = [], 1
    while True:
        d = api(f'{coll}/records?perPage=500&page={seite}')
        out += d['items']
        if seite >= d['totalPages']:
            break
        seite += 1
    return out


def rubrik(tn):
    if 'Fruehstueck' in tn:
        return 'Fruehstueck'
    if 'Pre Workout' in tn:
        return 'Vor dem Training'
    if tn & {'Nachtisch', 'Snack', 'Midday-Snack', 'Getränk'}:
        return 'Snack'
    return None          # Hauptgericht


def main():
    schreiben = '--schreiben' in sys.argv
    haupt = None
    if '--haupt' in sys.argv:
        haupt = sys.argv[sys.argv.index('--haupt') + 1]
        if haupt not in ERLAUBT:
            sys.exit(f'--haupt {haupt!r} ist keine gueltige Option: {sorted(ERLAUBT)}')

    tags = {t['id']: t['name'] for t in alle('tags')}
    rezepte = alle('rezepte')

    plan = {}
    for r in rezepte:
        if (r['kategorie'] or '').strip():
            continue                               # schon gesetzt, nichts anfassen
        k = rubrik({tags[t] for t in r['tags'] if t in tags}) or haupt
        if k:
            plan[r['id']] = (r['name'], k)

    verteilung = collections.Counter(k for _, k in plan.values())
    offen = sum(1 for r in rezepte
                if not (r['kategorie'] or '').strip() and r['id'] not in plan)
    print(f'{len(plan)} Rezepte bekommen eine Rubrik, {offen} bleiben offen\n')
    for k, v in verteilung.most_common():
        print(f'  {v:4d}  {k}')

    if not schreiben:
        print('\n(Probelauf - es wurde nichts geschrieben. Mit --schreiben ausfuehren.)')
        return

    print()
    for n, (rid, (name, k)) in enumerate(plan.items(), 1):
        api(f'rezepte/records/{rid}', 'PATCH', {'kategorie': k})
        if n % 25 == 0 or n == len(plan):
            print(f'  {n}/{len(plan)} geschrieben')


if __name__ == '__main__':
    main()
