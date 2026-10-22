#!/usr/bin/env python3
"""Erzeugt die Rezeptseiten aus PocketBase.

Einzige Quelle der Wahrheit ist pb.ascensus.fit. Die Dateinamen stammen aus
tools/slug-map.json, damit bestehende URLs stabil bleiben.

  python3 tools/build-rezepte.py            # alle Seiten neu bauen
  python3 tools/build-rezepte.py --check    # nur melden, was sich aendern wuerde

Authentifizierung: PB_TOKEN als Umgebungsvariable, oder ein Proxy, der den
Authorization-Header selbst setzt.

Englische Fassung: zu jedem Rezept entsteht rezept-<slug>-en.html, sofern
tools/rezepte-en.json es kennt. Die Datei liefert nur Woerter (Name, Schritte,
Zutaten-, Einheiten-, Tag- und Allergen-Woerterbuch); Zahlen, Fotos und die
Zuordnung kommen weiter aus PocketBase. Fehlt eine Uebersetzung, wird die
englische Seite NICHT geschrieben und der Lauf meldet es am Ende.
"""
import json, os, re, sys, html as H, urllib.request
from pathlib import Path

PB   = "https://pb.ascensus.fit/api/collections"
ROOT = Path(__file__).resolve().parent.parent
SITE = "https://ascensus.fit"

# Aus welchen Tags die beiden Badges gewaehlt werden - erste Treffer gewinnen.
TAG_PRIO = ["Vegan","Vegetarisch","Fisch",
            "High-Protein","Low-Carb","High-Carb","Ballaststoffreich","Kalorienarm",
            "Glutenfrei","Laktosefrei","Zuckerfrei",
            "Pasta","Salat","One Pot","Mealprep","Post Workout","Pre Workout",
            "Schnell und einfach","Suess","Herzhaft"]
# Grundrezepte, die als Zutat auftauchen und verlinkt werden sollen
GRUNDREZEPTE = {"Béchamelsauce": "rezept-bechamelsauce",
                "Tomaten-Gemüse-Sauce": "rezept-tomaten-gemuese-sauce"}

# Tag-Namen, die in der DB ohne Umlaute gespeichert sind
TAG_ANZEIGE = {"Fruehstueck": "Frühstück", "Suess": "Süß"}
# Oberhalb dieser Grenze zeigt die Seite gar keine Zeit mehr an.
ZEIT_GRENZE = 60

# Rubrik-Anzeige: die DB speichert Slugs ohne Umlaute.
# Mittag und Abendessen werden nicht mehr unterschieden und zeigen beide
# "Hauptgericht"; kaeme die Unterscheidung zurueck, sind das hier zwei Zeilen.
KATEGORIE = {"Fruehstueck":"Frühstück","Hauptgericht":"Hauptgericht",
             "Mittag":"Hauptgericht","Abendessen":"Hauptgericht",
             "Snack":"Snack & Süßes","Nachtisch":"Snack & Süßes","Grundrezept":"Grundrezept",
             "Vor dem Training":"Vor dem Training",
             "Nach dem Training":"Nach dem Training"}

# ---------------------------------------------------------------- Englisch
EN_DATEI = ROOT / "tools" / "rezepte-en.json"
EN = json.loads(EN_DATEI.read_text(encoding="utf-8")) if EN_DATEI.exists() else {}
GRUNDREZEPTE_EN = {"Béchamel sauce": "rezept-bechamelsauce",
                   "Tomato and vegetable sauce": "rezept-tomaten-gemuese-sauce"}

class FehlendeUebersetzung(Exception):
    pass

def en_num(x):
    """Zahl englisch formatieren: 541.1 -> 541.1 und 519.0 -> 519"""
    f = float(x)
    return str(int(round(f))) if abs(f - round(f)) < 0.05 else f"{f:.1f}"

def wb(name, de_wort):
    """Wort im Woerterbuch `name` nachschlagen; fehlt es, ist die Seite unvollstaendig."""
    try:
        return EN[name][de_wort]
    except KeyError:
        raise FehlendeUebersetzung(f"{name}: {de_wort!r}")

def api(path):
    r = urllib.request.Request(f"{PB}/{path}")
    if os.environ.get("PB_TOKEN"):
        r.add_header("Authorization", os.environ["PB_TOKEN"])
    with urllib.request.urlopen(r, timeout=60) as resp:
        return json.load(resp)

