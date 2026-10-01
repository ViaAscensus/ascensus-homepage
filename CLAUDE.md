# ascensus.fit

Statische Homepage von ASCENSUS (Ernährungs- und Laufcoaching, Patrick Spengler,
Frankfurt am Main). Reines HTML, CSS und Vanilla-JavaScript im Wurzelverzeichnis —
kein Framework, kein Build-Schritt, kein Paketmanager.

## Deployment

Coolify auf einem Hetzner-Server, Build strategy *Static*, `nginx:alpine`,
Publish directory `/`. Die Quelle ist eine GitHub App, Auto-Deploy ist aktiv:

```
Merge auf main  →  GitHub sendet push  →  Coolify deployt  →  live
```

Es wird nichts gebaut — Coolify liefert die Dateien aus dem Repo direkt aus.
Deshalb müssen **erzeugte HTML-Dateien mit eingecheckt werden**.

### Cache-Header liegen in Coolify, nicht hier

Die nginx-Konfiguration steht in Coolify unter *General → Build pipeline →
Custom Nginx configuration*. **Sie ist nicht versioniert** und taucht in keinem
PR auf; wird die Anwendung je neu angelegt, ist sie weg. Deshalb hier als Kopie:

```nginx
server {
    root /usr/share/nginx/html;

    # Standard fuer alles: nicht blind cachen, sondern per ETag rueckfragen.
    # Der Server antwortet mit 304, es fliessen ein paar hundert Byte statt
    # der ganzen Seite. Gilt damit auch fuer / und fuer URLs ohne Endung.
    add_header Cache-Control "no-cache" always;

    location / {
        root /usr/share/nginx/html;
        index index.html index.htm;
        try_files $uri $uri.html $uri/index.html $uri/index.htm $uri/ =404;
    }

    # Schriften aendern sich nie - volle Dauer
    location ~* \.(woff2|woff|ttf|eot)$ {
        add_header Cache-Control "public, max-age=31536000, immutable" always;
    }

    # Bilder und PDF: eine Woche, aber ohne immutable. Rezeptfotos tragen
    # den Rezeptnamen, ein neu erzeugtes Bild heisst genauso - der Browser
    # muss es also nach einer Weile neu holen koennen.
    location ~* \.(jpg|jpeg|png|gif|webp|svg|ico|pdf)$ {
        add_header Cache-Control "public, max-age=604800" always;
    }

    # CSS und JS: kurz, weil die Dateinamen keinen Hash tragen
    location ~* \.(css|js)$ {
        add_header Cache-Control "public, max-age=3600, must-revalidate" always;
    }

    # Handle 404 errors
    error_page 404 /404.html;
    location = /404.html {
        root /usr/share/nginx/html;
        internal;
    }

    # Handle server errors (50x)
    error_page 500 502 503 504 /50x.html;
    location = /50x.html {
        root /usr/share/nginx/html;
        internal;
    }
}
```

Drei Entscheidungen darin sind nicht beliebig:

- **`no-cache` auf Server-Ebene, nicht je `location`.** In nginx *ersetzt* ein
  `add_header` im Block den geerbten, statt ihn zu ergänzen. Die drei
  Asset-Blöcke überschreiben also gezielt; alles übrige — HTML, `/`, URLs ohne
  Endung — erbt `no-cache`. Eine Regel nur für `\.html$` würde die Startseite
  und endungslose URLs verfehlen, weil die in `location /` landen.
- **Bilder ohne `immutable`.** Rezeptfotos heißen nach dem Rezept
  (`rezept-weiberpasta.jpg`); erzeugt n8n eines neu, trägt es denselben Namen.
  Mit `immutable` fragt der Browser nie wieder nach und zeigt dauerhaft das
  alte Bild.
- **CSS und JS nur eine Stunde.** `ascensus.css` trägt keinen Inhalts-Hash im
  Namen. Bei langer Cache-Dauer sähen Besucher nach einer Designänderung
  monatelang die alte Fassung.

Ohne diese Konfiguration raten Browser die Cache-Dauer von HTML aus dem Alter
der Datei — in der Praxis Stunden bis Tage. Das führt dazu, dass eine frisch
deployte Seite alt aussieht, obwohl der Server längst die neue ausliefert.
Nachprüfen lässt sich der Zustand mit:

```bash
curl -sSI https://ascensus.fit/index.html | grep -i cache-control   # no-cache
curl -sSI https://ascensus.fit/ascensus.css | grep -i cache-control # max-age=3600
```

## Rezeptseiten werden generiert

`rezept-*.html`, das Kachel-Grid in `rezepte.html` und der Rezept-Abschnitt der
`sitemap.xml` stammen aus PocketBase und werden von `tools/build-rezepte.py`
erzeugt.

**Diese Dateien nie von Hand bearbeiten.** Änderungen gehören in PocketBase,
danach:

```bash
python3 tools/build-rezepte.py --check   # zeigt, was sich ändern würde
python3 tools/build-rezepte.py           # schreibt die Seiten
```

