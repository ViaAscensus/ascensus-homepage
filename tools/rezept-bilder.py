#!/usr/bin/env python3
"""Teaserbilder fuer Rezeptseiten ueber den n8n-Workflow erzeugen.

Ruft je Rezept https://n8n.ascensus.fit/webhook/rezept-bild auf und legt drei
Dateien an, genau wie sie die bestehenden Seiten erwarten:

  rezept-<slug>.png      1080x1350  rohe Antwort des Workflows
  rezept-<slug>.jpg      1200x900   Bild auf der Rezeptseite und im Kachel-Grid
  rezept-<slug>-og.png   1200x630   og:image

Der Zuschnitt ist vertikal mittig - so sitzen alle 18 urspruenglichen Bilder.

  python3 tools/rezept-bilder.py              # alle Rezepte ohne Bild
  python3 tools/rezept-bilder.py <slug> ...   # nur diese
  python3 tools/rezept-bilder.py --prompt     # nur zeigen, was gesendet wuerde

Danach tools/build-rezepte.py laufen lassen, damit die Seiten das Bild bekommen.

Der Workflow baut den Prompt aus dem gesendeten Body. Frueher trug der nur name
und zutaten, worauf die Bilder regelmaessig neben dem Rezept lagen: Sauerrahm auf
veganen Gerichten, eine erfundene Reisbeilage neben einem Snack, ein Bierglas.
Deshalb gehen jetzt auch kategorie, tags, portionen und die Schritte mit -
tools/n8n-rezept-bild.json ist der passende Workflow dazu.
"""
import collections, io, json, os, sys, time, urllib.request
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    sys.exit('Pillow fehlt:  pip install Pillow')

ROOT = Path(__file__).resolve().parent.parent
HOOK = 'https://n8n.ascensus.fit/webhook/rezept-bild'
PB   = 'https://pb.ascensus.fit/api/collections'

# Zielformate: (Hoehe, Endung, Speicheroptionen). Die Breite ist immer 1200.
FORMATE = ((900, '.jpg', dict(quality=88, subsampling=0)),
           (630, '-og.png', {}))


def pb(pfad):
    r = urllib.request.Request(f'{PB}/{pfad}')
    if os.environ.get('PB_TOKEN'):
        r.add_header('Authorization', os.environ['PB_TOKEN'])
    with urllib.request.urlopen(r, timeout=60) as resp:
        return json.load(resp)


def alle(coll):
    out, seite = [], 1
    while True:
        d = pb(f'{coll}/records?perPage=500&page={seite}')
        out += d['items']
        if seite >= d['totalPages']:
            break
        seite += 1
    return out


def body_fuer(r, zutaten, schritte, tagname):
    """Was der Workflow braucht, um die Szene richtig zu treffen."""
    return {
        'name':       r['name'],
        'kategorie':  r['kategorie'] or '',
        'portionen':  r['portionen'] or 1,
        'tags':       sorted(tagname),
        # mit Menge, damit die Verhaeltnisse auf dem Teller stimmen
        'zutaten':    [f'{z["menge"]:g} {z["einheit"]} {z["zutat"]}'.strip()
                       if z['menge'] else z['zutat'] for z in zutaten][:8],
        'schritte':   [s['anweisung'] for s in schritte],
    }


def hole_bild(body, versuche=2):
    daten = json.dumps(body).encode()
    for i in range(versuche):
        try:
            r = urllib.request.Request(HOOK, data=daten, method='POST',
                                       headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(r, timeout=180) as resp:
                roh = resp.read()
            im = Image.open(io.BytesIO(roh))
            im.load()
            return roh, im
        except Exception as e:
            if i + 1 == versuche:
                raise
            print(f'      Versuch {i+1} fehlgeschlagen ({e}), noch einer ...')
            time.sleep(5)


def ableiten(im, slug):
    b = im.convert('RGB')
    b = b.resize((1200, round(b.height * 1200 / b.width)), Image.LANCZOS)
    for hoehe, endung, opt in FORMATE:
        y = (b.height - hoehe) // 2          # vertikal mittig, wie die ersten 18
        b.crop((0, y, 1200, y + hoehe)).save(ROOT / f'{slug}{endung}', **opt)


def main():
    nur_prompt = '--prompt' in sys.argv
    gewuenscht = [a for a in sys.argv[1:] if not a.startswith('-')]

    slugmap  = json.load(open(ROOT / 'tools' / 'slug-map.json'))
    rezepte  = {r['id']: r for r in alle('rezepte')}
    tagname  = {t['id']: t['name'] for t in alle('tags')}
    zutaten  = collections.defaultdict(list)
    schritte = collections.defaultdict(list)
    for z in sorted(alle('zutaten'), key=lambda z: z['created']):
        zutaten[z['rezept']].append(z)
    for s in sorted(alle('schritte'), key=lambda s: s['nummer']):
        schritte[s['rezept']].append(s)

    offen = [(rid, s) for rid, s in slugmap.items()
             if (s in gewuenscht) if gewuenscht] or \
            [(rid, s) for rid, s in slugmap.items()
             if not (ROOT / f'{s}.jpg').exists()]
    if not offen:
        print('Alle Rezepte aus slug-map.json haben ein Bild.')
        return

    print(f'{len(offen)} Rezept(e)\n')
    for n, (rid, slug) in enumerate(offen, 1):
        r = rezepte.get(rid)
        if not r:
            print(f'{n:2d}. {slug}: kein PocketBase-Datensatz, uebersprungen')
            continue
        tn = {tagname[t] for t in r['tags'] if t in tagname}
        body = body_fuer(r, zutaten[rid], schritte[rid], tn)

        print(f'{n:2d}. {r["name"]}')
        if nur_prompt:
            print(json.dumps(body, ensure_ascii=False, indent=2))
            print()
            continue

        t0 = time.time()
        roh, im = hole_bild(body)
        (ROOT / f'{slug}.png').write_bytes(roh)
        ableiten(im, slug)
        print(f'      {im.size[0]}x{im.size[1]} in {time.time()-t0:.0f}s  ->  '
              f'{slug}.png / .jpg / -og.png\n')

    if not nur_prompt:
        print('fertig - jetzt tools/build-rezepte.py laufen lassen')


if __name__ == '__main__':
    main()