def all_records(coll, flt=""):
    out, page = [], 1
    while True:
        q = f"{coll}/records?perPage=500&page={page}" + (f"&filter=({flt})" if flt else "")
        d = api(q); out += d["items"]
        if page >= d["totalPages"]: break
        page += 1
    return out

def de(x):
    """Zahl deutsch formatieren: 541.1 -> 541,1 und 519.0 -> 519"""
    f = float(x)
    return str(int(round(f))) if abs(f - round(f)) < 0.05 else f"{f:.1f}".replace(".", ",")

def esc(s): return H.escape(str(s), quote=True)

LINK = ('<a href="{slug}.html" style="color: var(--olive); text-decoration: underline; '
        'text-underline-offset: 2px;">{text}</a>')

def verlinkt(text):
    """Nennungen eines Grundrezepts in Fliesstext zu Links machen."""
    out = esc(text)
    for name, slug in GRUNDREZEPTE.items():
        out = out.replace(esc(name), LINK.format(slug=slug, text=esc(name)))
    return out

def menge_text(z):
    if not z["menge"]:
        return esc(z["einheit"]) if z["einheit"] else "nach Geschmack"
    m = de(z["menge"])
    return f'{m} {esc(z["einheit"])}'.strip()

def iso_dauer(minuten):
    return f"PT{int(minuten)}M" if minuten else None

def zeit_anzeigen(r):
    """Angezeigt wird nur die Zubereitungszeit, und nur bis 60 Minuten.

    Alles darueber schreckt eher ab, als dass es hilft - solche Rezepte laufen
    ohne Zeitangabe. 0 heisst in der DB 'nicht erfasst'."""
    z = r["zeit_zubereitung"]
    return int(z) if z and 0 < z <= ZEIT_GRENZE else None

def baue(r, zutaten, schritte, tagname, slug, en_da=False):
    kcal, ew = de(r["kcal"]), de(r["eiweiss"])
    kh, fett = de(r["kohlenhydrate"]), de(r["fett"])
    titel = esc(r["name"])
    makros = f'{kcal} kcal · {ew} g Eiweiß · {kh} g Kohlenhydrate · {fett} g Fett pro Portion'
    lead   = makros
    beschreibung = (f'{r["name"]} – {kcal} kcal, {ew} g Eiweiß, {kh} g Kohlenhydrate, '
                    f'{fett} g Fett pro Portion.')
    zeit = zeit_anzeigen(r)

    badges = []
    if zeit:
        badges.append(f'{zeit} Min.')
    sichtbar = set(tagname)
    if "Vegan" in sichtbar:          # vegan impliziert vegetarisch
        sichtbar.discard("Vegetarisch")
    gewaehlt = [t for t in TAG_PRIO if t in sichtbar]
    badges += gewaehlt[:2]
    badges_html = "\n".join(f'        <span class="badge">{esc(TAG_ANZEIGE.get(b, b))}</span>' for b in badges)

    kurz = []
    if zeit:
        kurz.append(f'<span><strong>{zeit}</strong> Min. Zubereitung</span>')
    kurz.append(f'<span><strong>{kcal}</strong> kcal / Portion</span>')

    zut_html = "\n".join(
        f'        <li><span>{esc(z["zutat"])}</span>'
        f'<span class="menge"'
        + (f' data-menge="{de(z["menge"])}" data-einheit="{esc(z["einheit"])}"' if z["menge"] else "")
        + f'>{menge_text(z)}</span></li>' for z in zutaten)
    sch_html = "\n".join(f'        <li>{verlinkt(s["anweisung"])}</li>' for s in schritte)
    allerg = (f'<p class="allergene"><strong>Allergene:</strong> {esc(r["allergene"])}</p>'
              if (r["allergene"] or "").strip() else "")

    # Ohne eigenes Foto bleibt das Logo als Vorschaubild - sonst laeuft og:image ins Leere
    hat_og = (ROOT / f"{slug}-og.png").exists()
    og = f"{SITE}/{slug}-og.png" if hat_og else f"{SITE}/logo-wordmark-claim.png"

    ld = {"@context":"https://schema.org","@type":"Recipe","name":r["name"],
          "description":beschreibung,
          **({"image": f"{SITE}/{slug}-og.png"} if hat_og else {}),
          "recipeYield":f'{r["portionen"]} Portionen',
          "recipeCategory":KATEGORIE.get(r["kategorie"], r["kategorie"]),
          "keywords":", ".join(sorted(TAG_ANZEIGE.get(t, t) for t in tagname)),
          "recipeIngredient":[f'{menge_text(z)} {z["zutat"]}'.strip() for z in zutaten],
          "recipeInstructions":[{"@type":"HowToStep","position":s["nummer"],
                                 "text":s["anweisung"]} for s in schritte],
          "nutrition":{"@type":"NutritionInformation","servingSize":"1 Portion",
                       "calories":f'{kcal} kcal',"proteinContent":f'{ew} g',
                       "carbohydrateContent":f'{de(r["kohlenhydrate"])} g',
                       "fatContent":f'{de(r["fett"])} g',
                       "fiberContent":f'{de(r["ballaststoffe"])} g'},
          "author":{"@type":"Person","name":"Patrick Spengler"},
          "publisher":{"@type":"Organization","name":"ASCENSUS",
                       "logo":{"@type":"ImageObject","url":f"{SITE}/logo-wordmark.png"}}}
    # Nur auszeichnen, was die Seite auch zeigt - sonst widerspricht das
    # Suchergebnis der Seite selbst.
    if zeit:
        ld["prepTime"] = iso_dauer(zeit)

    bild = (f'<div class="rezept-bild">\n      <img src="{SITE}/{slug}.jpg" alt="{titel}" '
            f'width="1200" height="900" loading="lazy">\n    </div>'
            if (ROOT / f"{slug}.jpg").exists() else "")
    t = (ROOT / "tools" / "rezept-template.html").read_text(encoding="utf-8")
    for k, v in {"TITLE":titel, "DESC":esc(beschreibung), "LEAD":esc(lead), "SLUG":slug,
                 "KATEGORIE":esc(KATEGORIE.get(r["kategorie"], r["kategorie"])),
                 "BADGES":badges_html, "KURZINFO":"\n      ".join(kurz),
                 "PORTIONEN":str(r["portionen"]), "ZUTATEN":zut_html,
                 "SCHRITTE":sch_html, "ALLERGENE":allerg, "BILD":bild, "OGIMAGE":og,
                 "HREFLANG":hreflang_html(slug) if en_da else "",
                 "LANGSWITCH":schalter_html("de", slug) if en_da else "",
                 "JSONLD":json.dumps(ld, ensure_ascii=False, indent=2)}.items():
        t = t.replace("{{%s}}" % k, v)
    return t

