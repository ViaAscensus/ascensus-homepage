#!/usr/bin/env python3
"""Füllt die PocketBase-Sammlung `uebungskatalog` mit den deutschen Übungen aus wger.

Das Trainingsbuch (trainingsbuch.html) schlägt im Katalog nach, wenn eine Übung noch keine
Muskelgruppe hat: gleicher Name -> Gruppe wird automatisch gesetzt, ähnlicher Name ->
Vorschlag, sonst die übliche Nachfrage.

Felder der Sammlung (fehlende werden angelegt, vorhandene bleiben unberührt)
    name              Text    deutscher Name der Übung
    name_en           Text    englischer Name (nur zur Orientierung)
    muskelgruppe      Text    unsere Gruppe, z. B. Bizeps (leer, wenn nicht bestimmbar)
    muskeln_primaer   Text    wger-Muskeln, kommagetrennt
    muskeln_sekundaer Text    wger-Muskeln, kommagetrennt
    equipment         Text    Geräte, kommagetrennt
    bild_url          Text    Hauptbild bei wger (Quelle)
    bild              Datei   Kopie des Hauptbilds in PocketBase; die Seite lädt es von dort und nie von wger
    wger_id           Zahl    Kennung bei wger; macht den Lauf wiederholbar

Lesen darf jedes angemeldete Mitglied, schreiben nur der Superuser. Eine bereits gesetzte
Lese-Regel bleibt, wie sie ist.

Muskel-Umrechnung: Der erste Hauptmuskel von wger bestimmt die Gruppe (Tabelle WGER_MUSKEL).
Was wger nicht kennt (Nacken, Unterarme, Adduktoren, Unterer Rücken, Schienbein), erkennt das
Skript am Namen der Übung (Tabelle NAME_REGELN); diese Regeln haben Vorrang.
Übungen ohne Treffer bekommen keine Gruppe und werden im Katalog nicht zugeordnet.
Cardio-Übungen werden übersprungen.

Aufruf
    python3 tools/import-uebungskatalog.py --dry-run           # nur zeigen, nichts schreiben
    python3 tools/import-uebungskatalog.py --dry-run --limit=30
    python3 tools/import-uebungskatalog.py                     # importieren
    python3 tools/import-uebungskatalog.py --ohne-bilder       # Texte importieren, keine Bilder laden
    python3 tools/import-uebungskatalog.py --englisch          # Übungen ohne deutschen Namen mit englischem Namen aufnehmen

Zugang: Superuser (E-Mail und Passwort werden abgefragt, oder PB_TOKEN bzw.
PB_EMAIL/PB_PASSWORD; PB_URL überschreibt die Adresse, WGER_URL die wger-Adresse).
Der Probelauf braucht nur wger, kein Passwort.
"""
import getpass
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

PB = os.environ.get('PB_URL', 'https://pb.ascensus.fit').rstrip('/')
WGER = os.environ.get('WGER_URL', 'https://wger.de').rstrip('/')
NAME = 'uebungskatalog'
STANDARD_EMAIL = 'patrick@ascensus.fit'
LESEN = '@request.auth.id != ""'

FELDER = [
    {'name': 'name', 'type': 'text', 'required': True, 'max': 200},
    {'name': 'name_en', 'type': 'text', 'required': False, 'max': 200},
    {'name': 'muskelgruppe', 'type': 'text', 'required': False, 'max': 40},
    {'name': 'muskeln_primaer', 'type': 'text', 'required': False, 'max': 400},
    {'name': 'muskeln_sekundaer', 'type': 'text', 'required': False, 'max': 400},
    {'name': 'equipment', 'type': 'text', 'required': False, 'max': 400},
    {'name': 'bild_url', 'type': 'text', 'required': False, 'max': 600},
    {'name': 'wger_id', 'type': 'number', 'required': False, 'onlyInt': True},
    {'name': 'bild', 'type': 'file', 'required': False, 'maxSelect': 1, 'maxSize': 2000000,
     'mimeTypes': ['image/jpeg', 'image/png', 'image/webp', 'image/gif'], 'thumbs': ['320x320']},
]
MAX_BILD = 2000000

