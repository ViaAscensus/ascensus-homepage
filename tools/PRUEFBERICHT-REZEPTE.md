# Prüfbericht: 497 unveröffentlichte Rezepte

Stand 28.09.2026 · Quelle `pb.ascensus.fit` · geprüft wurden alle 515 `rezepte`-Datensätze
abzüglich der 18 in `tools/slug-map.json`. Alle 497 stehen auf `status = neu`.

## Vorbemerkung zur Datenbasis

Das Feld `zutaten.naehrwerte_pro_100g` trägt trotz seines Namens **nicht** Werte je 100 g,
sondern die absoluten Werte für die jeweils eingetragene Menge. Gegengerechnet an
*Ofen-Kartoffel mit Kräuterquark* (490 kcal), *Pancakes mini* (79 kcal),
*Reiswaffeln mit Erdnussmus und Banane* (297 kcal) und *Selfmade Knusper-Müsli-Bowl*
(4812 kcal / 10 Portionen = 481): die Summe der Zutatenzeilen trifft den Rezeptwert jeweils
exakt. Die Gegenrechnung läuft deshalb als *Summe der Zeilen ÷ Portionen*.

## Übersicht nach Schwere

| # | Fehlerklasse | Anzahl | Wirkung |
|---|---|---|---|
| A1 | Laktosefrei trotz Milchprodukt | **21** | falsche Gesundheitsaussage |
| A2 | Vegan trotz tierischer Zutat | **10** | falsche Gesundheitsaussage |
| A3 | Glutenfrei trotz Gluten | **7** | falsche Gesundheitsaussage |
| A4 | EggFree trotz Ei | **6** | falsche Gesundheitsaussage |
| A5 | Allergen nicht deklariert | **90** | LMIV-relevant |
| B1 | `kategorie` leer | **497** | fällt still auf „Hauptgericht" zurück |
| B2 | `ballaststoffe` = 0 bei allen | **497** | Ballaststoffreich nicht prüfbar |
| B3 | `zeit_gesamt` = 0 | **11** | kein Zeit-Badge, kein cookTime |
| B4 | ohne Zubereitungsschritte | **5** | Seite ohne Anleitung |
| B5 | `menge` = 0 bei echter Zutat | **12** | "nach Geschmack" statt Menge |
| B6 | Namensdubletten | **3** | doppelte Kacheln / URLs |
| C1 | High-Carb unter Schwelle | **135** | Tag trägt nicht |
| C2 | High-Protein unter Schwelle | **29** | Tag trägt nicht |
| C3 | Schnell und einfach > 30 Min. | **23** | Tag trägt nicht |
| C4 | Low-Carb über Schwelle | **20** | Tag trägt nicht |
| C5 | Kalorienarm über Schwelle | **15** | Tag trägt nicht |
| D1 | Rezeptwerte ≠ Zutatensumme (>15 %) | **0** | — |
| D2 | Getränk: kcal passen nicht zu Makros | **4** | kleine Absolutwerte |
| D3 | Zutatenzeile mit zu hohen Makros | **2** | Einzelwert prüfen |

---

## A — Falsche Auszeichnungen (blockieren die Veröffentlichung)

**40 Rezepte** tragen ein Diät-Tag, das die Zutatenliste widerlegt (44 Treffer, vier Rezepte
stehen in zwei Klassen: Kichererbsen-Dal mit Hirse, Kokos-Curry mit Hirse, Roasted Veggie
Enchilada Casserole, Strawberry Matcha Latte). Bezugsgrößen: Laktosefrei 256×, Glutenfrei 277×,
EggFree 271×, Vegan 139×, Vegetarisch 306× vergeben — Vegetarisch ist als einziges dieser Tags
durchgehend korrekt gesetzt.

### A1 · Laktosefrei trotz Milchprodukt — 21

Molkenprotein (*Whey*) zählt hier mit: Konzentrat trägt Laktose, nur Isolat wäre unkritisch.

| Rezept | Zutat |
|---|---|
| Bagel mit Avocado und Ei | Frischkäse mit Kräutern |
| Banane-Avocado-Spinat Shake (proteinreicher) | Whey Protein, Vanille |
| Fitness-Vanillekipferl | Butter |
| Frühstücks-Wrap mit Putenbrust | Frischkäse |
| Frühstücks-Wraps | Käse (Scheibe) |
| Hühnchen-Avocado-Pesto Nudeln | Parmesan |
| Kichererbsen-Dal mit Hirse | Ghee |
| Kokos-Curry mit Hirse | Ghee |
| Linsensalat mit Avocado | Schafskäse, Light |
| Orientalisches Müsli | Joghurt < 1% Fett |
| Rindfleisch-Burger | Cheddar mind. 50% Fett i. Tr. |
| Roasted Veggie Enchilada Casserole | Gouda |
| Rote-Bete-Schoko Muffins | Butter |
| Schoko-Bananen-Porridge | Proteinpulver Whey, Schokolade |
| Schoko-Kokos Porridge (proteinreicher) | Whey Protein, Schoko |
| Strammer Max Klassisch | Butter |
| Strawberry Matcha Latte | Proteinpulver Whey, neutral |
| Süße Quinoa-Bowl | Milch 1,5% Fett |
| Süßkartoffelbrownies | Proteinpulver Whey, Schokolade |
| Süßkartoffeltoast mit Avocado und Ei | Körniger Frischkäse < 10% Fett i. Tr. |
| Vollkornbrötchen mit Schinken | Streichkäse leicht 9% |

### A2 · Vegan trotz tierischer Zutat — 10

| Rezept | Zutat |
|---|---|
| Gefüllte Zucchini mit Veganem Hackfleisch und Reis | Pizzakäse, light |
| Kichererbsen-Dal mit Hirse | Ghee |
| Kokos-Cookies | Eier roh |
| Kokos-Curry mit Hirse | Ghee |
| Mangold-Salat mit Apfelstücken und Walnüssen | Honig |
| Orangen Chicken Curry - Vegan | Honig |
| Reispfanne mit Tempeh in Erdnusssauce | Honig |
| Roasted Veggie Enchilada Casserole | Gouda |
| Strawberry Matcha Latte | Proteinpulver Whey, neutral |
| Süßkartoffel-Hack-Auflauf - Vegan | Mozzarella, Streukäse |

### A3 · Glutenfrei trotz glutenhaltiger Zutat — 7

Hafer ist von Natur aus glutenfrei, gilt nach LMIV aber als glutenhaltiges Getreide, solange er nicht ausdrücklich als glutenfrei deklariert ist. Ungekennzeichnete Sojasauce enthält Weizen.