def hreflang_html(slug):
    return (f'\n  <link rel="alternate" hreflang="de" href="{SITE}/{slug}.html">'
            f'\n  <link rel="alternate" hreflang="en" href="{SITE}/{slug}-en.html">'
            f'\n  <link rel="alternate" hreflang="x-default" href="{SITE}/{slug}.html">')

def schalter_html(aktuell, slug):
    """DE | EN oben rechts - gleiches Markup wie auf den uebrigen Seiten."""
    if aktuell == "de":
        inner = ('<span aria-current="true">DE</span><span aria-hidden="true">·</span>'
                 f'<a href="{SITE}/{slug}-en.html" hreflang="en" lang="en" aria-label="Read this page in English">EN</a>')
    else:
        inner = (f'<a href="{SITE}/{slug}.html" hreflang="de" lang="de" aria-label="Diese Seite auf Deutsch lesen">DE</a>'
                 '<span aria-hidden="true">·</span><span aria-current="true">EN</span>')
    return f'<div class="asc-lang" role="group" aria-label="Language / Sprache">{inner}</div>\n      '

# Statische Texte der Seitenvorlage. Jedes Paar muss in der Vorlage vorkommen -
# sonst bricht der Lauf ab und niemand merkt erst auf der Seite, dass etwas fehlt.
TEMPLATE_EN = [
 ('<html lang="de">', '<html lang="en">'),
 ('{{TITLE}} – ASCENSUS Rezepte</title>', '{{TITLE}} – ASCENSUS Recipes</title>'),
 ('aria-label="ASCENSUS Startseite"', 'aria-label="ASCENSUS home"'),
 ('aria-label="Hauptnavigation"', 'aria-label="Main navigation"'),
 ('#ansatz">Ansatz</a>', '#ansatz">Approach</a>'), ('#ablauf">Ablauf</a>', '#ablauf">Process</a>'),
 ('pakete.html">Pakete</a>', 'pakete.html">Packages</a>'), ('wissen.html">Wissen</a>', 'wissen.html">Knowledge</a>'),
 ('rezepte.html">Rezepte</a>\n      <a class="asc-navlink" href="https://ascensus.fit/index.html#faq">FAQ</a>',
  'rezepte.html">Recipes</a>\n      <a class="asc-navlink" href="https://ascensus.fit/index.html#faq">FAQ</a>'),
 ('#kontakt">Kontakt</a>', '#kontakt">Contact</a>'),
 ('>Kostenloses Erstgespräch</a>', '>Free intro call</a>'),
 ('rel="noopener">Erstgespräch</a>\n      {{LANGSWITCH}}', 'rel="noopener">Intro call</a>\n      {{LANGSWITCH}}'),
 ('aria-label="Menü öffnen"', 'aria-label="Open menu"'),
 ('>← Rezepte</a>', '>← Recipes</a>'),
 ('aria-label="Weniger Portionen"', 'aria-label="Fewer servings"'),
 ('aria-label="Anzahl Portionen"', 'aria-label="Number of servings"'),
 ('<span>Portionen</span>', '<span>servings</span>'),
 ('aria-label="Mehr Portionen"', 'aria-label="More servings"'),
 ('<h2>Zutaten</h2>', '<h2>Ingredients</h2>'), ('<h2>Zubereitung</h2>', '<h2>Method</h2>'),
 ('<strong>Passt das zu Deinem Alltag?</strong><br>In einem kostenlosen 30-minütigen Erstgespräch schauen wir gemeinsam auf Deine Ernährung — ohne Verkaufsdruck.',
  '<strong>Does this fit your everyday life?</strong><br>In a free 30-minute intro call, we look at your nutrition together — with no sales pressure.'),
 ('>Erstgespräch buchen</a>', '>Book intro call</a>'),
 ('>← Alle Rezepte</a>', '>← All recipes</a>'),
 ('Ernährungs- &amp; Laufcoaching · Frankfurt am Main', 'Nutrition &amp; running coaching · Frankfurt am Main'),
 ('Echt · Fundiert · Nachhaltig', 'Authentic · Evidence-based · Sustainable'),
 ('<h4>Kontakt</h4>', '<h4>Contact</h4>'), ('<h4>Rechtliches</h4>', '<h4>Legal</h4>'),
 ('>Impressum</a>', '>Legal notice</a>'), ('>Datenschutz</a>', '>Privacy policy</a>'),
 ('>AGB</a>', '>Terms &amp; conditions</a>'), ('>Widerruf</a>', '>Right of withdrawal</a>'),
 ('>Datenschutzeinstellungen</a>', '>Privacy settings</a>'), ('>Mitglieder-Login →</a>', '>Member login →</a>'),
 ('aria-label="Schnellzugriff"', 'aria-label="Quick access"'),
 ('rezepte.html">Rezepte</a>\n  <a href="https://ascensus.fit/wissen.html">Knowledge</a>',
  'rezepte.html">Recipes</a>\n  <a href="https://ascensus.fit/wissen.html">Knowledge</a>'),
 ('class="asc-bottombar-cta" href="https://cal.meetergo.com/ascensus/erstgesprach" target="_blank" rel="noopener">Erstgespräch</a>',
  'class="asc-bottombar-cta" href="https://cal.meetergo.com/ascensus/erstgesprach" target="_blank" rel="noopener">Intro call</a>'),
 ("newAmount.toFixed(1).replace('.', ',')", "newAmount.toFixed(1)"),
]
# Seiten, die es auf Englisch gibt: Links in der Vorlage zeigen dann auf die -en-Fassung
SEITEN_EN = "index|pakete|wissen|rezepte|impressum|datenschutz|agb|widerruf"