# wger-Muskel (Kennung -> unsere Gruppe). Die Kennungen sind bei wger fest vergeben;
# zusätzlich wird der englische Name geprüft, falls sich eine Kennung ändert.
WGER_MUSKEL = {
    1: 'Bizeps',        # Biceps brachii
    2: 'Schultern',     # Anterior deltoid
    3: 'Brust',         # Serratus anterior
    4: 'Brust',         # Pectoralis major
    5: 'Trizeps',       # Triceps brachii
    6: 'Bauch',         # Rectus abdominis
    7: 'Waden',         # Gastrocnemius
    8: 'Gesäß',         # Gluteus maximus
    9: 'Trapez',        # Trapezius
    10: 'Quadrizeps',   # Quadriceps femoris
    11: 'Beinbeuger',   # Biceps femoris
    12: 'Rücken',       # Latissimus dorsi
    13: 'Bizeps',       # Brachialis
    14: 'Obliques',     # Obliquus externus abdominis
    15: 'Waden',        # Soleus
}
WGER_MUSKEL_EN = {
    'biceps brachii': 'Bizeps', 'brachialis': 'Bizeps', 'anterior deltoid': 'Schultern',
    'serratus anterior': 'Brust', 'pectoralis major': 'Brust', 'triceps brachii': 'Trizeps',
    'rectus abdominis': 'Bauch', 'gastrocnemius': 'Waden', 'soleus': 'Waden',
    'gluteus maximus': 'Gesäß', 'trapezius': 'Trapez', 'quadriceps femoris': 'Quadrizeps',
    'biceps femoris': 'Beinbeuger', 'latissimus dorsi': 'Rücken',
    'obliquus externus abdominis': 'Obliques',
}

# Namensregeln, die vor der Muskeltabelle gelten (gleiche Begriffe wie in trainingsbuch.html)
NAME_REGELN = [
    (('kreuzheben', 'rückenstrecker', 'rueckenstrecker', 'hyperextension', 'deadlift', 'good morning',
      'guten morgen', 'unterer rücken', 'lower back', 'back extension'), 'Unterer Rücken'),
    (('adduktor', 'adductor', 'innere oberschenkel'), 'Adduktoren'),
    (('schienbein', 'tibialis', 'shin'), 'Schienbein'),
    (('unterarm', 'forearm', 'handgelenk', 'wrist curl', 'reverse curl'), 'Unterarme'),
    (('neck curl', 'nackenmuskulatur', 'nackenstrecker', 'neck extension'), 'Nacken'),
    (('oblique', 'russian twist', 'seitliche bauch', 'seitstütz', 'side plank'), 'Obliques'),
    (('beinheb', 'leg raise', 'crunch', 'sit-up', 'situp', 'plank', 'unterarmstütz'), 'Bauch'),
]


class Fehler(Exception):
    pass


token = os.environ.get('PB_TOKEN')


def http(url, methode='GET', body=None, kopf=None, versuche=3):
    daten = json.dumps(body).encode() if body is not None else None
    for versuch in range(versuche):
        r = urllib.request.Request(url, data=daten, method=methode)
        r.add_header('Accept', 'application/json')
        r.add_header('User-Agent', 'ascensus-katalog-import/1.0')
        if daten is not None:
            r.add_header('Content-Type', 'application/json')
        for k, v in (kopf or {}).items():
            r.add_header(k, v)
        try:
            with urllib.request.urlopen(r, timeout=60) as resp:
                inhalt = resp.read()
                return json.loads(inhalt) if inhalt else {}
        except urllib.error.HTTPError as e:
            text = e.read().decode('utf-8', 'replace')[:300]
            if e.code in (429, 500, 502, 503, 504) and versuch < versuche - 1:
                time.sleep(2 * (versuch + 1))
                continue
            raise Fehler(f'HTTP {e.code} bei {url}: {text}') from None
        except urllib.error.URLError as e:
            if versuch < versuche - 1:
                time.sleep(2 * (versuch + 1))
                continue
            raise Fehler(f'Keine Verbindung zu {url}: {e.reason}') from None


