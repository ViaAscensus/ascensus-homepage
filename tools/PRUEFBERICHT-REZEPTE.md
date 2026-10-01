# Prüfbericht: Rezeptbestand

Stand 01.10.2026 · Quelle `pb.ascensus.fit` · 506 `rezepte`-Datensätze, davon 28
veröffentlicht (`tools/slug-map.json`) und 478 unveröffentlicht. Grundlage ist der
aktuelle Code-Stand von `tools/pruefe-rezepte.py`, einschließlich der heutigen
Atwater-Erweiterung (Ballaststoffe 2 kcal/g, Fruchtsäuren 3 kcal/g nach Anhang XIV
VO (EU) 1169/2011).

## Befund: 0

```
python3 tools/pruefe-rezepte.py                   → 478 geprüft, 0 Befunde
python3 tools/pruefe-rezepte.py --veroeffentlicht  →  28 geprüft, 0 Befunde
```

Tags, Allergene, Vollständigkeit (Zutaten/Schritte/Zeiten/Mengen/Kategorie), die
Nährwert-Gegenrechnung (Rezept gegen Zutatensumme) und die Atwater-Plausibilität
(Rezeptebene wie Einzelzutat) sind für beide Bestände sauber. Keine Dubletten.

Alle 506 Rezepte stehen auf `status: geprueft` — keines mehr auf `neu`.

## Wie der Bestand hierher kam

Der vorletzte Bericht (28.09.2026, 497 unveröffentlichte Rezepte) fand vier große
Fehlerklassen: 40 Tag-Widersprüche (Laktosefrei/Vegan/Glutenfrei/EggFree gegen die
Zutatenliste), 90 fehlende Allergenangaben, eine bei allen 497 leere `kategorie`
und 29–135 Tag-Schwellen-Abweichungen bei den berechneten Tags. Die wurden
zwischen dem 28.09. und dieser Sitzung behoben — vermutlich über
`korrigiere-rezepte.py`, `setze-rubriken.py` und `berechne-tags.py`, aber
außerhalb dieser Sitzung.

In der heutigen Sitzung kam der Rest dazu:

1. **7 Datensätze gelöscht** — 5 Testrezepte ohne jede Zubereitung (Endiviensalat
   mit Feta in Öldressing, Kartoffelwaffeln, Overnight Oats mit Haferdrink,
   Pancakes mini, Pita Taschen) und 2 mit in sich widersprüchlichen Zutatendaten
   (`menge = 0` bei gleichzeitig eingetragenem Nährwert: Cashewmilch mit 6 g Fett,
   Koriander mit 31 kcal).

2. **16 veröffentlichte Rezepte** ohne Zutaten-Nährwerte seit der Veröffentlichung
   nachgetragen (9 vom 03.09., 7 der acht ohne Status-Update vom September),
   dazu ein Duplikat (Iced Coffee mit Quark / Iced Protein Coffee) zusammengeführt.
   Werte aus `naehrwerte_bls`, Mengen in EL/TL/Stück mit gängigen
   Küchenmaß-Äquivalenten umgerechnet. Tags neu berechnet, Status der acht auf
   `geprueft` gesetzt, Seiten neu gebaut.

3. **Atwater-Gegenprobe erweitert** (`tools/pruefe-rezepte.py`): Ballaststoffe
   (2 kcal/g) und Fruchtsäuren (3 kcal/g, Zitrone/Zitronensaft/Limette/
   Limettensaft) zählen jetzt mit — ohne das meldete jedes ballaststoff- oder
   zitruslastige Rezept einen Widerspruch, der keiner war.

4. **44 Ballaststoffreich-Rezepte**: `ballaststoffe` stand bei allen auf 0, das
   Tag war nicht verifizierbar. Aus `naehrwerte_bls` (Feld `FIBT`) je Zutat
   nachgerechnet — bei allen 44 bestätigt sich das Tag (7,4–35,7 g/Portion).