def template_en(t):
    for de_, en_ in TEMPLATE_EN:
        if de_ not in t:
            raise SystemExit(f"rezept-template.html: Textstelle fehlt fuer die englische Fassung: {de_[:60]!r}")
        t = t.replace(de_, en_)
    return re.sub(r'(https://ascensus\.fit/(?:%s))\.html' % SEITEN_EN, r'\1-en.html', t)

def verlinkt_en(text):
    out = esc(text)
    for name, slug in GRUNDREZEPTE_EN.items():
        out = re.sub(re.escape(esc(name)), lambda m: LINK.format(slug=slug + "-en", text=m.group(0)), out, flags=re.I)
    return out

def menge_text_en(z):
    if not z["menge"]:
        return esc(wb("einheiten", z["einheit"])) if z["einheit"] else "to taste"
    return f'{en_num(z["menge"])} {esc(wb("einheiten", z["einheit"]) if z["einheit"] else "")}'.strip()

def uebersetze(r, zutaten, schritte, tagname, slug):
    """Deutsche Datensaetze -> englische Woerter. Wirft FehlendeUebersetzung."""
    try:
        rz = EN["rezepte"][slug]
    except KeyError:
        raise FehlendeUebersetzung(f"rezepte: {slug!r}")
    if len(rz["schritte"]) != len(schritte):
        raise FehlendeUebersetzung(f"{slug}: {len(schritte)} Schritte in der DB, {len(rz['schritte'])} uebersetzt")
    zs = sorted(({**z, "zutat": wb("zutaten", z["zutat"])} for z in zutaten), key=lambda z: z["zutat"].lower())
    ss = [{**s, "anweisung": rz["schritte"][i]} for i, s in enumerate(sorted(schritte, key=lambda s: s["nummer"]))]
    allerg = ", ".join(wb("allergene", a) for a in re.split(r",\s*", r["allergene"] or "") if a.strip())
    kat = KATEGORIE.get(r["kategorie"], r["kategorie"])
    r2 = {**r, "name": rz["name"], "allergene": allerg, "kategorie_en": wb("kategorien", kat)}
    tags_en = {t: wb("tags", t) for t in tagname}
    return r2, zs, ss, tags_en