| Rezept | Zutat |
|---|---|
| Fitness-Plätzchen | Haferflocken |
| Quark-Haferflocken Brötchen mit Käse | Haferflocken |
| Quark-Haferflocken Brötchen mit Schinken | Haferflocken |
| Reis-Süßkartoffel-Pfanne mit Tofu | Sojasauce |
| Schoko-Tannenbäume | Salzstangen |
| Süßkartoffelwaffeln mit Avocado und Lachs | Mehl |
| Tofu-Gemüse-Spieße mit mildem Curry-Dip | Sojasauce |

### A4 · EggFree trotz Ei — 6

| Rezept | Zutat |
|---|---|
| American  Sandwich | Mayo light |
| Big Mac Bowl | Mayonnaise light |
| Big Mac Bowl - Vegetarisch | Mayonnaise light |
| Cottage Cheese Pizza | Eier roh |
| Räucherforelle mit Gemüsepuffer | Eier roh |
| Tiramisu Cream Cups mit körnigem Frischkäse | Löffelbiskuit aus Biskuitmasse |

### A5 · Allergen nicht deklariert — 90

Verteilung der fehlenden Angaben:

| Allergen | fehlt in | häufigste Auslöser |
|---|---|---|
| Gluten | 70 | Haferflocken (36), Sojasauce (13), Gnocchi roh (4) |
| Nuesse | 9 | Nüsse (4), Allos Mandel Cuisine (3), Cashewmilch (1) |
| Milch | 6 | Whey Protein, Vanille (3), Whey Protein Neutral (1), Halloumi (1) |
| Eier | 3 | Löffelbiskuit aus Biskuitmasse (2), Hühnerei Eiweiß (1) |
| Sesam | 2 | Tahini aus rohem Sesam (2) |
| Krebstiere | 2 | Frutti di Mare (1), Frutti Di Mare (1) |
| Sojabohnen | 1 | Veganes Bio-Soja-Faschiertes (1) |

Bei 21 der 90 auffälligen Rezepte ist `allergene` komplett leer, bei den übrigen 69 steht eine
unvollständige Angabe (etwa „Nüsse", obwohl auch Haferflocken drin sind — das ist der häufigere
und heiklere Fall, weil die Angabe dann vollständig aussieht).

Unabhängig davon ist bei 90 der 497 Rezepte das Feld leer; bei 69 davon habe ich auch kein
deklarationspflichtiges Allergen in der Zutatenliste gefunden, dort ist das Feld plausibel leer.

<details><summary>Alle 90 Rezepte</summary>

