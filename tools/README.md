# Rezeptseiten erzeugen

Die Rezeptseiten werden **nicht von Hand bearbeitet**. Einzige Quelle der Wahrheit
ist PocketBase (`pb.ascensus.fit`). Wer eine Zutat, eine Zeit oder einen Nährwert
ändern will, ändert das dort und baut anschließend neu.

## Bauen

```bash
python3 tools/build-rezepte.py --check   # zeigt nur, was sich ändern würde
python3 tools/build-rezepte.py           # schreibt die Seiten
```

Erzeugt werden:

* `rezept-*.html` – eine Seite je Eintrag in `tools/slug-map.json`
* `rezept-bechamelsauce.html`, `rezept-tomaten-gemuese-sauce.html` – aus
  `tools/grundrezepte.json` (diese beiden haben keinen PocketBase-Datensatz)
* das Kachel-Grid in `rezepte.html`
* der Rezept-Abschnitt in `sitemap.xml`

Der Lauf ist idempotent: zweimal hintereinander ausgeführt ändert sich nichts.

## Zugang

Der Generator liest die PocketBase-API. Entweder ist ein Proxy vorgeschaltet, der
den `Authorization`-Header setzt, oder ein Token steht in der Umgebung:

```bash
PB_TOKEN=<token> python3 tools/build-rezepte.py
```

Das Token stammt aus der Collection `api_clients` (Datensatz `claude-rezepte@ascensus.fit`),
erzeugt über *Impersonate* in der PocketBase-Oberfläche. PocketBase erwartet den Token
**pur** im Header, ohne `Bearer`-Präfix.

## Dateien

| Datei | Zweck |
|---|---|
| `build-rezepte.py` | der Generator |
| `rezept-template.html` | Seitengerüst mit `{{PLATZHALTER}}` |
| `slug-map.json` | PocketBase-ID → Dateiname. **Nicht ändern**, sonst brechen URLs. |
| `grundrezepte.json` | die beiden Saucen ohne DB-Datensatz |
| `reihenfolge.json` | Reihenfolge der Kacheln auf `rezepte.html` |

## Ein neues Rezept veröffentlichen

1. In PocketBase prüfen: `status` auf `geprueft`, `zeit_gesamt` > 0, Tags passen
   zur Zutatenliste (besonders `Vegan` / `Vegetarisch` / `Glutenfrei`).
2. Foto als `rezept-<slug>.jpg` (1200×900) und `rezept-<slug>-og.png` ablegen.
   Fehlt das Foto, wird die Seite ohne Bild gebaut.
3. ID und Slug in `slug-map.json` eintragen, Slug in `reihenfolge.json` ergänzen.
4. `python3 tools/build-rezepte.py` ausführen und das Ergebnis committen.