def baue_en(r, zutaten, schritte, tagname, slug):
    """Englische Rezeptseite. tagname enthaelt die DB-Namen; die Auswahl der Badges
    folgt derselben Rangfolge wie auf der deutschen Seite."""
    r2, zs, ss, tags_en = uebersetze(r, zutaten, schritte, tagname, slug)
    kcal, ew = en_num(r["kcal"]), en_num(r["eiweiss"])
    kh, fett = en_num(r["kohlenhydrate"]), en_num(r["fett"])
    titel = esc(r2["name"])
    lead = f'{kcal} kcal · {ew} g protein · {kh} g carbohydrates · {fett} g fat per serving'
    beschreibung = (f'{r2["name"]} – {kcal} kcal, {ew} g protein, {kh} g carbohydrates, '
                    f'{fett} g fat per serving.')
    zeit = zeit_anzeigen(r)
    badges = [f'{zeit} min'] if zeit else []
    sichtbar = set(tagname)
    if "Vegan" in sichtbar: sichtbar.discard("Vegetarisch")
    badges += [tags_en[t] for t in TAG_PRIO if t in sichtbar][:2]
    badges_html = "\n".join(f'        <span class="badge">{esc(b)}</span>' for b in badges)
    kurz = []
    if zeit: kurz.append(f'<span><strong>{zeit}</strong> min preparation</span>')
    kurz.append(f'<span><strong>{kcal}</strong> kcal / serving</span>')
    zut_html = "\n".join(
        f'        <li><span>{esc(z["zutat"])}</span>'
        f'<span class="menge"'
        + (f' data-menge="{en_num(z["menge"])}" data-einheit="{esc(wb("einheiten", z["einheit"]) if z["einheit"] else "")}"' if z["menge"] else "")
        + f'>{menge_text_en(z)}</span></li>' for z in zs)
    sch_html = "\n".join(f'        <li>{verlinkt_en(s["anweisung"])}</li>' for s in ss)
    allerg = (f'<p class="allergene"><strong>Allergens:</strong> {esc(r2["allergene"])}</p>'
              if r2["allergene"].strip() else "")
    hat_og = (ROOT / f"{slug}-og.png").exists()
    og = f"{SITE}/{slug}-og.png" if hat_og else f"{SITE}/logo-wordmark-claim.png"
    ld = {"@context":"https://schema.org","@type":"Recipe","name":r2["name"],"inLanguage":"en",
          "description":beschreibung,
          **({"image": f"{SITE}/{slug}-og.png"} if hat_og else {}),
          "recipeYield":f'{r["portionen"]} servings',
          "recipeCategory":r2["kategorie_en"],
          "keywords":", ".join(sorted(tags_en.values())),
          "recipeIngredient":[f'{menge_text_en(z)} {z["zutat"]}'.strip() for z in zs],
          "recipeInstructions":[{"@type":"HowToStep","position":i,"text":s["anweisung"]}
                                for i, s in enumerate(ss, 1)],
          "nutrition":{"@type":"NutritionInformation","servingSize":"1 serving",
                       "calories":f'{kcal} kcal',"proteinContent":f'{ew} g',
                       "carbohydrateContent":f'{kh} g',"fatContent":f'{fett} g',
                       "fiberContent":f'{en_num(r["ballaststoffe"])} g'},
          "author":{"@type":"Person","name":"Patrick Spengler"},
          "publisher":{"@type":"Organization","name":"ASCENSUS",
                       "logo":{"@type":"ImageObject","url":f"{SITE}/logo-wordmark.png"}}}
    if zeit: ld["prepTime"] = iso_dauer(zeit)
    bild = (f'<div class="rezept-bild">\n      <img src="{SITE}/{slug}.jpg" alt="{titel}" '
            f'width="1200" height="900" loading="lazy">\n    </div>'
            if (ROOT / f"{slug}.jpg").exists() else "")
    t = template_en((ROOT / "tools" / "rezept-template.html").read_text(encoding="utf-8"))
    for k, v in {"TITLE":titel, "DESC":esc(beschreibung), "LEAD":esc(lead), "SLUG":slug + "-en",
                 "KATEGORIE":esc(r2["kategorie_en"]), "BADGES":badges_html, "KURZINFO":"\n      ".join(kurz),
                 "PORTIONEN":str(r["portionen"]), "ZUTATEN":zut_html, "SCHRITTE":sch_html,
                 "ALLERGENE":allerg, "BILD":bild, "OGIMAGE":og,
                 "HREFLANG":hreflang_html(slug), "LANGSWITCH":schalter_html("en", slug),
                 "JSONLD":json.dumps(ld, ensure_ascii=False, indent=2)}.items():
        t = t.replace("{{%s}}" % k, v)
    return t