Der Lauf ist idempotent. Details und wie ein neues Rezept veröffentlicht wird:
`tools/README.md`.

Von Hand gepflegt werden dagegen: `index.html`, `pakete*.html`, `wissen*.html`,
die Rechtstexte, `anamnese*.html`, `trainingsbuch.html` und die `mitglieder-*.html`.

## PocketBase

`https://pb.ascensus.fit`. Der Zugang läuft über die API-Anmeldedaten der
Umgebung — der Proxy setzt den `Authorization`-Header selbst, es ist kein Login
nötig. PocketBase erwartet den Token **pur**, ohne `Bearer`-Präfix.

Rezeptdaten (Konto `api_clients`, darf lesen, anlegen, ändern und seit dem
30.09.2026 auch löschen):

| Collection | Felder |
|---|---|
| `rezepte` | `name`, `kategorie`, `portionen`, `zeit_zubereitung`, `zeit_gesamt`, `kcal`, `eiweiss`, `kohlenhydrate`, `fett`, `ballaststoffe`, `allergene`, `tags`, `status`, `naehrwerte_quelle` |
| `zutaten` | `rezept`, `zutat`, `menge`, `einheit`, `gruppe`, `naehrwerte_pro_100g` (Format `"90g K / 16g E / 2g F / 454 kcal"`) |
| `schritte` | `rezept`, `nummer`, `anweisung` |
| `tags` | `name`, `typ` (`aus_zutaten` \| `berechnet` \| `bestaetigung`), `aktiv` |

**Falle:** `zutaten.naehrwerte_pro_100g` trägt trotz seines Namens die absoluten
Werte für die eingetragene Menge, nicht Werte je 100 g. Eine Gegenrechnung ist
daher: Summe der Zutatenzeilen geteilt durch `portionen`.

Der Mitgliederbereich nutzt daneben `members`, `invitations`, `quiz_wochen`,
`quiz_fortschritt` und `trainingsbuch_entries` über `pocketbase.umd.js`.

Bilder zu den Rezepten erzeugt ein n8n-Webhook aus denselben PocketBase-Daten.

## Vor dem Veröffentlichen eines Rezepts prüfen

Im September 2026 wurden acht ungeprüfte Datensätze veröffentlicht, deren Fehler
anschließend im HTML landeten. Diese drei Prüfungen fangen das ab:

1. **Der Prüferlauf meldet für dieses Rezept nichts** — und `status` steht auf
   `geprueft`. Der Status allein genügt nicht: zwei Seiten mit fehlender
   Gluten-Angabe trugen ihn bereits. Er sagt aus, dass jemand einen Haken
   gesetzt hat, nicht dass geprüft wurde.
2. `zeit_gesamt` ist größer als 0
3. Tags passen zur Zutatenliste — besonders `Vegan`, `Vegetarisch` und `Glutenfrei`

Alle drei prüft `tools/pruefe-rezepte.py`, dazu Nährwerte gegen die
Zutatensumme, Allergene, Vollständigkeit und Dubletten:

```bash
python3 tools/pruefe-rezepte.py                   # die unveröffentlichten
python3 tools/pruefe-rezepte.py --veroeffentlicht # die Seiten, die online stehen
python3 tools/pruefe-rezepte.py --json            # vollständiger Befund
```

Der letzte Befund liegt in `tools/PRUEFBERICHT-REZEPTE.md`.

Gefundenes korrigiert `tools/korrigiere-rezepte.py` (falsche Diät-Tags, fehlende
Allergene), beide Werkzeuge ohne `--schreiben` nur als Probelauf.

**Entscheidung zu Whey/Molke:** zählt immer gegen `Laktosefrei`, auch als Isolat
— die Datenbank unterscheidet Konzentrat/Isolat nicht. Eine falsch als
laktosefrei markierte Seite trifft einen Kunden mit echter Intoleranz, eine zu
Unrecht entfernte Markierung trifft niemanden. Steht als Regel in
`tools/pruefe-rezepte.py` bei der `milch`-Erkennung.

## Berechnete Tags werden gerechnet, nicht gepflegt

Fünf Tags mit `typ: berechnet` folgen aus den Zahlen und werden von
`tools/berechne-tags.py` gesetzt — von Hand gepflegt lagen sie gegen jede
denkbare Schwelle nur zu 26 bis 63 % richtig:

| Tag | Schwelle |
|---|---|
| High-Protein | Eiweiß ≥ 20 % der kcal (VO (EG) 1924/2006) |
| High-Carb | Kohlenhydrate ≥ 50 % der kcal |
| Low-Carb | Kohlenhydrate ≤ 20 % der kcal |
| Kalorienarm | ≤ 400 kcal je Portion |
| Schnell und einfach | `zeit_gesamt` zwischen 1 und 30 Minuten |

Die Zahlen stehen als `GRENZE` **nur** in `tools/berechne-tags.py`; der Prüfer
liest sie von dort, damit Rechnen und Prüfen nicht auseinanderlaufen.