| Rezept | bisher eingetragen | fehlt |
|---|---|---|
| Apfel-Beeren-Muffins | Nüsse | Gluten (Haferflocken) |
| Aprikose-Dattel Energy Balls | — | Gluten (Haferflocken) |
| Asiatisches Gemüse mit Tofu-Streifen | Sesam, Sojabohnen | Gluten (Sojasauce) |
| Banane-Avocado-Spinat Shake (proteinreicher) | Nüsse | Milch (Whey Protein, Vanille) |
| Banane-Vanille-Waffeln | Milch | Gluten (Haferflocken) |
| Banane-Vanille-Waffeln - Vegan | — | Gluten (Haferflocken) |
| Bananen-Waffeln | Eier | Gluten (Haferflocken) |
| Beerige Baked Oats | Eier, Nüsse, Milch | Gluten (Haferflocken) |
| Big Mac Bowl - Vegetarisch | Senf, Milch, Eier | Sojabohnen (Veganes Bio-Soja-Faschiertes) |
| Blaubeere-Banane-Shake | — | Milch (Whey Protein, Vanille) |
| Cashew-Apfel-Zimt Quinoa | — | Nuesse (Cashewmilch) |
| Cheesecake Overnight Oats mit körnigem Frischkäse | Milch, Nüsse | Gluten (Haferflocken) |
| Cheesecake Pancake | Gluten, Eier, Milch | Nuesse (Nussmus) |
| Chia-Apfel-Zimt Shake (kohlenhydratreicher) | — | Gluten (Haferflocken) |
| Cremige Pasta mit Lauch und Tomate | — | Nuesse (Allos Mandel Cuisine) |
| Cremige Pasta mit Lauch und Tomate - Vegan | — | Nuesse (Allos Mandel Cuisine) |
| Crispy Hot Honey Chicken Bowl | Milch, Sojabohnen | Gluten (Sojasoße light) |
| Fitness-Kokosmakronen | Milch | Eier (Hühnerei Eiweiß) |
| Fitness-Plätzchen | Nüsse, Eier, Milch | Gluten (Haferflocken) |
| Gelbes Curry | Sojabohnen | Gluten (Sojasauce) |
| Gnocchi mit Tomaten und Mozzarella | Milch | Gluten (Gnocchi roh) |
| Gnocchi Pfanne mit Rucola und Feta | Milch | Gluten (Gnocchi roh) |
| Gnocchi-Champignon-Pfanne mit Puten-Streifen | — | Gluten (Gnocchi mit Spinat und Basilikum) |
| Gnocchi-Pfanne mit Lachs und Tomate | Fisch, Milch | Gluten (Gnocchi roh) |
| Gnocchi-Pfanne mit Linsenbratlingen | Milch | Gluten (Gnocchi mit Süßkartoffel) |
| Gnocchi-Pfanne mit Rucola, Feta und Vegan Chicken | Milch | Gluten (Gnocchi roh) |
| Green Smoothie-Bowl | Milch | Gluten (Haferflocken) |
| Haferflocken-Bananen-Pancakes | Eier, Milch | Gluten (Haferflocken) |
| Hähnchenbrustfilet mit Auberginen-Hummus | — | Sesam (Tahini aus rohem Sesam) |
| Himbeer-Tiramisu | Milch, Gluten | Eier (Löffelbiskuit aus Biskuitmasse) |
| Kabeljau-Gemüse-Pasta | Fisch, Milch | Gluten (Vollkornnudeln) |
| Kartoffelwaffeln | Eier, Milch | Gluten (Hartweizengriess, trocken) |
| Klassisches Bananenbrot | Eier, Gluten | Milch (Whey Protein Neutral) |
| Kokos-Birne-Porridge | — | Gluten (Haferflocken) |
| Lachs-Bowl | Fisch, Erdnüsse, Milch, Sojabohnen, Sesam | Gluten (Sojasauce) |
| Lachs-Reis-Bowl mit Edamame und Avocado | Sojabohnen, Fisch, Milch, Sesam | Gluten (Soja Sauce) |
| Lachs-Spinat-Nudel-Auflauf | Fisch, Milch | Gluten (Vollkornnudeln) |
| Lebkuchen Bites | Nüsse | Gluten (Haferflocken) |
| Lebkuchen-Porridge | Nüsse | Gluten (Haferflocken) |
| Leinsamen-Haferbrot - Glutenfrei | — | Nuesse (Nüsse) |
| Mandel-Beeren Porridge - Vegan | Nüsse | Gluten (Haferflocken) |
| Mango-Bananen-Shake | — | Milch (Whey Protein, Vanille) |
| Matcha Energy Balls | Nüsse, Erdnüsse | Gluten (Haferflocken) |
| Maultaschen-Pfanne | — | Gluten (Vegan Maultaschen) |
| Meeresfrüchte-Spaghetti | Gluten | Krebstiere (Frutti di Mare) |
| Nüsse und Rosinen | Schwefeldioxid und Schwefeldioxid-Nitrat | Nuesse (Nüsse) |
| Nussiges Porridge mit Mandeln und Cranberries | Nüsse, Milch | Gluten (Haferflocken) |
| Oat Cake aus dem Airfryer | Milch, Eier, Nüsse | Gluten (Haferflocken) |
| Orangen Chicken Curry - Vegan | Sesam, Sojabohnen | Gluten (Sojasauce) |
| Orangen Puten Curry | Sojabohnen, Sesam | Gluten (Sojasauce) |
| Orientalische Linsen-Bowl | — | Sesam (Tahini aus rohem Sesam) |
| Overnight Oats | — | Gluten (Haferflocken Feinblatt) |
| Overnight-Oats | Milch, Nüsse | Gluten (Haferflocken) |
| Pita Taschen | — | Milch (Halloumi); Gluten (Pita Brottaschen) |
| Porridge mit Banane und Walnüssen | Nüsse, Milch | Gluten (Haferflocken) |
| Porridge mit Banane und Walnüssen - Vegan | Nüsse | Gluten (Haferflocken) |
| Post-Workout-Shake - Vegan | Milch | Gluten (Hafermilch) |
| Quark mit Früchten | Milch | Nuesse (Nüsse) |
| Quark mit Haferflocken, Mandeln und Nüssen | Milch, Nüsse | Gluten (Haferflocken) |
| Quark-Haferflocken Brötchen | Eier, Milch | Gluten (Haferflocken) |
| Quark-Haferflocken Brötchen mit Käse | Milch, Eier | Gluten (Haferflocken) |
| Quark-Haferflocken Brötchen mit Schinken | Milch, Eier | Gluten (Haferflocken) |
| Quinoa-Salat Mexican Style - Vegan | — | Gluten (Seitan) |
| Reis-Süßkartoffel-Pfanne mit Tofu | Sojabohnen, Sesam | Gluten (Sojasauce) |
| Reisnudelbowl mit Gemüse und gebackenem Tofu | Sojabohnen, Eier, Erdnüsse, Sesam | Gluten (Sojasauce) |
| Reispfanne mit Tempeh in Erdnusssauce | Erdnüsse, Milch, Sojabohnen | Gluten (Sojasauce) |
| Rindersteak mit frischen Kartoffel-Pommes und einer Frischkäse-Pfeffer-Soße | Milch, Sojabohnen | Gluten (Sojasoße) |
| Rindfleisch-Bites | Sojabohnen | Gluten (Sojasoße) |
| Salat mit Feta und Granatapfel | Milch | Nuesse (Nüsse) |
| Schnelle Gemüse-Reispfanne mit Ei | Eier, Sojabohnen | Gluten (Sojasauce) |
| Schoko-Bananen-Porridge | Milch, Nüsse | Gluten (Haferflocken) |
| Schoko-Bananen-Porridge - Vegan | Nüsse | Gluten (Haferflocken) |
| Schoko-Kokos Porridge | Nüsse | Gluten (Haferflocken) |
| Schoko-Kokos Porridge (proteinreicher) | Nüsse | Milch (Whey Protein, Schoko); Gluten (Haferflocken) |
| Schoko-Kokos Porridge (proteinreicher) - Vegan | Nüsse | Gluten (Haferflocken) |
| Selbstgemachter Hummus | — | Nuesse (Allos Mandel Cuisine) |
| Selbstgemachtes Beef Jerky im Air Fryer | Sojabohnen | Gluten (Sojasoße) |
| Selfmade Knusper-Müsli-Bowl | Nüsse, Milch | Gluten (Haferflocken) |
| Skyr-Muffins mit Paprika und Käse | Milch, Eier | Gluten (Haferflocken) |
| Sommerlicher Glasnudelsalat mit Mango und Erdnusssoße | Erdnüsse, Sesam, Sojabohnen | Gluten (Sojasauce) |
| Sommerrollen #Vegetarisch | Sojabohnen, Eier, Erdnüsse, Sesam | Gluten (Sojasauce) |
| Sommerrollen mit Hühnchen | Sojabohnen, Eier, Erdnüsse, Sesam | Gluten (Sojasauce) |
| Thunfisch-Vollkornnudel-Auflauf | Fisch, Milch | Gluten (Vollkornnudeln) |
| Tiramisu Cream Cups mit körnigem Frischkäse | Milch, Gluten, Nüsse | Eier (Löffelbiskuit aus Biskuitmasse) |
| Tofu-Gemüse-Spieße mit mildem Curry-Dip | Sojabohnen | Gluten (Sojasauce) |
| Tomate-Paprika-Gnocchi Pfanne mit Meeresfrüchten | — | Gluten (Bio Gnocchi Dinkel); Krebstiere (Frutti Di Mare) |
| Vegan Green Smoothie-Bowl | — | Gluten (Haferflocken) |
| Weihnachtliche Apfel-Zimt-Muffins | Nüsse | Gluten (Haferflocken) |
| Zimtschnecken-Bananenbrot | Milch, Eier | Gluten (Haferflocken) |
| Zoats | — | Gluten (Haferflocken) |

</details>

---

## B — Vollständigkeit

### B1 · `kategorie` ist bei allen 497 leer

Kein einziger unveröffentlichter Datensatz hat eine Rubrik. `build-rezepte.py:154` fängt das
still ab (`FILTER.get(r["kategorie"], ("hauptgericht", "Hauptgericht"))`), sodass jedes Rezept
als *Hauptgericht* einsortiert würde, und `:139` schreibt ein leeres `{{KATEGORIE}}` in die Seite.
Das trifft jede Veröffentlichung aus diesem Bestand und ist damit der breiteste Einzelbefund.

### B2 · `ballaststoffe` = 0 bei allen 497

Damit lässt sich das Tag **Ballaststoffreich** (44× vergeben, davon 
44 unter den 497) nicht gegenrechnen. Die Zutatenzeilen führen 
ebenfalls keine Ballaststoffe, eine Rekonstruktion aus dem Bestand ist also nicht möglich.

### B3 · `zeit_gesamt` = 0 — 11