# Rubrik der DB -> Filterwert und Anzeigename auf rezepte.html
# Die Filterwerte muessen zu den data-filter-Knoepfen in rezepte.html passen:
# alle, fruehstueck, hauptgericht, snack, vor-dem-training. Eine Rubrik auf
# einen Wert ohne Knopf abzubilden versteckt die Kachel unter jedem Filter
# ausser "Alle" - "Nach dem Training" braucht also erst einen Knopf.
FILTER = {"Fruehstueck":("fruehstueck","Frühstück"),
          "Hauptgericht":("hauptgericht","Hauptgericht"),
          "Mittag":("hauptgericht","Hauptgericht"),
          "Abendessen":("hauptgericht","Hauptgericht"),
          "Snack":("snack","Snack & Süßes"),
          "Nachtisch":("snack","Snack & Süßes"),
          "Grundrezept":("hauptgericht","Grundrezept"),
          "Vor dem Training":("vor-dem-training","Vor dem Training"),
          "Nach dem Training":("nach-dem-training","Nach dem Training")}

def karte(r, tagname, slug, nr):
    """Eine Kachel fuer das Grid auf rezepte.html."""
    # Frueher fiel eine fehlende Rubrik still auf Hauptgericht zurueck. Da sie
    # bei 487 Datensaetzen leer ist, waere so reihenweise falsch einsortiert
    # worden, ohne dass es auffaellt.
    if r["kategorie"] not in FILTER:
        raise SystemExit(f'{slug}: kategorie ist {r["kategorie"]!r}, erwartet '
                         f'wird eine von {sorted(FILTER)}')
    filt, label = FILTER[r["kategorie"]]
    zeit = zeit_anzeigen(r)
    badges = ([f'{zeit} Min.'] if zeit else [])
    sichtbar = set(tagname)
    if "Vegan" in sichtbar: sichtbar.discard("Vegetarisch")
    badges += [t for t in TAG_PRIO if t in sichtbar][:2]
    bh = "\n".join(f'              <span class="post-badge">{esc(TAG_ANZEIGE.get(b, b))}</span>'
                   for b in badges)
    # Ohne Foto bleibt die Flaeche leer - .post-bild hat ein eigenes aspect-ratio
    # und eine Hintergrundfarbe, ein fehlendes <img> gaebe sonst ein kaputtes Bild.
    img = (f'\n            <img src="{SITE}/{slug}.jpg" alt="{esc(r["name"])}" '
           f'loading="lazy" width="600" height="450">\n          '
           if (ROOT / f"{slug}.jpg").exists() else "")
    return f"""        <!-- {nr}. {r['name']} -->
        <a class="post" data-kategorie="{filt}" href="{SITE}/{slug}.html">
          <div class="post-bild">{img}</div>
          <div class="post-body">
            <p class="post-cat">{esc(label)}</p>
            <h3>{esc(r['name'])}</h3>
            <div class="post-badges">
{bh}
            </div>
            <div class="post-foot">
              <span>{de(r['kcal'])} kcal / Portion</span>
              <span class="post-more">Ansehen →</span>
            </div>
          </div>
        </a>"""

