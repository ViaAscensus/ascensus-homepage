#!/usr/bin/env python3
"""Rechnet die Tags vom Typ "berechnet" aus den Naehrwerten neu.

Fuenf der sechs Tags mit `typ: berechnet` in PocketBase folgen aus den Zahlen
des Rezepts. Gepflegt wurden sie bisher von Hand, und zwar ohne erkennbare
Regel: gegen jede denkbare Schwelle gerechnet lag die Uebereinstimmung zwischen
26 und 63 Prozent. Der Schaden liegt vor allem im Fehlen — viele Rezepte
erfuellen eine Bedingung, tragen das Tag aber nicht und sind ueber den Filter
nicht zu finden.

Dieses Werkzeug setzt sie deterministisch:

  High-Protein          Eiweiss >= 20 % der kcal      VO (EG) 1924/2006
  High-Carb             Kohlenhydrate >= 50 % der kcal
  Low-Carb              Kohlenhydrate <= 20 % der kcal
  Kalorienarm           <= 400 kcal je Portion
  Schnell und einfach   zeit_gesamt zwischen 1 und 30 Minuten

**Ballaststoffreich bleibt unberuehrt.** Das Feld `ballaststoffe` ist bei den
unveroeffentlichten Rezepten durchweg 0 und die Zutatenzeilen fuehren keine
Ballaststoffe — es gibt schlicht nichts zu rechnen. Solange keine Datenquelle
da ist, bleibt das Tag so stehen, wie es gesetzt wurde.

  python3 tools/berechne-tags.py                # Probelauf
  python3 tools/berechne-tags.py --schreiben
  python3 tools/berechne-tags.py --schreiben --log tag-aenderungen.md

Danach tools/build-rezepte.py laufen lassen: die Tags stehen als Badges auf den
Seiten und im Kachel-Grid.
"""
import collections, json, os, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PB = 'https://pb.ascensus.fit/api/collections'


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


# Die einzige Stelle, an der die Schwellen stehen. tools/pruefe-rezepte.py liest
# sie von hier, damit Rechnen und Pruefen nicht auseinanderlaufen koennen.
GRENZE = {
    'High-Protein':        20,    # Eiweiss-Anteil an den kcal, in Prozent
    'High-Carb':           50,    # Kohlenhydrat-Anteil an den kcal, in Prozent
    'Low-Carb':            20,    # Kohlenhydrat-Anteil an den kcal, in Prozent
    'Kalorienarm':        400,    # kcal je Portion
    'Schnell und einfach': 30,    # Minuten gesamt
    'Ballaststoffreich':    5,    # g je Portion - nur zum Pruefen, nicht zum Rechnen
}


def anteil(r, feld):
    """Anteil eines Makronaehrstoffs an den Kalorien, in Prozent."""
    return 4 * r[feld] / r['kcal'] * 100 if r['kcal'] else None


# Jede Regel gibt True, False oder None zurueck. None heisst: nicht entscheidbar,
# dann bleibt das Tag so, wie es ist.
REGELN = {
    'High-Protein':        lambda r: None if not r['kcal'] else anteil(r, 'eiweiss') >= GRENZE['High-Protein'],
    'High-Carb':           lambda r: None if not r['kcal'] else anteil(r, 'kohlenhydrate') >= GRENZE['High-Carb'],
    'Low-Carb':            lambda r: None if not r['kcal'] else anteil(r, 'kohlenhydrate') <= GRENZE['Low-Carb'],
    'Kalorienarm':         lambda r: None if not r['kcal'] else r['kcal'] <= GRENZE['Kalorienarm'],
    'Schnell und einfach': lambda r: None if not r['zeit_gesamt'] else r['zeit_gesamt'] <= GRENZE['Schnell und einfach'],
}
UNBERUEHRT = 'Ballaststoffreich'


def main():
    schreiben = '--schreiben' in sys.argv
    logdatei = None
    if '--log' in sys.argv:
        logdatei = ROOT / 'tools' / sys.argv[sys.argv.index('--log') + 1]

    tags = alle('tags')
    tagid = {t['name']: t['id'] for t in tags}
    tagname = {t['id']: t['name'] for t in tags}
    fehlend = [n for n in REGELN if n not in tagid]
    if fehlend:
        sys.exit(f'Diese Tags gibt es in PocketBase nicht: {fehlend}')

    rezepte = alle('rezepte')
    veroeffentlicht = set(json.loads(
        (ROOT / 'tools' / 'slug-map.json').read_text(encoding='utf-8')))

    plan, dazu, weg, unklar = {}, collections.Counter(), collections.Counter(), collections.Counter()
    for r in rezepte:
        ist = set(r['tags'])
        neu = set(ist)
        notiz = []
        for name, regel in REGELN.items():
            soll = regel(r)
            tid = tagid[name]
            if soll is None:
                unklar[name] += 1
                continue                       # nicht entscheidbar, unveraendert lassen
            if soll and tid not in neu:
                neu.add(tid); dazu[name] += 1; notiz.append(f'+{name}')
            elif not soll and tid in neu:
                neu.discard(tid); weg[name] += 1; notiz.append(f'-{name}')
        if neu != ist:
            plan[r['id']] = {'name': r['name'], 'tags': sorted(neu), 'notiz': notiz,
                             'live': r['id'] in veroeffentlicht}

    live = sum(1 for v in plan.values() if v['live'])
    print(f'{len(plan)} von {len(rezepte)} Rezepten bekommen andere Tags '
          f'({live} davon veroeffentlicht)\n')
    print(f'{"Tag":22s} {"dazu":>6} {"weg":>6} {"unklar":>7}')
    for n in REGELN:
        print(f'{n:22s} {dazu[n]:6d} {weg[n]:6d} {unklar[n]:7d}')
    print(f'\n{UNBERUEHRT} bleibt unberuehrt (keine Ballaststoffdaten).')

    zeilen = ['# Neuberechnung der Tags vom Typ "berechnet"', '',
              f'{len(plan)} Rezepte geaendert, davon {live} veroeffentlichte.',
              'Erzeugt von `tools/berechne-tags.py`.', '',
              '| Rezept | live | Änderung |', '|---|---|---|']
    for rid, e in sorted(plan.items(), key=lambda x: x[1]['name']):
        zeilen.append(f'| {e["name"]} | {"ja" if e["live"] else ""} | {" ".join(e["notiz"])} |')

    if not schreiben:
        print('\n(Probelauf - es wurde nichts geschrieben. Mit --schreiben ausfuehren.)')
        return

    print()
    for n, (rid, e) in enumerate(plan.items(), 1):
        api(f'rezepte/records/{rid}', 'PATCH', {'tags': e['tags']})
        if n % 50 == 0 or n == len(plan):
            print(f'  {n}/{len(plan)} geschrieben')

    if logdatei:
        logdatei.write_text('\n'.join(zeilen) + '\n', encoding='utf-8')
        print(f'\nProtokoll: {logdatei.relative_to(ROOT)}')
    print('\nJetzt tools/build-rezepte.py laufen lassen.')


if __name__ == '__main__':
    main()
