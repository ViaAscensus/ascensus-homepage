# Prüfbericht: 478 unveröffentlichte Rezepte

Stand 01.10.2026 (aktualisiert) · Quelle `pb.ascensus.fit` · geprüft wurden alle 506
`rezepte`-Datensätze abzüglich der 28 in `tools/slug-map.json`. Grundlage ist der aktuelle
Code-Stand von `tools/pruefe-rezepte.py` inklusive der heutigen Atwater-Erweiterung
(Ballaststoffe 2 kcal/g, Fruchtsäuren 3 kcal/g nach Anhang XIV VO (EU) 1169/2011).

**Nachträge vom selben Tag:** Die 44 Rezepte unter „Ballaststoffreich ohne Datenbasis" (siehe
vorherige Fassung dieses Berichts) sind erledigt — Ballaststoffwerte je Zutat aus
`naehrwerte_bls` nachgerechnet und ins Rezept geschrieben. Bei allen 44 bestätigt sich das
Tag (durchweg deutlich über der 5-g-Schwelle, 7,4 bis 35,7 g/Portion), keines musste entfernt
werden. Danach auch der Grüner-Spargel-Befund korrigiert (siehe unten) — **der Bestand steht
damit bei 0 Befunden.**

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

**0 von 478 unveröffentlichten Rezepten haben noch einen Befund.** Tags, Allergene,
Vollständigkeit, Rezept-Nährwerte, Ballaststoffreich, Dubletten und die
Zutaten-Plausibilität (Atwater) sind durchweg sauber.

### Ballaststoffreich — erledigt (vormals 44 ohne Datenbasis)

Die 44 Rezepte mit dem Tag „Ballaststoffreich" hatten bis heute `ballaststoffe = 0` und
keine Ballaststoffwerte in den Zutatenzeilen — nicht prüfbar. Nachgerechnet aus
`naehrwerte_bls` (Feld `FIBT`, je Zutat mit der eingetragenen Menge multipliziert, durch
Portionen geteilt) bestätigt sich das Tag bei **allen 44** — niedrigster Wert 7,4 g/Portion,
höchster 35,7 g/Portion, alle deutlich über der 5-g-Schwelle. Kein einziges musste korrigiert
werden.

<details><summary>Alle 44 Rezepte mit nachgerechnetem Wert</summary>

| Rezept | Ballaststoffe/Portion |
|---|---|
| Asia-Bowl mit Hähnchen | 10,9 g |
| Asiatische Gemüse-Pfanne mit Hähnchen | 12,3 g |
| Asiatische Gemüse-Reis-Pfanne mit Hähnchen | 9,5 g |
| Asiatisches Gemüse mit Tofu-Streifen | 11,0 g |
| Beerige Baked Oats | 11,9 g |
| Beerige Overnight Oats | 16,3 g |
| Blattsalat mit Süßkartoffel | 10,6 g |
| Bowl mit gegrillten Garnelen | 24,8 g |
| Brokkoli-Mandel-Bowl mit Zitronen-Dressing | 12,6 g |
| Buchweizen Spaghetti mit Gemüse und Rührei | 14,8 g |
| Buchweizen-Linsen Pasta mit Gemüse | 21,0 g |
| Buchweizen-Spaghetti-Paprika Pfanne mit Ei | 10,9 g |
| Bunter Quinoa-Salat mit Schafskäse | 7,4 g |
| Bunter Raddichio Salat | 11,2 g |
| Carrot Cake Baked Oats | 10,2 g |
| Cheesecake Overnight Oats mit körnigem Frischkäse | 14,6 g |
| Cremige Linsen-Pasta - Vegan | 15,5 g |
| Cremige Pasta mit Lauch und Tomate | 10,1 g |
| Cremige Pasta mit Lauch und Tomate - Vegan | 12,8 g |
| Gebratene Hähnchenbrust mit griechischem Salat | 11,8 g |
| Gelbes Curry | 13,0 g |
| Gemüse-Linsen-Kokos Pfanne | 20,8 g |
| Gemüse-Quinoa-One Pot mit Kalbsleber | 12,8 g |
| Gemüse-Sesam-Pfanne mit Tofu | 13,8 g |
| Glasnudelsalat mit Tempeh | 16,0 g |
| Gnocchi-Pfanne mit Lachs und Tomate | 10,9 g |
| Gnocchi-Pfanne mit Linsenbratlingen | 10,2 g |
| Green Smoothie-Bowl | 15,9 g |
| Kichererbsen-Curry | 27,1 g |
| Kichererbsen-Dal mit Hirse | 22,1 g |
| Kichererbsen-Paprika Pfanne mit Kartoffelpüree | 35,7 g |
| Kichererbsen-Paprika-Garnelen Pfanne mit Kartoffelpüree | 26,2 g |
| Kokos-Chia-Pudding | 11,0 g |
| Linsenragout mit Zucchini und Tofu | 13,0 g |
| Nudelsalat | 21,4 g |
| Pancakes - Glutenfrei | 10,0 g |
| Reis-Süßkartoffel-Pfanne mit Tofu | 12,4 g |
| Rote Linsen Dal | 25,8 g |
| Schoko-Kokos Porridge | 24,0 g |
| Schoko-Kokos Porridge (proteinreicher) | 18,0 g |
| Schoko-Kokos Porridge (proteinreicher) - Vegan | 18,5 g |
| Süßer Karotte-Zucchini Porridge | 11,3 g |
| Very Berry Smoothie Bowl | 21,9 g |
| Winterliche Bowl mit Kürbis | 35,4 g |