def karte_en(r, tagname, slug, nr):
    """Kachel fuer das Grid auf rezepte-en.html (gleiche Filterwerte wie deutsch)."""
    filt, label_de = FILTER[r["kategorie"]]
    label = wb("kategorien", label_de)
    name = EN["rezepte"][slug]["name"] if slug in EN.get("rezepte", {}) else None
    if name is None:
        raise FehlendeUebersetzung(f"rezepte: {slug!r}")
    zeit = zeit_anzeigen(r)
    badges = ([f'{zeit} min'] if zeit else [])
    sichtbar = set(tagname)
    if "Vegan" in sichtbar: sichtbar.discard("Vegetarisch")
    badges += [wb("tags", t) for t in TAG_PRIO if t in sichtbar][:2]
    bh = "\n".join(f'              <span class="post-badge">{esc(b)}</span>' for b in badges)
    img = (f'\n            <img src="{SITE}/{slug}.jpg" alt="{esc(name)}" '
           f'loading="lazy" width="600" height="450">\n          '
           if (ROOT / f"{slug}.jpg").exists() else "")
    return f"""        <!-- {nr}. {name} -->
        <a class="post" data-kategorie="{filt}" href="{SITE}/{slug}-en.html">
          <div class="post-bild">{img}</div>
          <div class="post-body">
            <p class="post-cat">{esc(label)}</p>
            <h3>{esc(name)}</h3>
            <div class="post-badges">
{bh}
            </div>
            <div class="post-foot">
              <span>{en_num(r['kcal'])} kcal / serving</span>
              <span class="post-more">View →</span>
            </div>
          </div>
        </a>"""

def uebersicht(karten, name="rezepte.html", zaehl=(r"mit allen \d+ Rezepten", "mit allen {n} Rezepten")):
    """Grid in rezepte.html ersetzen und den Consent-Block ergaenzen, falls er fehlt."""
    f = ROOT / name
    h = f.read_text(encoding="utf-8")
    neu = ('<div class="post-grid" id="rezept-grid">\n\n' + "\n\n".join(karten)
           + '\n\n      </div>')
    # Index-Suche statt Regex: zwischen Grid-Ende und dem Leer-Absatz steht ein Kommentar
    auf = '<div class="post-grid" id="rezept-grid">'
    zu  = '<p class="post-empty"'
    a, b = h.find(auf), h.find(zu)
    if a < 0 or b < 0:
        raise SystemExit(f"{name}: Grid-Markierungen nicht gefunden")
    ende = h.rindex('</div>', a, b) + len('</div>')
    h2 = h[:a] + neu + h[ende:]
    if "klaro.js" not in h2:
        tpl = (ROOT / "tools" / "rezept-template.html").read_text(encoding="utf-8")
        block = re.search(r'<!-- Consent & Analytics -->.*?(?=<script type="application/ld\+json">)',
                          tpl, re.S).group(0)
        h2 = h2.replace("</head>", block + "</head>")
    # Muster statt Literal: sonst greift der Austausch nur solange dort 18 steht
    h2 = re.sub(zaehl[0], zaehl[1].format(n=len(karten)), h2)
    if h2 != h:
        f.write_text(h2, encoding="utf-8"); return True
    return False

def sitemap(slugs_in_reihenfolge, heute, en_slugs=()):
    """rezepte.html und alle Rezeptseiten in die sitemap.xml eintragen."""
    f = ROOT / "sitemap.xml"
    orig = f.read_text(encoding="utf-8")
    x = re.sub(r'\n*  <!-- Rezepte \(erzeugt.*?(?=\n*</urlset>)', "", orig, flags=re.S)
    eintraege = ["\n\n  <!-- Rezepte (erzeugt von tools/build-rezepte.py) -->"]
    eintraege.append(f"""
  <url>
    <loc>{SITE}/rezepte.html</loc>
    <lastmod>{heute}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>""")
    for slug in slugs_in_reihenfolge:
        eintraege.append(f"""
  <url>
    <loc>{SITE}/{slug}.html</loc>
    <lastmod>{heute}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>""")
    if en_slugs:
        eintraege.append(f"""
  <url>
    <loc>{SITE}/rezepte-en.html</loc>
    <lastmod>{heute}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>""")
        for slug in en_slugs:
            eintraege.append(f"""
  <url>
    <loc>{SITE}/{slug}-en.html</loc>
    <lastmod>{heute}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
  </url>""")
    kopf = x[:x.rindex("</urlset>")].rstrip()
    neu = kopf + "".join(eintraege) + "\n\n</urlset>\n"
    if neu == orig:
        return False
    f.write_text(neu, encoding="utf-8")
    return True