| Rezept | Hinweis |
|---|---|
| Eiweißriegel (fertig) |  |
| Endiviensalat mit Feta in Öldressing |  |
| Gefüllter Truthahn mit Apfel-Walnuss-Füllung, Süßkartoffelpüree und geröstetem Rosenkohl |  |
| Gemüsepfanne mit Pute |  |
| Kartoffelwaffeln |  |
| MangoButtermilch (kalt) |  |
| Orientalisches Müsli  - Vegan |  |
| Overnight Oats |  |
| Pancakes mini |  |
| Pita Taschen |  |
| Spicy Red Curry Nudelsalat mit Hähnchenbrustfilet |  |

### B4 · ohne Zubereitungsschritte — 5

| Rezept | Hinweis |
|---|---|
| Endiviensalat mit Feta in Öldressing |  |
| Kartoffelwaffeln |  |
| Overnight Oats |  |
| Pancakes mini |  |
| Pita Taschen |  |

### B5 · `menge` = 0 bei kalorienrelevanter Zutat — 12

Der Generator schreibt für diese Zeilen "nach Geschmack" (`menge_text`), obwohl die Zutat mit ≥ 5 kcal in der Bilanz steht.

| Rezept | Zutat |
|---|---|
| Bananen-Pancakes | Tapiokastärke (g) |
| Cashew-Apfel-Zimt Quinoa | Cashewmilch (g) |
| Cottage Cheese Pizza | Light-Streukäse (g) |
| Cremige Pasta mit Lauch und Tomate | Allos Mandel Cuisine (g) |
| Cremige Pasta mit Lauch und Tomate - Vegan | Allos Mandel Cuisine (g) |
| Endiviensalat mit Feta in Öldressing | Condimento Bianco (g) |
| Gurken-Kokosdrink mit Koriander | Koriander, frisch (g) |
| Kartoffelwaffeln | Hartweizengriess, trocken (g) |
| Overnight Oats | 4 Korn Flocken (g); Haferflocken Feinblatt (g); Chia Samen (g) |
| Rindersteak mit frischen Kartoffel-Pommes und einer Frischkäse-Pfeffer-Soße | Schwarzer Pfeffer, ganzes Korn (g); Schwarzer Grün, ganzes Korn (g) |
| Selbstgemachter Hummus | Allos Mandel Cuisine (g) |
| Tomaten-Spaghetti mit Hackbällchen | Knoblauchzehe (g); gehackte Tomaten (g) |

### B6 · Namensdubletten — 3 Paare

| Datensätze | Bemerkung |
|---|---|
| `9gh4ubu03pv4st8` Apfel-Buchweizen Pancakes **(veröffentlicht)** / `r5ywxnobwwz1n6k` Apfel-Buchweizen-Pancakes | Schreibweise unterscheidet sich nur im Bindestrich |
| `ra2kgcccxndal1l` Himbeer- Bananen Nice Cream (ohne Eismaschine) / `z2v1cp9z7h7npyp` Himbeer-Bananen Nice Cream (ohne Eismaschine) | Schreibweise unterscheidet sich nur im Bindestrich |
| `0n03qzbd5nl33oe` Overnight Oats / `acaftgjd1ogxpql` Overnight-Oats | Schreibweise unterscheidet sich nur im Bindestrich |

*Apfel-Buchweizen Pancakes* ist bereits als `rezept-apfel-buchweizen-pancakes.html` live;
`r5ywxnobwwz1n6k` ist ein zweiter Datensatz mit Bindestrich. Ein Slug für den Zweitsatz würde
mit der bestehenden Seite kollidieren.

---

## C — Berechnete Tags gegen die Nährwerte

### Angesetzte Schwellen

| Tag | Schwelle | Herkunft |
|---|---|---|
| High-Protein | Eiweiß ≥ 20 % der kcal | VO (EG) 1924/2006, Claim „hoher Proteingehalt" |
| Ballaststoffreich | ≥ 3 g je 100 kcal | VO (EG) 1924/2006, Claim „hoher Ballaststoffgehalt" |
| Low-Carb | Kohlenhydrate ≤ 20 % der kcal | keine gesetzliche Definition, gängige Praxis |
| High-Carb | Kohlenhydrate ≥ 55 % der kcal | keine gesetzliche Definition, DGE-Richtwert |
| Kalorienarm | ≤ 400 kcal je Portion | keine gesetzliche Definition (der LMIV-Wert von 40 kcal/100 g zielt auf Einzellebensmittel, nicht auf Mahlzeiten) |
| Schnell und einfach | `zeit_gesamt` ≤ 30 Min. | Hausregel |

Die Schwelle für High-Protein ist an der Bircher-Müsli-Notiz in `CLAUDE.md` geeicht:
13 g Eiweiß auf 401 kcal = 13 E% — das Tag trägt nicht, genau wie dort vermerkt.

### Wie stark die Zahlen an der Schwelle hängen

| Tag | vergeben | Treffer bei drei Schwellen |
|---|---|---|
| High-Carb | 178 | < 50 E%: **96** · < 55 E%: **135** · < 60 E%: **159** |
| High-Protein | 237 | < 15 E%: **4** · < 20 E%: **29** · < 25 E%: **83** |
| Low-Carb | 70 | > 15 E%: **28** · > 20 E%: **20** · > 26 E%: **11** |
| Kalorienarm | 64 | > 300 kcal: **30** · > 400 kcal: **15** · > 500 kcal: **5** |