</details>

Bei den beiden höchsten Werten (Kichererbsen-Paprika Pfanne 35,7 g, Winterliche Bowl mit
Kürbis 35,4 g) steckt die Menge in großen Mengen roher/trockener Hülsenfrüchte (180 g
Kichererbsen bzw. 125 g Kidneybohnen, jeweils `portionen: 1`) — rechnerisch korrekt, aber an
der oberen Grenze dessen, was in einer Portion plausibel ist. Nicht Teil dieser Prüfung, aber
der Hinweis gehört hierher, falls die Portionsgröße selbst noch mal geprüft werden soll.

Nicht in PocketBase gespeichert ist der Ballaststoffwert je Zutat (nur das Rezept-Aggregat) —
anders als bei den Haupt-Nährwerten gibt es dafür kein Feld in `zutaten`. Eine künftige
Gegenrechnung „Summe der Zeilen" wie bei kcal/Eiweiß/Kohlenhydrat/Fett ist für Ballaststoffe
deshalb nicht möglich, ohne das Datenmodell zu erweitern.

### Grüner Spargel — erledigt (vormals 2 Treffer bei der Zutaten-Plausibilität)

Zwei Zutatenzeilen hatten Makros, die mehr kcal ergeben als eingetragen (Grüner Spargel mit
Hähnchen und Curry: 44 kcal angegeben, Makros ergaben 64; Quinoasalat mit grünem Spargel,
Kichererbsen und Walnüssen: 33 kcal angegeben, Makros ergaben 47). Beide Zeilen trugen
offensichtlich falsche Werte — 200 g bzw. 150 g „Grüner Spargel" mit 44 bzw. 33 kcal wären
22 kcal/100 g gewesen, aber mit Protein- und Fettanteilen, die dazu nicht passten (4 g Eiweiß
und 4 g Fett auf 200 g Spargel ist für das Gemüse zu viel).

Mit `naehrwerte_bls` („Spargel roh", 28 kcal / 3,98 g K / 1,96 g E / 0,156 g F je 100 g)
neu berechnet und in beide Rezepte geschrieben, Rezeptsummen entsprechend angepasst:

| Rezept | kcal vorher → nachher |
|---|---|
| Grüner Spargel mit Hähnchen und Curry | 386 → 397 kcal |
| Quinoasalat mit grünem Spargel, Kichererbsen und Walnüssen | 639 → 649 kcal |

Berechnete Tags wurden danach geprüft, keine Änderung nötig.

## Veröffentlichte Seiten: 28 von 28 sauber

`tools/pruefe-rezepte.py --veroeffentlicht` meldet **0 Befunde** — Tags, Allergene,
Vollständigkeit und (soweit die Zutaten-Nährwerte vorliegen) die Nährwert-Gegenrechnung
stimmen bei allen 28 Seiten. Das schließt die 16 Rezepte ein, deren Zutaten-Nährwerte heute
nachgetragen wurden.

## Was das für die Veröffentlichung heißt

Der Bestand ist strukturell sauber: keine Tag-Widersprüche, keine fehlenden Allergene, keine
leeren Rubriken, keine Dubletten, keine Rezepte ohne Zutaten/Schritte/Zeit, keine
Nährwert-Widersprüche mehr.

**Nachtrag:** Die 50 Rezepte, die noch auf `status: neu` standen, wurden danach inhaltlich
gelesen (nicht nur automatisiert geprüft — Regel 1 verlangt mehr) und stehen jetzt auf
`geprueft`. Dabei kamen sieben konkrete, vom automatischen Check nicht erfasste Lücken heraus:
zwei in der Zubereitung verwendete, aber nie im Zutatenfeld stehende Zutaten (Kurkuma, Kurkuma-
Zitrone-Ingwer Shot; Limettensaft, Glasnudelsalat mit Tempeh), fehlende Gemüsebrühe in beiden
Gnocchi-Pfannen, fehlende Maisstärke in der Asiatischen Gemüse-Reis-Pfanne, eine Frühlingszwiebel
mit `menge = 0` trotz Verwendung (Nudelsalat), und ein als Fließtext-Rest in den Vorgänger
gerutschter Zubereitungsschritt (Rote Linsen Dal). Alle sieben behoben, Details dazu in
`CLAUDE.md` unter „Offene Punkte". Damit ist der komplette Bestand (506 Rezepte) auf
`status: geprueft`, und `pruefe-rezepte.py` meldet für beide Bestände (veröffentlicht und
unveröffentlicht) 0 Befunde.

Für die Nachträge habe ich in PocketBase geschrieben: `ballaststoffe` bei den 44
Ballaststoffreich-Rezepten, die Zutatenzeile und die Rezeptsumme bei den beiden
Grüner-Spargel-Rezepten, die sieben oben genannten Korrekturen, und zuletzt `status` bei
den 50 Rezepten. Sonst nichts an den Daten verändert.