def main():
    check = "--check" in sys.argv
    slugs = json.loads((ROOT / "tools" / "slug-map.json").read_text(encoding="utf-8"))
    tags  = {t["id"]: t["name"] for t in all_records("tags")}
    zut, sch = all_records("zutaten"), all_records("schritte")
    Z, C = {}, {}
    for z in zut: Z.setdefault(z["rezept"], []).append(z)
    for s in sch: C.setdefault(s["rezept"], []).append(s)

    aufgaben = [(rid, slug, None) for rid, slug in slugs.items()]
    gr_datei = ROOT / "tools" / "grundrezepte.json"
    if gr_datei.exists():
        for g in json.loads(gr_datei.read_text(encoding="utf-8")):
            aufgaben.append((None, g["slug"], g))

    geaendert, karten, karten_en, fehlt = 0, {}, {}, []
    for rid, slug, fest in sorted(aufgaben, key=lambda t: t[1]):
        r = fest if fest else api(f"rezepte/records/{rid}")
        if fest:
            zs, ss, tn = r["zutaten"], r["schritte"], set(r["tags"])
        else:
            zs = sorted(Z.get(rid, []), key=lambda z: z["zutat"].lower())
            ss = sorted(C.get(rid, []), key=lambda s: s["nummer"])
            tn = {tags.get(t) for t in r["tags"]} - {None}
        try:
            seite_en = baue_en(r, zs, ss, tn, slug) if EN else None
            if seite_en and not fest: karten_en[slug] = karte_en(r, tn, slug, 0)
        except FehlendeUebersetzung as e:
            seite_en = None
            fehlt.append((slug, str(e)))
        neu = baue(r, zs, ss, tn, slug, en_da=seite_en is not None)
        if not fest:                      # Grundrezepte stehen nicht im Grid
            karten[slug] = karte(r, tn, slug, 0)
        for datei, inhalt, marke in ((f"{slug}.html", neu, ""), (f"{slug}-en.html", seite_en, " EN")):
            if inhalt is None: continue
            ziel = ROOT / datei
            alt = ziel.read_text(encoding="utf-8") if ziel.exists() else ""
            if alt == inhalt:
                print(f"  =  {datei[:-5]}")
            else:
                geaendert += 1
                print(f"  {'~' if check else '>'}  {datei[:-5]}")
                if not check: ziel.write_text(inhalt, encoding="utf-8")
    print(f"\n{geaendert} Seiten "
          + ("wuerden sich aendern" if check else "neu geschrieben"))
    if fehlt:
        print(f"\nOHNE ENGLISCHE FASSUNG ({len(fehlt)}) - Uebersetzung in tools/rezepte-en.json ergaenzen:")
        for slug, grund in fehlt: print(f"  !  {slug}: fehlt {grund}")

    if not check and karten:
        reihenfolge = json.loads((ROOT / "tools" / "reihenfolge.json").read_text(encoding="utf-8"))
        def ordnen(k):
            g = [k[s] for s in reihenfolge if s in k] + [x for s, x in sorted(k.items()) if s not in reihenfolge]
            return [re.sub(r"<!-- \d+\.", f"<!-- {i+1}.", x, count=1) for i, x in enumerate(g)]
        print("rezepte.html:", "aktualisiert" if uebersicht(ordnen(karten)) else "unveraendert")
        if karten_en and (ROOT / "rezepte-en.html").exists():
            print("rezepte-en.html:", "aktualisiert" if uebersicht(
                ordnen(karten_en), "rezepte-en.html", (r"with all \d+ recipes", "with all {n} recipes")) else "unveraendert")
        grund = sorted(g["slug"] for g in json.loads(
            (ROOT / "tools" / "grundrezepte.json").read_text(encoding="utf-8")))
        alle_slugs = [s for s in reihenfolge if s in karten] + \
                     sorted(s for s in karten if s not in reihenfolge) + grund
        en_slugs = [s for s in alle_slugs if (ROOT / f"{s}-en.html").exists()]
        heute = __import__("datetime").date.today().isoformat()
        print("sitemap.xml: ", "aktualisiert" if sitemap(alle_slugs, heute, en_slugs) else "unveraendert")
    if fehlt:
        sys.exit(2)

if __name__ == "__main__":
    main()