5. **Grüner Spargel** in 2 Rezepten hatte Zutatenzeilen mit unplausiblen Makros
   (Protein/Fett-Werte, die nicht zu Spargel passen). Mit `naehrwerte_bls`
   („Spargel roh") neu berechnet.

6. **Die 50 Rezepte mit `status: neu`** wurden inhaltlich gelesen — nicht nur
   automatisiert geprüft, Regel 1 aus `CLAUDE.md` verlangt mehr als einen
   bestandenen Check. Dabei fielen 7 Lücken auf, die kein automatischer Check
   sieht, weil sie keine falschen, sondern fehlende Daten sind:

   | Rezept | Lücke |
   |---|---|
   | Kurkuma-Zitrone-Ingwer Shot | Kurkuma fehlte im Zutatenfeld, obwohl die Zubereitung es verlangt |
   | Glasnudelsalat mit Tempeh | Limettensaft fehlte (wird im Dressing verwendet) |
   | Gnocchi-Pfanne mit Lachs und Tomate | Gemüsebrühe fehlte |
   | Gnocchi-Pfanne mit Linsenbratlingen | Gemüsebrühe fehlte |
   | Asiatische Gemüse-Reis-Pfanne mit Hähnchen | Maisstärke zum Binden fehlte |
   | Nudelsalat | Frühlingszwiebel mit `menge = 0` trotz Verwendung im Rezept |
   | Rote Linsen Dal | Ein Zubereitungsschritt steckte als Fließtext-Rest im Vorgänger |

   Alle sieben mit Mengen und `naehrwerte_bls`-Werten ergänzt, Rezeptsummen neu
   berechnet. Dabei außerdem aufgefallen: „Kokos Pfanne" in der
   Reis-Süßkartoffel-Pfanne mit Tofu ist laut Zubereitungstext eine fertige
   Gemüsepfanne, keine reine Fettquelle wie beim Ballaststoff-Nachtrag (Punkt 4)
   zunächst angenommen — Ballaststoffwert korrigiert (12,4 → 16,4 g/Portion).
   Danach Tags neu berechnet (1 Änderung) und alle 50 auf `status: geprueft`
   gesetzt.

## Bekannte Grenzen, kein offener Fehler

- **Ballaststoffe sind nur für die 44 Rezepte mit dem Tag „Ballaststoffreich"
  nachgerechnet**, nicht für den übrigen Bestand. Bei den restlichen
  unveröffentlichten Rezepten steht `ballaststoffe` weiterhin auf 0 — das ist
  keine falsche Angabe, nur eine nicht geschlossene Lücke. Eine Gegenrechnung
  „Summe der Zutatenzeilen" ist dafür ohnehin nicht möglich, weil es in
  `zutaten` kein Ballaststoff-Feld je Zeile gibt, nur das Rezept-Aggregat.
- **Fruchtsäuren** zählen in der Atwater-Gegenprobe nur für eine kurze, nicht
  erschöpfende Liste (Zitrone, Zitronensaft, Limette, Limettensaft) — ergänzt
  nach Bedarf, so wie die Whey/Laktose-Regel, nicht vorsorglich für jedes
  säurehaltige Lebensmittel.
- **Mengen aus EL/TL/Stück** wurden mit gängigen Küchenmaß-Äquivalenten in Gramm
  umgerechnet (z. B. 1 EL Öl = 10 g, 1 Ei = 60 g) — Schätzungen, keine
  Originalangaben.

## Was das für die Veröffentlichung heißt

Es gibt aktuell keine bekannte Fehlerliste mehr, die vor einer Veröffentlichung
abzuarbeiten wäre. Alle drei Freigabe-Prüfungen aus `CLAUDE.md` (`status:
geprueft`, `zeit_gesamt > 0`, Tags passend zur Zutatenliste) sind für den
gesamten Bestand erfüllt. Das ersetzt nicht die eigene inhaltliche Durchsicht
vor jeder einzelnen Veröffentlichung — nur die automatisiert prüfbaren Punkte
sind erledigt.
