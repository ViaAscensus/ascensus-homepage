# Prüfbericht: 478 unveröffentlichte Rezepte

Stand 01.10.2026 · Quelle `pb.ascensus.fit` · geprüft wurden alle 506 `rezepte`-Datensätze
abzüglich der 28 in `tools/slug-map.json`. Grundlage ist der aktuelle Code-Stand von
`tools/pruefe-rezepte.py` inklusive der heutigen Atwater-Erweiterung (Ballaststoffe
2 kcal/g, Fruchtsäuren 3 kcal/g nach Anhang XIV VO (EU) 1169/2011).

## Was sich seit dem letzten Bericht (28.09.2026) geändert hat

Der letzte Bericht fand bei **497** unveröffentlichten Rezepten vier große Fehlerklassen:
40 Tag-Widersprüche (Laktosefrei/Vegan/Glutenfrei/EggFree gegen die Zutatenliste), 90 fehlende
Allergenangaben, eine bei allen 497 leere `kategorie` und 135–29 Tag-Schwellen-Abweichungen
bei den berechneten Tags. **Alle davon sind inzwischen behoben** — vermutlich über
`korrigiere-rezepte.py`, `setze-rubriken.py` und `berechne-tags.py`, aber außerhalb dieser
Sitzung, ich habe das nicht selbst gemacht. Stichproben bestätigen es: *Fitness-Plätzchen*
trägt jetzt korrekt „Gluten" im Allergenfeld, `kategorie` ist bei keinem der 506 Datensätze
mehr leer.

In der heutigen Sitzung kamen dazu:

- 7 Datensätze gelöscht (5 Testrezepte ohne Zubereitung, 2 mit in sich widersprüchlichen
  Zutatendaten — menge = 0 bei gleichzeitig eingetragenem Nährwert).
- Für 16 veröffentlichte Rezepte, deren Zutaten-Nährwerte seit der Veröffentlichung fehlten,
  die Werte über `naehrwerte_bls` nachgetragen und Tags/Status korrigiert.
- Die Atwater-Gegenprobe in `pruefe-rezepte.py` um Ballaststoffe und Fruchtsäuren erweitert,
  weil beides vorher ballaststoff- bzw. zitruslastige Rezepte fälschlich als Widerspruch
  gemeldet hat.

Damit ist der Bestand heute in einem anderen Zustand als am 28.09. — dieser Bericht ersetzt
den alten vollständig, nicht nur in den Zahlen.

## Aktueller Befund

| Fehlerklasse | Anzahl | Wirkung |
|---|---|---|
| Ballaststoffreich ohne Datenbasis | **44** | Tag nicht verifizierbar |
| Zutatenzeile: Makros ergeben mehr kcal als eingetragen | **2** | Einzelwert prüfen |
| Alles andere (Tags, Allergene, Vollständigkeit, Rezept-Nährwerte, Dubletten) | **0** | — |

Das sind insgesamt zwei offene Punkte, beide bereits aus früheren Ständen bekannt und beide
strukturell bedingt, nicht neu entstanden.

### Ballaststoffreich ohne Datenbasis — 44

Diese 44 Rezepte tragen das Tag „Ballaststoffreich", aber `ballaststoffe` steht bei allen
unveröffentlichten Rezepten auf 0 und die Zutatenzeilen führen ebenfalls keine Ballaststoffe
— eine Gegenrechnung ist nicht möglich. Das Tag ist damit weder bestätigt noch widerlegt,
nur nicht prüfbar. `tools/berechne-tags.py` lässt es deshalb bewusst unberührt.

<details><summary>Alle 44 Rezepte</summary>