**High-Carb ist der Sonderfall.** Der Median der so getaggten Rezepte liegt bei 49 E%, der
Median über alle 497 bei 41 E% — das Tag wurde offenbar relativ vergeben („kohlenhydratbetont
im Vergleich zum Rest"), nicht gegen eine feste Grenze. Die 135 sind deshalb weniger eine
Fehlerliste als ein Hinweis, dass für dieses Tag erst eine Definition festgelegt werden muss.
Die anderen drei Tags sitzen sauber: bei High-Protein liegt das 25. Perzentil bei 23 E%, die
29 Treffer sind echte Ausreißer.

### C2 · High-Protein unter 20 E% — 29

| Rezept | Rechnung |
|---|---|
| Bagel mit Avocado und Ei | 17 g EW bei 471 kcal = 14 E% |
| Buchweizen-Spaghetti-Paprika Pfanne mit Ei | 28 g EW bei 695 kcal = 16 E% |
| Cashew-Curry mit Reis | 33 g EW bei 686 kcal = 19 E% |
| Chicken Korma | 30 g EW bei 676 kcal = 18 E% |
| Cremige Frischkäse Pasta mit Gemüse | 29 g EW bei 665 kcal = 17 E% |
| Cremige Linsen-Pasta - Vegan | 28 g EW bei 623 kcal = 18 E% |
| Fitness-Plätzchen | 11 g EW bei 302 kcal = 15 E% |
| Gnocchi Pfanne mit Rucola und Feta | 28 g EW bei 669 kcal = 17 E% |
| Gnocchi-Pfanne mit Lachs und Tomate | 36 g EW bei 778 kcal = 19 E% |
| Gnocchi-Pfanne mit Linsenbratlingen | 30 g EW bei 667 kcal = 18 E% |
| Gnocchi-Pfanne mit Rucola, Feta und Vegan Chicken | 36 g EW bei 721 kcal = 20 E% |
| Green Goddess Pasta | 24 g EW bei 552 kcal = 17 E% |
| Klassischer Nudelsalat - Vegetarisch | 17 g EW bei 372 kcal = 18 E% |
| Linsennudeln mit Pesto | 29 g EW bei 631 kcal = 18 E% |
| Nudelsalat | 26 g EW bei 529 kcal = 20 E% |
| Omelette mit Rote Beete und Maiswaffeln | 19 g EW bei 430 kcal = 18 E% |
| Peanutbutter Brownies | 15 g EW bei 306 kcal = 20 E% |
| Pfirsich Burrata Salat mit gerösteten Pistazien | 14 g EW bei 460 kcal = 12 E% |
| Rainbow Bowl | 44 g EW bei 888 kcal = 20 E% |
| Schnelle Pasta mit Süßkartoffel | 27 g EW bei 607 kcal = 18 E% |
| Skyr-Schokobrötchen | 14 g EW bei 314 kcal = 18 E% |
| Sommerrollen #Vegetarisch | 16 g EW bei 458 kcal = 14 E% |
| Sommerrollen mit Hühnchen | 18 g EW bei 470 kcal = 15 E% |
| Spinat-Feta-Lasagne | 15 g EW bei 368 kcal = 16 E% |
| Süßkartoffel-Hack-Auflauf - Vegan | 18 g EW bei 373 kcal = 19 E% |
| Süßkartoffel-Quark-Pfanne mit Apfel und Zimt | 29 g EW bei 584 kcal = 20 E% |
| Tofu-Kokos-Curry | 25 g EW bei 633 kcal = 16 E% |
| Tofu-Kokos-Curry mit Reis | 26 g EW bei 688 kcal = 15 E% |
| Zucchini-Karotte Reibekuchen mit Joghurt Dip | 28 g EW bei 563 kcal = 20 E% |

### C3 · Schnell und einfach über 30 Min. — 23

| Rezept | zeit_gesamt |
|---|---|
| Apfel-Beeren-Muffins | 60 Min. |
| Chocolate Brownie Nice Cream (ohne Eismaschine) | 60 Min. |
| Coconut Balls | 50 Min. |
| Cottage Cheese Pizza | 40 Min. |
| Energy Bites mit Mandel und Kokos | 60 Min. |
| Erdnussbutter-Cheesecake im Glas | 75 Min. |
| Gefüllte Halloween Paprika - Vegan | 40 Min. |
| Gefüllte Halloween Paprika mit Hähnchen | 40 Min. |
| Himbeer-Haferflocken-Muffins | 120 Min. |
| Himbeer-Tiramisu | 60 Min. |
| Quinoa-Gemüse-Pfanne mit Garnelen | 35 Min. |
| Reis-Bowl mit Rucola, Aubergine und Süßkartoffel | 35 Min. |
| Rhabarber-Beeren Zero Schorle | 60 Min. |
| Rinderhack-Brokkoli-Auflauf mit Käsekruste | 35 Min. |
| Rote-Bete-Schoko Muffins | 40 Min. |
| Schnelle Hühner-Nudelsuppe | 35 Min. |
| Schnelle Hühnersuppe | 35 Min. |
| Selbstgemachtes Beef Jerky im Air Fryer | 120 Min. |
| Süßkartoffelwaffeln mit Avocado und Lachs | 50 Min. |
| Tiramisu Cream Cups mit körnigem Frischkäse | 120 Min. |
| Tortellini-Auflauf mit Hirtenkäse | 40 Min. |
| Überbackene Putensteaks mit Gemüse | 40 Min. |
| Zucchini-Lachs Spieße mit Honig-Senf Dip und Kartoffel Wedges | 40 Min. |

### C4 · Low-Carb über 20 E% — 20

| Rezept | Rechnung |
|---|---|
| Asiatische Gemüse-Pfanne mit Hähnchen | 32 g KH bei 405 kcal = 32 E% |
| Balanced Breakfast | 21 g KH bei 386 kcal = 22 E% |
| Cottage Cheese Pizza | 34 g KH bei 537 kcal = 25 E% |
| Fruchtzwerge Shake (Erdbeere) | 26 g KH bei 373 kcal = 28 E% |
| Fruchtzwerge Shake (Himbeere) | 26 g KH bei 370 kcal = 28 E% |
| Frühstücksbowl mit Himbeeren, Apfel und Whey-Drip | 30 g KH bei 364 kcal = 33 E% |
| Grünes Chicken-Curry - Vegan | 19 g KH bei 375 kcal = 20 E% |
| Hähnchen-Gemüse-Pfanne mit Reis | 27 g KH bei 318 kcal = 34 E% |
| Karotten-Gurken-Salat mit Ei und Kokosjoghurt | 20 g KH bei 333 kcal = 24 E% |
| Matcha-Latte mit Skyr | 8 g KH bei 112 kcal = 29 E% |
| Pfeffer-Rinderfilet auf Selleriepüree mit Balsamico-Zwiebeln | 34 g KH bei 665 kcal = 20 E% |
| Quarkauflauf mit Mandarinen | 24 g KH bei 473 kcal = 20 E% |
| Rinderfilet mit Heidelbeer-Balsamico-Reduktion auf Selleriestampf | 26 g KH bei 357 kcal = 29 E% |
| Rindfleisch-Kartoffel-Pfanne mit Hüttenkäse | 38 g KH bei 502 kcal = 30 E% |
| Rote-Bete-Schoko Muffins | 10 g KH bei 185 kcal = 22 E% |
| Skyr mit Beeren | 13 g KH bei 206 kcal = 25 E% |
| Skyr-Kaffee | 9 g KH bei 116 kcal = 31 E% |
| Süßkartoffel-Hähnchen-Gemüse Bowl | 35 g KH bei 450 kcal = 31 E% |
| Wurzelgemüse aus dem Ofen mit Hähnchenschenkel | 22 g KH bei 431 kcal = 20 E% |
| Zitrone-Minze Zero Erfrischungsgetränk | 1 g KH bei 8 kcal = 50 E% |

### C5 · Kalorienarm über 400 kcal — 15

| Rezept | Wert |
|---|---|
| Avocado-Boot mit Ei und Bacon | 634 kcal / Portion |
| Big Mac Bowl | 569 kcal / Portion |
| Big Mac Bowl - Vegetarisch | 624 kcal / Portion |
| Edamamesalat mit Wasabi-Ingwer-Dressing | 483 kcal / Portion |
| Fruchtzwerge Shake (Banane) | 446 kcal / Portion |
| Gebratene Hähnchenbrust mit griechischem Salat | 457 kcal / Portion |
| Gefüllte Paprika mit Champignons | 482 kcal / Portion |
| Gefüllte Paprika mit Champignons und Reis | 748 kcal / Portion |
| Gemüse-Sesam-Pfanne mit Thunfisch | 496 kcal / Portion |
| Gemüse-Shakshuka mit Schafskäse | 475 kcal / Portion |
| Hähnchenbrustfilet mit Hokkaido-Kürbis | 420 kcal / Portion |
| Quarkauflauf mit Mandarinen | 473 kcal / Portion |
| Rührei mit Spinat und Ziegenkäse | 563 kcal / Portion |
| Thunfisch-Reis-Pfanne | 462 kcal / Portion |
| Vegan Green Smoothie-Bowl | 490 kcal / Portion |

### C1 · High-Carb unter 55 E% — 135

<details><summary>Alle 135 — erst nach Festlegung der Schwelle sinnvoll abzuarbeiten</summary>

| Rezept | Rechnung |
|---|---|
| Bagel mit Avocado und Ei | 47 g KH bei 471 kcal = 40 E% |
| Beerige Baked Oats | 58 g KH bei 463 kcal = 50 E% |
| Bowl mit gegrillten Garnelen | 90 g KH bei 718 kcal = 50 E% |
| Bowl mit Rinderhack, Reis, Gemüse und körnigem Frischkäse | 48 g KH bei 532 kcal = 36 E% |
| Buchweizen Spaghetti mit Gemüse und Rührei | 64 g KH bei 693 kcal = 37 E% |
| Buchweizen-Spaghetti-Paprika Pfanne mit Ei | 76 g KH bei 695 kcal = 44 E% |
| Caprese Pesto Stulle | 55 g KH bei 553 kcal = 40 E% |
| Cashew-Curry mit Reis | 74 g KH bei 686 kcal = 43 E% |
| Cevapcici mit Tomatenreis | 56 g KH bei 552 kcal = 41 E% |
| Cheesecake Overnight Oats mit körnigem Frischkäse | 58 g KH bei 574 kcal = 40 E% |
| Chia-Apfel-Zimt Shake (kohlenhydratreicher) | 54 g KH bei 469 kcal = 46 E% |
| Chicken Alfredo Pasta | 40 g KH bei 349 kcal = 46 E% |
| Chicken Fajitas | 31 g KH bei 345 kcal = 36 E% |
| Chicken Korma | 81 g KH bei 676 kcal = 48 E% |
| Cremige Lachs-Pasta | 58 g KH bei 627 kcal = 37 E% |
| Cremige Linsen-Pasta - Vegan | 67 g KH bei 623 kcal = 43 E% |
| Cremige Pasta mit Lauch und Tomate - Vegan | 55 g KH bei 484 kcal = 45 E% |
| Crispy Hot Honey Chicken Bowl | 59 g KH bei 575 kcal = 41 E% |
| Curry-Reis-Pfanne mit Karotte, Zucchini und Rinderhack | 63 g KH bei 652 kcal = 39 E% |
| Erbsen-Schinken-Nudeln | 70 g KH bei 529 kcal = 53 E% |
| Erdnuss-Dattel-Riegel nach Snickers Art | 11 g KH bei 284 kcal = 15 E% |
| Feta-Nudelpfanne mit Putensteak | 64 g KH bei 666 kcal = 38 E% |
| Fitness-Bananenbrot | 24 g KH bei 255 kcal = 38 E% |
| Fladenbrot mit Tofu und Gemüse | 79 g KH bei 595 kcal = 53 E% |
| Fruchtzwerge Shake (Banane) | 44 g KH bei 446 kcal = 39 E% |
| Gebratener Reis mit Gemüse | 63 g KH bei 487 kcal = 52 E% |
| Gefüllte Halloween Paprika - Vegan | 61 g KH bei 597 kcal = 41 E% |
| Gefüllte Halloween Paprika mit Hähnchen | 46 g KH bei 572 kcal = 32 E% |
| Gefüllte Paprika mit Champignons und Reis | 70 g KH bei 748 kcal = 37 E% |
| Gefüllte Zucchini mit Hackfleisch und Reis | 75 g KH bei 751 kcal = 40 E% |
| Gefüllte Zucchini mit Linsenbratlingen | 73 g KH bei 647 kcal = 45 E% |
| Gefüllte Zucchini mit Veganem Hackfleisch und Reis | 85 g KH bei 659 kcal = 52 E% |
| Gelbes Curry | 96 g KH bei 818 kcal = 47 E% |
| Gemüse-Hirse-Pfanne mit Hähnchen | 70 g KH bei 552 kcal = 51 E% |
| Gemüse-Linsen-Kokos Pfanne | 88 g KH bei 686 kcal = 51 E% |
| Gemüse-Quinoa-One Pot mit Kalbsleber | 69 g KH bei 557 kcal = 50 E% |
| Glasnudelsalat mit Tempeh | 70 g KH bei 609 kcal = 46 E% |
| Gnocchi mit Tomaten und Mozzarella | 47 g KH bei 361 kcal = 52 E% |
| Gnocchi Pfanne mit Rucola und Feta | 65 g KH bei 669 kcal = 39 E% |
| Gnocchi-Pfanne mit Lachs und Tomate | 96 g KH bei 778 kcal = 49 E% |
| Gnocchi-Pfanne mit Rucola, Feta und Vegan Chicken | 65 g KH bei 721 kcal = 36 E% |
| Green Goddess Pasta | 72 g KH bei 552 kcal = 52 E% |
| Gyrospfanne mit Kartoffeln | 41 g KH bei 482 kcal = 34 E% |
| Hackfleisch-Reis-Pfanne mit Brokkoli | 67 g KH bei 659 kcal = 41 E% |
| Haferflocken-Bananen-Pancakes | 65 g KH bei 584 kcal = 45 E% |
| Hähnchenbrust mit Brokkoli und Süßkartoffel | 52 g KH bei 541 kcal = 38 E% |
| Hähnchenbrust mit Rotkohl und Klößen | 67 g KH bei 808 kcal = 33 E% |
| Himbeer- Bananen Nice Cream (ohne Eismaschine) | 33 g KH bei 258 kcal = 51 E% |
| Himbeer-Bananen Nice Cream (ohne Eismaschine) | 32 g KH bei 248 kcal = 52 E% |
| Himbeer-Haferflocken-Muffins | 41 g KH bei 399 kcal = 41 E% |
| Himbeer-Tiramisu | 26 g KH bei 191 kcal = 54 E% |
| Kartoffel-Spinat Bratlinge mit Joghurt-Curry-Dip | 70 g KH bei 649 kcal = 43 E% |
| Kichererbsen-Paprika-Garnelen Pfanne mit Kartoffelpüree | 83 g KH bei 627 kcal = 53 E% |
| Klassisches Bananenbrot | 19 g KH bei 182 kcal = 42 E% |
| Knusprige Kartoffelrösti mit Kräuterdip | 53 g KH bei 623 kcal = 34 E% |
| Kurkuma-Rotbarschfilet mit Karotten und Spinat | 64 g KH bei 667 kcal = 38 E% |
| Leinsamen-Haferbrot - Glutenfrei | 16 g KH bei 227 kcal = 28 E% |
| Mango Nice Cream (ohne Eismaschine) | 22 g KH bei 211 kcal = 42 E% |
| Maultaschen-Pfanne | 86 g KH bei 698 kcal = 49 E% |
| Mexikanische Wraps | 72 g KH bei 597 kcal = 48 E% |
| Muschelnudeln mit Erbsen-Joghurt-Sauce und Feta-Krümel | 86 g KH bei 687 kcal = 50 E% |
| Nudel-Hackfleisch-Pfanne mit Paprika und Zucchini | 71 g KH bei 604 kcal = 47 E% |
| Ofen-Kartoffel mit Kräuterquark | 42 g KH bei 490 kcal = 34 E% |
| Ofen-Pasta mit Garnelen und Feta | 50 g KH bei 635 kcal = 31 E% |
| Orangen Chicken Curry - Vegan | 70 g KH bei 622 kcal = 45 E% |
| Orientalisches Müsli | 61 g KH bei 466 kcal = 52 E% |
| Orientalisches Müsli  - Vegan | 54 g KH bei 408 kcal = 53 E% |
| Overnight-Oats | 32 g KH bei 264 kcal = 48 E% |
| Pancakes - Glutenfrei | 61 g KH bei 517 kcal = 47 E% |
| Panini mit Putenbrust und Mozzarella | 19 g KH bei 187 kcal = 41 E% |
| Paprika-Tomate-Hirse Pfanne mit Feta | 69 g KH bei 750 kcal = 37 E% |
| Pasta mit Gemüse-Tomaten-Sugo | 108 g KH bei 796 kcal = 54 E% |
| Pilz-Karotte-Tofu Reispfanne | 79 g KH bei 610 kcal = 52 E% |
| Porridge mit Banane und Walnüssen | 48 g KH bei 368 kcal = 52 E% |
| Poulet Yassa (Senegalesisches Zitronenhähnchen) | 57 g KH bei 859 kcal = 27 E% |
| Pulled Chicken Pfanne mit Edamame, Feta und Reis | 42 g KH bei 372 kcal = 45 E% |
| Puten-Streifen in Zucchini-Lauch-Gemüse und Hokkaido | 81 g KH bei 617 kcal = 53 E% |
| Quark-Haferflocken Brötchen | 35 g KH bei 294 kcal = 48 E% |
| Quark-Haferflocken Brötchen mit Käse | 35 g KH bei 392 kcal = 36 E% |
| Quark-Haferflocken Brötchen mit Schinken | 35 g KH bei 355 kcal = 39 E% |
| Quinoa-Bananen-Porridge | 42 g KH bei 343 kcal = 49 E% |
| Quinoa-Bowl mit Spinat, Avocado und Ei | 55 g KH bei 517 kcal = 43 E% |
| Quinoa-Gemüse-Pfanne mit Garnelen | 76 g KH bei 566 kcal = 54 E% |
| Quinoa-Gemüse-Pfanne mit Hähnchenbrust | 88 g KH bei 674 kcal = 52 E% |
| Quinoa-Hackfleisch-Pfanne mit Paprikastreifen und Joghurt-Topping | 93 g KH bei 835 kcal = 45 E% |
| Quinoa-Salat Mexican Style | 83 g KH bei 774 kcal = 43 E% |
| Quinoa-Salat Mexican Style - Vegan | 96 g KH bei 780 kcal = 49 E% |
| Rainbow Bowl | 115 g KH bei 888 kcal = 52 E% |
| Reis-Süßkartoffel-Kokos-Curry mit Tofu | 92 g KH bei 701 kcal = 52 E% |
| Reisnudelbowl mit Gemüse und gebackenem Tofu | 97 g KH bei 706 kcal = 55 E% |
| Reispfanne mit Tempeh in Erdnusssauce | 83 g KH bei 784 kcal = 42 E% |
| Risoni mit Gemüse und Thunfisch-Tomatensauce | 62 g KH bei 472 kcal = 53 E% |
| Schnelle Gemüse-Reispfanne mit Ei | 76 g KH bei 585 kcal = 52 E% |
| Schnelle Hühner-Nudelsuppe | 56 g KH bei 424 kcal = 53 E% |
| Schoko-Bananen-Porridge | 31 g KH bei 262 kcal = 47 E% |
| Schoko-Bananen-Porridge - Vegan | 33 g KH bei 339 kcal = 39 E% |
| Selfmade Knusper-Müsli-Bowl | 56 g KH bei 481 kcal = 47 E% |
| Shakshuka mit Spinat und Kichererbsen | 57 g KH bei 651 kcal = 35 E% |
| Skyr-Schokobrötchen | 42 g KH bei 314 kcal = 54 E% |
| Sommerrollen #Vegetarisch | 50 g KH bei 458 kcal = 44 E% |
| Sommerrollen mit Hühnchen | 49 g KH bei 470 kcal = 42 E% |
| Spaghetti Bolognese | 81 g KH bei 708 kcal = 46 E% |
| Spaghetti Carbonara | 72 g KH bei 588 kcal = 49 E% |
| Spaghetti Carbonara - Vegan | 65 g KH bei 661 kcal = 39 E% |
| Spaghetti mit Teriyaki-Soja-Schnetzel | 98 g KH bei 722 kcal = 54 E% |
| Spekulatius-Dessert im Glas | 56 g KH bei 595 kcal = 38 E% |
| Spicy Red Curry Nudelsalat mit Hähnchenbrustfilet | 61 g KH bei 491 kcal = 50 E% |
| Spicy Red Curry Nudelsalat mit Tofu | 63 g KH bei 490 kcal = 51 E% |
| Spicy Red Curry Reissalat mit Garnelen | 63 g KH bei 482 kcal = 52 E% |
| Spicy Red Curry Reissalat mit Hähnchenbrustfilet | 62 g KH bei 527 kcal = 47 E% |
| Spicy Red Curry Reissalat mit Tofu | 64 g KH bei 550 kcal = 47 E% |
| Spinat-Feta-Lasagne | 40 g KH bei 368 kcal = 43 E% |
| Süßkartoffel-Hack-Auflauf | 44 g KH bei 555 kcal = 32 E% |
| Süßkartoffel-Hack-Auflauf - Vegan | 49 g KH bei 373 kcal = 53 E% |
| Süßkartoffel-Linsen-Curry Eintopf | 117 g KH bei 979 kcal = 48 E% |
| Süßkartoffel-Rosenkohl-Linsen Pfanne mit Hähnchenbrust | 72 g KH bei 650 kcal = 44 E% |
| Süßkartoffel-Tofu-Bowl | 69 g KH bei 660 kcal = 42 E% |
| Süßkartoffeltoast mit Avocado und Ei | 42 g KH bei 443 kcal = 38 E% |
| Taco-Reis-Pfanne mit Rinderhack | 77 g KH bei 778 kcal = 40 E% |
| Tomate-Aubergine-Reispfanne mit Kalbsgulasch | 70 g KH bei 673 kcal = 42 E% |
| Tomaten-Spaghetti mit Hackbällchen | 23 g KH bei 314 kcal = 29 E% |
| Tortellini-Auflauf mit Hirtenkäse | 69 g KH bei 559 kcal = 49 E% |
| Überbackene Enchiladas | 53 g KH bei 495 kcal = 43 E% |
| Überbackener Feta mit Linsenpasta | 61 g KH bei 601 kcal = 41 E% |
| Überbackener Feta mit Pasta | 77 g KH bei 597 kcal = 52 E% |
| Überbackenes Putenschnitzel mit Reis | 60 g KH bei 621 kcal = 39 E% |
| Vegan Green Smoothie-Bowl | 66 g KH bei 490 kcal = 54 E% |
| Vegetarische Hähnchenbrust mit Rotkohl und Klößen | 70 g KH bei 642 kcal = 44 E% |
| Very Berry Smoothie Bowl | 63 g KH bei 489 kcal = 52 E% |
| Wok-Nudeln mit Tofu | 68 g KH bei 551 kcal = 49 E% |
| Wrap mit gebratenem Gemüse und Kichererbsen | 56 g KH bei 433 kcal = 52 E% |
| Würzige Rindfleischpfanne mit Paprika und Süßkartoffel | 67 g KH bei 544 kcal = 49 E% |
| Würziger Tomatenreis mit Fetakäse | 56 g KH bei 522 kcal = 43 E% |
| Zimtschnecken-Bananenbrot | 19 g KH bei 201 kcal = 38 E% |
| Zoats | 55 g KH bei 423 kcal = 52 E% |

</details>

---

## D — Nährwerte

### D1 · Gegenrechnung Rezept gegen Zutatensumme: **keine Abweichung über 15 %**

Für alle 497 Rezepte stimmen `kcal`, `eiweiss`, `kohlenhydrate` und `fett` je Portion mit der
Summe der Zutatenzeilen überein. Das ist zu erwarten, wenn die Rezeptwerte aus denselben
Zeilen berechnet wurden — die Gegenrechnung bestätigt also die Rechenkette, nicht die
Richtigkeit der einzelnen Zutatenwerte. **Das eigentliche Restrisiko liegt in den Zeilen**,
deshalb die beiden folgenden Prüfungen.

Verworfen habe ich dabei Treffer unter 3 g bzw. 20 kcal Absolutdifferenz: bei ganzzahlig
gespeicherten Werten erzeugt „2 vs. 2 g" sonst 19 % Abweichung. Mit dieser Grenze bleibt nichts übrig.

### D2 · kcal passen nicht zu den Makros (Rezeptebene) — 4

Durchweg Getränke mit sehr kleinen Absolutwerten — 4/4/9 kcal je Gramm greift dort nicht sauber, weil Ballaststoffe und Zuckeralkohole eigene Brennwerte haben. Eher Rundung als Fehler.

| Rezept | Rechnung |
|---|---|
| Ingwer-Limette-Gurke Refresher | 25 kcal angegeben, Makros ergeben 16 kcal (-36 %) |
| Kurkuma-Zitrone-Ingwer Shot | 63 kcal angegeben, Makros ergeben 45 kcal (-29 %) |
| Rhabarber-Beeren Zero Schorle | 37 kcal angegeben, Makros ergeben 20 kcal (-46 %) |
| Zitrone-Minze Zero Erfrischungsgetränk | 8 kcal angegeben, Makros ergeben 4 kcal (-50 %) |

### D3 · Zutatenzeile: Makros ergeben mehr kcal als eingetragen — 2

Geprüft wurde nur der Überschuss: ein Minus erklären Ballaststoffe und Zuckeralkohole (Erythrit 0 kcal/g, Xylit 2,4 statt 4), ein Plus nicht. Übrig bleiben zwei Zeilen zum selben Lebensmittel — grüner Spargel hat rund 20 kcal/100 g, die eingetragenen Makros passen dazu nicht.

| Rezept | Befund |
|---|---|
| Grüner Spargel mit Hähnchen und Curry | Grüner Spargel: 44 kcal, Makros ergeben 64 kcal (+45 %) |
| Quinoasalat mit grünem Spargel, Kichererbsen und Walnüssen | Grüner Spargel: 33 kcal, Makros ergeben 47 kcal (+42 %) |

---

## Was das für die Veröffentlichung heißt

Keines der 497 Rezepte ist heute veröffentlichungsreif, weil **B1 (`kategorie` leer) alle 497**
betrifft und die drei Freigabe-Prüfungen aus `CLAUDE.md` bei allen scheitern
(`status = neu` bei 497, `zeit_gesamt = 0` bei 11, Tag-Widersprüche bei 40).

Der kürzeste Weg zu einem ersten veröffentlichbaren Schwung:

1. **A1–A5** abarbeiten (118 verschiedene Rezepte) — das sind die Fehler, die als falsche
   Aussage nach außen gehen. Die 40 Tag-Widersprüche zuerst, sie sind die kürzeste Liste mit
   der größten Außenwirkung.
2. **B1** klären: Rubrik für alle 497 setzen, oder den Fallback in `build-rezepte.py:154` von
   „stillschweigend Hauptgericht" auf einen harten Abbruch umstellen, damit so etwas nicht mehr
   unbemerkt durchläuft.
3. **C** erst danach, und bei High-Carb zuerst die Schwelle festlegen.
4. **B6**: den Dubletten-Datensatz `r5ywxnobwwz1n6k` prüfen, bevor irgendein Slug vergeben wird.

Ich habe nichts geschrieben — weder in PocketBase noch im Repo.
