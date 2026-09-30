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

- **Der Großteil der Rezepte ist inhaltlich ungeprüft** (`status: neu`). Bei ihnen
  sind die Zutaten-Nährwerte vollständig hinterlegt, eine Gegenrechnung ist also
  möglich. Bei den veröffentlichten fehlen sie — deren Werte wurden geschätzt und
  wurden korrigiert.
- Einige Rezepte haben `zeit_gesamt = 0`, einige keine Schritte, einige
  `menge = 0` bei kalorienrelevanten Zutaten. Der Prüfer nennt sie; sie sind
  bis zum Nachtragen nicht veröffentlichbar.
- **Erledigt:** Die Dublette der Apfel-Buchweizen-Pancakes (`r5ywxnobwwz1n6k`)
  ist entfernt. Sie trug als einzige die Zutaten-Nährwerte, die dem
  veröffentlichten Datensatz (`9gh4ubu03pv4st8`) fehlten — deshalb erst
  übertragen, dann gelöscht. Dabei kam ein Fehler auf der Live-Seite heraus:
  Die Zutatensumme ergibt 55 g Kohlenhydrat, hinterlegt waren 60 — exakt an
  der High-Carb-Schwelle. Mit dem korrigierten Wert liegt das Rezept bei 46 %,
  das Tag ist weg. **Regel bei künftigen Dubletten:** erst die Werte auf den
  bleibenden Datensatz übertragen, dann löschen — nie umgekehrt, sonst sind
  Daten weg, die nirgends sonst stehen.
- `Ballaststoffreich` ist mangels `ballaststoffe`-Werten nicht prüfbar, siehe oben.
- **Geklärt:** es gibt mehr Rezeptseiten als Datensätze auf `status: geprueft`,
  weil die acht im September veröffentlichten Rezepte den Status nie bekommen
  haben. Regel 1 gilt also unverändert, sie wurde einmal verletzt und die
  Betroffenen stehen noch so da. `pruefe-rezepte.py` ersetzt den Status nicht —
  es prüft nur die *unveröffentlichten* Rezepte und sieht diese acht gar nicht.
  Die Differenz findet sich mit:

  ```bash
  python3 -c "import json;print(len(json.load(open('tools/slug-map.json'))))"
  # dagegen die Anzahl auf status=geprueft, siehe Schnipsel oben
  ```

  Offen bleibt damit: **diese acht Seiten sind nie geprüft worden.** Ihre
  Zutaten-Nährwerte fehlen, eine Gegenrechnung ist bei ihnen nicht möglich —
  Tags, Allergene und Vollständigkeit ließen sich aber prüfen.
- **Kein Fehler:** die Verweise auf `wissen-xxx.html` in den sechs
  `wissen-*.html` stehen sämtlich in einem HTML-Kommentar — ein nie gefüllter
  Vorlagenblock „Das könnte Dich auch interessieren" mit den Platzhaltern
  `Kategorie` und `Titel`. Kein Browser rendert sie, es sind keine toten Links.
  Zu tun wäre höchstens, den Block zu füllen oder zu entfernen.