| Rezept |
|---|
| Asia-Bowl mit Hähnchen |
| Asiatische Gemüse-Pfanne mit Hähnchen |
| Asiatische Gemüse-Reis-Pfanne mit Hähnchen |
| Asiatisches Gemüse mit Tofu-Streifen |
| Beerige Baked Oats |
| Beerige Overnight Oats |
| Blattsalat mit Süßkartoffel |
| Bowl mit gegrillten Garnelen |
| Brokkoli-Mandel-Bowl mit Zitronen-Dressing |
| Buchweizen Spaghetti mit Gemüse und Rührei |
| Buchweizen-Linsen Pasta mit Gemüse |
| Buchweizen-Spaghetti-Paprika Pfanne mit Ei |
| Bunter Quinoa-Salat mit Schafskäse |
| Bunter Raddichio Salat |
| Carrot Cake Baked Oats |
| Cheesecake Overnight Oats mit körnigem Frischkäse |
| Cremige Linsen-Pasta - Vegan |
| Cremige Pasta mit Lauch und Tomate |
| Cremige Pasta mit Lauch und Tomate - Vegan |
| Gebratene Hähnchenbrust mit griechischem Salat |
| Gelbes Curry |
| Gemüse-Linsen-Kokos Pfanne |
| Gemüse-Quinoa-One Pot mit Kalbsleber |
| Gemüse-Sesam-Pfanne mit Tofu |
| Glasnudelsalat mit Tempeh |
| Gnocchi-Pfanne mit Lachs und Tomate |
| Gnocchi-Pfanne mit Linsenbratlingen |
| Green Smoothie-Bowl |
| Kichererbsen-Curry |
| Kichererbsen-Dal mit Hirse |
| Kichererbsen-Paprika Pfanne mit Kartoffelpüree |
| Kichererbsen-Paprika-Garnelen Pfanne mit Kartoffelpüree |
| Kokos-Chia-Pudding |
| Linsenragout mit Zucchini und Tofu |
| Nudelsalat |
| Pancakes - Glutenfrei |
| Reis-Süßkartoffel-Pfanne mit Tofu |
| Rote Linsen Dal |
| Schoko-Kokos Porridge |
| Schoko-Kokos Porridge (proteinreicher) |
| Schoko-Kokos Porridge (proteinreicher) - Vegan |
| Süßer Karotte-Zucchini Porridge |
| Very Berry Smoothie Bowl |
| Winterliche Bowl mit Kürbis |

</details>

**Lösung liegt außerhalb dieses Prüfers**: Ballaststoffwerte müssten je Zutat in PocketBase
nachgetragen werden (z. B. aus `naehrwerte_bls`, Feld `FIBT`, wie es heute für die 4 Getränke
unter D unten gemacht wurde). Das wäre eine eigene, größere Aktion über alle Zutaten hinweg,
nicht nur diese 44 Rezepte.

### Zutatenzeile: Makros ergeben mehr kcal als eingetragen — 2

Geprüft wird nur der Überschuss: ein Minus erklären Ballaststoffe und Zuckeralkohole
(Erythrit 0 kcal/g, Xylit 2,4 statt 4 — beide von der Prüfung ausgenommen), ein Plus nicht.
Beide verbliebenen Treffer betreffen dasselbe Lebensmittel:

| Rezept | Befund |
|---|---|
| Grüner Spargel mit Hähnchen und Curry | Grüner Spargel: 44 kcal, Makros ergeben 64 kcal (+45 %) |
| Quinoasalat mit grünem Spargel, Kichererbsen und Walnüssen | Grüner Spargel: 33 kcal, Makros ergeben 47 kcal (+42 %) |

Grüner Spargel hat real rund 20 kcal/100 g — die eingetragenen Makros (vermutlich mit weißem
Spargel oder einer falschen Mengenbasis verwechselt) passen nicht dazu. Unverändert seit dem
letzten Bericht, nicht Teil der heutigen Arbeit.

## Veröffentlichte Seiten: 28 von 28 sauber

`tools/pruefe-rezepte.py --veroeffentlicht` meldet **0 Befunde** — Tags, Allergene,
Vollständigkeit und (soweit die Zutaten-Nährwerte vorliegen) die Nährwert-Gegenrechnung
stimmen bei allen 28 Seiten. Das schließt die 16 Rezepte ein, deren Zutaten-Nährwerte heute
nachgetragen wurden.

## Was das für die Veröffentlichung heißt

Der Bestand ist strukturell in einem guten Zustand: keine Tag-Widersprüche, keine fehlenden
Allergene, keine leeren Rubriken, keine Dubletten, keine Rezepte ohne Zutaten/Schritte/Zeit.
Was zwischen `status: neu` (50 Datensätze) und der Veröffentlichung steht, ist damit im
Wesentlichen nur noch die inhaltliche Prüfung selbst (Regel 1 aus `CLAUDE.md`) — nicht mehr
eine Liste bekannter Datenfehler, die vorher abgearbeitet werden müsste.

Offen bleiben die beiden Punkte oben, beide nicht kurzfristig lösbar:

1. **Ballaststoffreich bei 44 Rezepten** bleibt unprüfbar, bis es eine Datenquelle für
   Ballaststoffe je Zutat gibt.
2. **Grüner Spargel** in 2 Rezepten hat eine unplausible Nährwertzeile — betrifft nur die
   beiden genannten Rezepte, kein systematisches Problem.

Ich habe für diesen Bericht nichts an den Daten verändert — nur gelesen und ausgewertet.