def pb(pfad, methode='GET', body=None):
    kopf = {'Authorization': token} if token else {}
    return http(f'{PB}/{pfad}', methode, body, kopf)


def frage(text, verdeckt=False):
    try:
        return (getpass.getpass(text) if verdeckt else input(text)).strip()
    except EOFError:
        return ''


def anmelden():
    global token
    if token:
        return
    email = os.environ.get('PB_EMAIL') or frage(f'E-Mail [{STANDARD_EMAIL}]: ') or STANDARD_EMAIL
    passwort = os.environ.get('PB_PASSWORD') or frage(f'Passwort für {email}: ', verdeckt=True)
    if not passwort:
        sys.exit('Ohne Passwort kann nichts geschrieben werden.')
    token = pb('api/collections/_superusers/auth-with-password', 'POST',
               {'identity': email, 'password': passwort})['token']
    print(f'Angemeldet als {email}')


def sammlung_einrichten():
    """Legt Sammlung und fehlende Felder an, setzt die Lese-Regel falls noch keine gesetzt ist."""
    try:
        s = pb(f'api/collections/{NAME}')
    except Fehler as e:
        if 'HTTP 404' not in str(e):
            raise
        print(f'+ Sammlung {NAME} wird angelegt')
        pb('api/collections', 'POST', {
            'name': NAME, 'type': 'base', 'fields': FELDER,
            'indexes': [f'CREATE UNIQUE INDEX `idx_{NAME}_wger` ON `{NAME}` (`wger_id`)'],
            'listRule': LESEN, 'viewRule': LESEN,
        })
        return {f['name'] for f in FELDER}
    vorhanden = {f['name'].lower() for f in s.get('fields', [])}
    print('Vorhandene Felder: ' + ', '.join(sorted(vorhanden)))
    for regel in ('listRule', 'viewRule'):
        if s.get(regel) is None:
            print(f'+ {regel} wird gesetzt (angemeldete Mitglieder dürfen lesen)')
            pb(f'api/collections/{s["id"]}', 'PATCH', {regel: LESEN})
    # Fehlende Felder einzeln ergänzen: ein Fehler bei einem Feld stoppt die anderen nicht.
    for f in FELDER:
        if f['name'].lower() in vorhanden:
            continue
        aktuell = pb(f'api/collections/{s["id"]}')
        if f['name'].lower() in {x['name'].lower() for x in aktuell.get('fields', [])}:
            continue
        try:
            pb(f'api/collections/{s["id"]}', 'PATCH', {'fields': aktuell['fields'] + [f]})
            print(f'+ Feld {f["name"]} ergänzt')
        except Fehler as e:
            print(f'! Feld {f["name"]} konnte nicht ergänzt werden, wird beim Import ausgelassen: {str(e)[:160]}')
    final = pb(f'api/collections/{s["id"]}')
    return {x['name'] for x in final.get('fields', [])}  # echte Schreibweise der Felder


def wger_alle(pfad, **params):
    """Läuft über alle Seiten einer wger-Liste."""
    params.setdefault('limit', 100)
    url = f'{WGER}/api/v2/{pfad}/?' + urllib.parse.urlencode(params)
    while url:
        seite = http(url)
        for eintrag in seite.get('results', []):
            yield eintrag
        url = seite.get('next')
        if url and url.startswith('http://') and WGER.startswith('https://'):
            url = 'https://' + url[len('http://'):]


def sprache_id(kuerzel):
    for s in wger_alle('language'):
        if s.get('short_name') == kuerzel:
            return s['id']
    raise Fehler(f'Sprache {kuerzel} nicht bei wger gefunden')


