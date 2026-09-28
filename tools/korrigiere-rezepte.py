#!/usr/bin/env python3
"""Korrigiert die Befunde mit Aussenwirkung in PocketBase.

Zwei Klassen aus tools/PRUEFBERICHT-REZEPTE.md:

  A1-A4  Diaet-Tag widerspricht der Zutatenliste  -> Tag entfernen
  A5     Allergen nicht deklariert                -> Allergen ergaenzen

Beides sind Aussagen, die als falsch nach aussen gingen. Der Eingriff ist
bewusst konservativ: entfernt wird die Behauptung, nicht die Zutat. Ob ein
Rezept stattdessen auf eine vegane Zutat umgestellt werden soll, ist eine
inhaltliche Entscheidung und bleibt offen.

  python3 tools/korrigiere-rezepte.py              # Probelauf, schreibt nichts
  python3 tools/korrigiere-rezepte.py --schreiben  # aendert PocketBase
  python3 tools/korrigiere-rezepte.py --schreiben --log aenderungen.md
  python3 tools/korrigiere-rezepte.py --veroeffentlicht   # die Seiten online

Nach einem Lauf mit --veroeffentlicht muss tools/build-rezepte.py laufen, sonst
steht die Korrektur nur in der Datenbank und nicht auf der Seite.

Die Befunde stammen aus tools/pruefe-rezepte.py, damit beide Werkzeuge
dieselbe Zutatenerkennung benutzen.
"""
import json, os, re, subprocess, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PB = 'https://pb.ascensus.fit/api/collections'

# Welcher Befund welches Tag widerlegt
TAG_ZU_BEFUND = {
    'laktosefrei_falsch': 'Laktosefrei',
    'vegan_falsch':       'Vegan',
    'glutenfrei_falsch':  'Glutenfrei',
    'eggfree_falsch':     'EggFree',
    'vegetarisch_falsch': 'Vegetarisch',
}
# Der Pruefer schreibt die Allergene ohne Umlaute, die Datenbank mit
SCHREIBWEISE = {'Nuesse': 'Nüsse', 'Erdnuesse': 'Erdnüsse'}


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


def befunde():
    ruf = [sys.executable, str(ROOT / 'tools' / 'pruefe-rezepte.py'), '--json']
    if '--veroeffentlicht' in sys.argv:
        ruf.append('--veroeffentlicht')     # dann die Seiten, die online stehen
    r = subprocess.run(ruf, capture_output=True, text=True, cwd=ROOT)
    if r.returncode:
        sys.exit(f'pruefe-rezepte.py fehlgeschlagen:\n{r.stderr}')
    return json.loads(r.stdout)


def plane(B, rezepte, tagid):
    """-> {rezept_id: {'tags': [...], 'allergene': '...', 'warum': [...]}}"""
    plan = {}

    def eintrag(rid):
        r = rezepte[rid]
        return plan.setdefault(rid, {'name': r['name'], 'warum': []})

    # A1-A4: das widerlegte Tag entfernen
    for schluessel, tagname in TAG_ZU_BEFUND.items():
        for name, rid, zutat in B['befund'].get(schluessel, []):
            if tagname not in tagid:
                continue
            e = eintrag(rid)
            tags = e.get('tags', list(rezepte[rid]['tags']))
            if tagid[tagname] in tags:
                tags.remove(tagid[tagname])
                e['tags'] = tags
                e['warum'].append(f'Tag "{tagname}" entfernt (Zutat: {zutat})')

    # A5: fehlende Allergene ergaenzen, Bestehendes bleibt stehen
    for name, rid, text in B['befund'].get('allergen_fehlt', []):
        e = eintrag(rid)
        aktuell = (e.get('allergene') or rezepte[rid]['allergene'] or '').strip()
        vorhanden = [t.strip() for t in aktuell.split(',') if t.strip()]
        neu = []
        for teil in text.split('; '):
            a = teil.split(' (')[0]
            ausloeser = teil.split(' (')[1].rstrip(')') if ' (' in teil else ''
            a = SCHREIBWEISE.get(a, a)
            if a not in vorhanden and a not in neu:
                neu.append(a)
                e['warum'].append(f'Allergen "{a}" ergaenzt (Zutat: {ausloeser})')
        if neu:
            e['allergene'] = ', '.join(vorhanden + neu)
    return plan


def main():
    schreiben = '--schreiben' in sys.argv
    logdatei = None
    if '--log' in sys.argv:
        logdatei = ROOT / 'tools' / sys.argv[sys.argv.index('--log') + 1]

    B = befunde()
    rezepte = {r['id']: r for r in alle('rezepte')}
    tagid = {t['name']: t['id'] for t in alle('tags')}

    plan = plane(B, rezepte, tagid)
    ntags = sum(1 for v in plan.values() if 'tags' in v)
    nall  = sum(1 for v in plan.values() if 'allergene' in v)
    print(f'{len(plan)} Rezepte zu aendern '
          f'({ntags} mit Tag-Korrektur, {nall} mit Allergen-Ergaenzung)\n')

    zeilen = ['# Korrekturen an den Rezeptdaten', '',
              f'{len(plan)} Rezepte: {ntags} Tag-Korrekturen, {nall} Allergen-Ergaenzungen.',
              'Erzeugt von `tools/korrigiere-rezepte.py`, Befunde aus `tools/pruefe-rezepte.py`.',
              '', '| Rezept | Aenderung | vorher | nachher |', '|---|---|---|---|']

    for rid, e in sorted(plan.items(), key=lambda x: x[1]['name']):
        r = rezepte[rid]
        print(f'  {e["name"]}')
        for w in e['warum']:
            print(f'      {w}')
        if 'allergene' in e:
            vor, nach = r['allergene'] or '—', e['allergene']
        else:
            vor = nach = ''
        alt_tags = {t for t in r['tags']}
        neu_tags = set(e.get('tags', r['tags']))
        weg = sorted(n for n, i in tagid.items() if i in alt_tags - neu_tags)
        teile = []
        if weg:
            teile.append('Tag entfernt: ' + ', '.join(weg))
        if 'allergene' in e:
            teile.append('Allergene ergaenzt')
        zeilen.append(f'| {e["name"]} | {"; ".join(teile)} | '
                      f'{(r["allergene"] or "—") if "allergene" in e else ", ".join(weg)} | '
                      f'{e.get("allergene", "entfernt")} |')

    if not schreiben:
        print('\n(Probelauf - es wurde nichts geschrieben. Mit --schreiben ausfuehren.)')
        return

    print()
    for rid, e in plan.items():
        patch = {}
        if 'tags' in e:
            patch['tags'] = e['tags']
        if 'allergene' in e:
            patch['allergene'] = e['allergene']
        api(f'rezepte/records/{rid}', 'PATCH', patch)
        print(f'  geschrieben: {e["name"]}')

    if logdatei:
        logdatei.write_text('\n'.join(zeilen) + '\n', encoding='utf-8')
        print(f'\nProtokoll: {logdatei.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