`Ballaststoffreich` wird **nicht** gerechnet: `ballaststoffe` ist bei den
unveröffentlichten Rezepten durchweg 0 und die Zutatenzeilen führen keine
Ballaststoffe. Solange es keine Datenquelle gibt, bleibt das Tag ungeprüft
stehen und sollte bei neuen Rezepten nicht vergeben werden.

Nach einem Lauf `tools/build-rezepte.py` ausführen — die Tags stehen als Badges
auf den Seiten und im Kachel-Grid.

## Konventionen

- Deutsche Seite: Dezimalkomma, Umlaute ausschreiben. Die DB speichert Rubriken
  und Tags teils ohne Umlaute (`Fruehstueck`), der Generator bildet das ab.
- Jede Seite bindet den Block aus `head-snippet.html` ein: Google Consent Mode,
  Klaro und gtag. Ohne ihn erscheint kein Cookie-Banner.
- Keine Ressourcen von Drittservern einbinden — alles liegt lokal im Repo
  (Inter als woff2, Klaro selbst gehostet).
- Dateinamen der Rezeptseiten stehen in `tools/slug-map.json` und bleiben stabil,
  damit URLs nicht brechen.

## Offene Punkte

**Keine Anzahlen in dieser Datei.** Sie veralten mit jeder Prüfung, und ein
fortgeschriebener Wert ist eine Wette darauf, dass seitdem niemand gearbeitet hat.
Der aktuelle Stand kommt aus `tools/pruefe-rezepte.py`; die bloßen Anzahlen
notfalls direkt:

```bash
pb=https://pb.ascensus.fit/api/collections/rezepte/records
for f in "status='neu'" "status='geprueft'" "zeit_gesamt=0"; do
  printf '%-22s ' "$f"
  curl -sS --get "$pb" --data-urlencode "filter=$f" --data-urlencode perPage=1 \
    --data-urlencode fields=id | python3 -c 'import sys,json;print(json.load(sys.stdin)["totalItems"])'
done
ls rezept-*.html | wc -l   # veroeffentlichte Seiten
```

- **Erledigt (01.10.2026):** Alle Rezepte stehen auf `status: geprueft`, die acht
  im September veröffentlichten Rezepte eingeschlossen — deren Zutaten-Nährwerte
  fehlten seit der Veröffentlichung und wurden über `naehrwerte_bls` nachgetragen.
  `pruefe-rezepte.py` meldet 0 Befunde, sowohl für die unveröffentlichten als auch
  für die veröffentlichten Seiten. Die frühere Dublette der Apfel-Buchweizen-Pancakes
  (`r5ywxnobwwz1n6k`) ist dabei entfernt worden — sie trug als einzige die
  Zutaten-Nährwerte, die dem veröffentlichten Datensatz (`9gh4ubu03pv4st8`) fehlten,
  deshalb erst übertragen, dann gelöscht. **Regel bei künftigen Dubletten:** erst
  die Werte auf den bleibenden Datensatz übertragen, dann löschen — nie umgekehrt,
  sonst sind Daten weg, die nirgends sonst stehen.

  Vor dem Setzen auf `geprueft` wurden die 50 damals noch `status: neu` stehenden
  Rezepte inhaltlich gelesen, nicht nur automatisiert geprüft (Regel 1 verlangt
  mehr als einen bestandenen Check). Dabei kamen sieben konkrete Lücken heraus und
  wurden behoben: zwei fehlende Zutaten, die in der Zubereitung vorkommen, aber nie
  im Zutatenfeld standen (Kurkuma im Kurkuma-Zitrone-Ingwer Shot, Limettensaft im
  Glasnudelsalat mit Tempeh), zwei Rezepte, die Gemüsebrühe verlangen, ohne sie zu
  listen (beide Gnocchi-Pfannen), eine fehlende Maisstärke zum Binden (Asiatische
  Gemüse-Reis-Pfanne), eine Frühlingszwiebel mit `menge = 0` trotz Verwendung im
  Rezept (Nudelsalat) und ein Zubereitungsschritt, der als Fließtext-Rest im
  vorherigen Schritt steckte, statt ein eigener zu sein (Rote Linsen Dal).
  `Ballaststoffreich` ist seitdem für alle
  Rezepte, die das Tag tragen, über `naehrwerte_bls` nachgerechnet und bestätigt —
  für den großen Rest des Bestands ohne das Tag bleibt die Datenlücke bestehen.
- **Kein Fehler:** die Verweise auf `wissen-xxx.html` in den sechs
  `wissen-*.html` stehen sämtlich in einem HTML-Kommentar — ein nie gefüllter
  Vorlagenblock „Das könnte Dich auch interessieren" mit den Platzhaltern
  `Kategorie` und `Titel`. Kein Browser rendert sie, es sind keine toten Links.
  Zu tun wäre höchstens, den Block zu füllen oder zu entfernen.