def muskelname(m):
    return (m.get('name_en') or m.get('name') or '').strip()


def gruppe_bestimmen(name, muskeln):
    n = name.lower() + ' '
    for woerter, gruppe in NAME_REGELN:
        if any(w in n for w in woerter):
            return gruppe
    for m in muskeln:
        g = WGER_MUSKEL.get(m.get('id')) or WGER_MUSKEL_EN.get(muskelname(m).lower())
        if g:
            return g
    return ''


def bild(info):
    bilder = info.get('images') or []
    haupt = next((b for b in bilder if b.get('is_main')), bilder[0] if bilder else None)
    return (haupt or {}).get('image') or ''


def eintrag_bauen(info, de_id, englisch):
    uebersetzungen = info.get('translations') or []
    de = next((t for t in uebersetzungen if t.get('language') == de_id and (t.get('name') or '').strip()), None)
    en = next((t for t in uebersetzungen if t.get('language') != de_id and (t.get('name') or '').strip()
               and t.get('language') == 2), None)
    if not de and not (englisch and en):
        return None
    kat = (info.get('category') or {}).get('name', '')
    if kat.lower() == 'cardio':
        return None
    name = (de or en)['name'].strip()
    primaer = info.get('muscles') or []
    sekundaer = info.get('muscles_secondary') or []
    return {
        'name': name,
        'name_en': (en['name'].strip() if en else ''),
        'muskelgruppe': gruppe_bestimmen(name, primaer),
        'muskeln_primaer': ', '.join(muskelname(m) for m in primaer),
        'muskeln_sekundaer': ', '.join(muskelname(m) for m in sekundaer),
        'equipment': ', '.join((e.get('name') or '').strip() for e in (info.get('equipment') or [])),
        'bild_url': bild(info),
        'wger_id': info['id'],
    }


def bild_laden(url):
    """Lädt das Bild von wger; gibt (Bytes, Dateiname, Typ) zurück oder None."""
    try:
        r = urllib.request.Request(url, headers={'User-Agent': 'ascensus-katalog-import/1.0'})
        with urllib.request.urlopen(r, timeout=60) as resp:
            typ = (resp.headers.get('Content-Type') or '').split(';')[0].strip().lower()
            daten = resp.read(MAX_BILD + 1)
    except (urllib.error.URLError, OSError):
        return None
    if typ not in ('image/jpeg', 'image/png', 'image/webp', 'image/gif') or not daten or len(daten) > MAX_BILD:
        return None
    endung = {'image/jpeg': 'jpg', 'image/png': 'png', 'image/webp': 'webp', 'image/gif': 'gif'}[typ]
    return daten, f'uebung.{endung}', typ


def bild_hochladen(satz_id, feldname, daten, dateiname, typ):
    grenze = '----ascensus' + str(int(time.time() * 1000))
    kopf = (f'--{grenze}\r\nContent-Disposition: form-data; name="{feldname}"; filename="{dateiname}"\r\n'
            f'Content-Type: {typ}\r\n\r\n').encode()
    body = kopf + daten + f'\r\n--{grenze}--\r\n'.encode()
    for versuch in range(3):
        r = urllib.request.Request(f'{PB}/api/collections/{NAME}/records/{satz_id}', data=body, method='PATCH')
        r.add_header('Content-Type', f'multipart/form-data; boundary={grenze}')
        r.add_header('Authorization', token)
        try:
            with urllib.request.urlopen(r, timeout=120) as resp:
                return json.loads(resp.read() or b'{}')
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and versuch < 2:
                time.sleep(2 * (versuch + 1))
                continue
            raise Fehler(f'Bild-Upload fehlgeschlagen (HTTP {e.code}): {e.read().decode("utf-8", "replace")[:200]}') from None


def main():
    args = sys.argv[1:]
    trocken = '--dry-run' in args
    englisch = '--englisch' in args
    bilder = '--ohne-bilder' not in args
    limit = next((int(a.split('=', 1)[1]) for a in args if a.startswith('--limit=')), None)
    print(('PROBELAUF (nichts wird geschrieben)' if trocken else 'IMPORT') + f' · wger: {WGER} · PocketBase: {PB}')

    de_id = sprache_id('de')
    print(f'Deutsch hat bei wger die Kennung {de_id}')

    eintraege, uebersprungen, gesehen = [], 0, 0
    for info in wger_alle('exerciseinfo'):
        gesehen += 1
        e = eintrag_bauen(info, de_id, englisch)
        if e is None:
            uebersprungen += 1
        else:
            eintraege.append(e)
        if limit and len(eintraege) >= limit:
            break
        if gesehen % 200 == 0:
            print(f'  ... {gesehen} bei wger gelesen, {len(eintraege)} übernommen')
    mit = sum(1 for e in eintraege if e['muskelgruppe'])
    print(f'{gesehen} Übungen bei wger gelesen, {len(eintraege)} übernommen '
          f'({mit} mit Muskelgruppe, {len(eintraege) - mit} ohne), {uebersprungen} übersprungen '
          f'(kein deutscher Name oder Cardio).')

    verteilung = {}
    for e in eintraege:
        verteilung[e['muskelgruppe'] or '(ohne)'] = verteilung.get(e['muskelgruppe'] or '(ohne)', 0) + 1
    print('Verteilung: ' + ', '.join(f'{k} {v}' for k, v in sorted(verteilung.items(), key=lambda x: -x[1])))
    for e in eintraege[:8]:
        print(f'  · {e["name"]} -> {e["muskelgruppe"] or "(ohne)"}  [{e["muskeln_primaer"]}]')
    if trocken:
        print('Probelauf beendet, nichts geschrieben. Ohne --dry-run importieren.')
        return

    anmelden()
    felder = sammlung_einrichten()
    echt = {n.lower(): n for n in felder}
    eintraege = [{echt[k.lower()]: v for k, v in e.items() if k.lower() in echt} for e in eintraege]
    vorhanden = {}
    for r in _pb_alle(NAME):
        vorhanden[r.get('wger_id')] = r
    echt_bild = echt.get('bild')
    neu = geaendert = gleich = bild_neu = bild_fehlt = 0
    for i, e in enumerate(eintraege, 1):
        alt = vorhanden.get(e['wger_id'])
        if alt is None:
            satz = pb(f'api/collections/{NAME}/records', 'POST', e)
            satz_id = satz['id']
            hat_bild = False
            neu += 1
        else:
            satz_id = alt['id']
            hat_bild = bool(echt_bild and alt.get(echt_bild))
            if any(alt.get(k) != v for k, v in e.items()):
                pb(f'api/collections/{NAME}/records/{satz_id}', 'PATCH', e)
                geaendert += 1
            else:
                gleich += 1
        quelle = e.get(echt.get('bild_url', 'bild_url'))
        if bilder and echt_bild and quelle and not hat_bild:
            geladen = bild_laden(quelle)
            if geladen:
                bild_hochladen(satz_id, echt_bild, *geladen)
                bild_neu += 1
            else:
                bild_fehlt += 1
        if i % 100 == 0:
            print(f'  ... {i}/{len(eintraege)} verarbeitet')
    print(f'Fertig: {neu} neu, {geaendert} aktualisiert, {gleich} unverändert.')
    if bilder:
        print(f'Bilder: {bild_neu} hochgeladen, {bild_fehlt} nicht ladbar (fehlend, zu groß oder kein Bild).')


def _pb_alle(sammlung):
    seite = 1
    while True:
        antwort = pb(f'api/collections/{sammlung}/records?perPage=200&page={seite}')
        for r in antwort.get('items', []):
            yield r
        if seite >= antwort.get('totalPages', 1):
            return
        seite += 1


if __name__ == '__main__':
    try:
        main()
    except Fehler as e:
        sys.exit(f'Fehler: {e}')
    except KeyboardInterrupt:
        sys.exit('Abgebrochen.')
