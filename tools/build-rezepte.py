#!/usr/bin/env python3
"""Erzeugt die Rezeptseiten aus PocketBase.

Einzige Quelle der Wahrheit ist pb.ascensus.fit. Die Dateinamen stammen aus
tools/slug-map.json, damit bestehende URLs stabil bleiben.

  python3 tools/build-rezepte.py            # alle Seiten neu bauen
  python3 tools/build-rezepte.py --check    # nur melden, was sich aendern wuerde

Authentifizierung: PB_TOKEN als Umgebungsvariable, oder ein Proxy, der den
Authorization-Header selbst setzt.
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
# Rubrik-Anzeige: die DB speichert Slugs ohne Umlaute.
# Mittag und Abendessen werden nicht mehr unterschieden und zeigen beide
# "Hauptgericht"; kaeme die Unterscheidung zurueck, sind das hier zwei Zeilen.
KATEGORIE = {"Fruehstueck":"Frühstück","Hauptgericht":"Hauptgericht",
             "Mittag":"Hauptgericht","Abendessen":"Hauptgericht",
             "Snack":"Snack","Nachtisch":"Nachtisch","Grundrezept":"Grundrezept",
             "Vor dem Training":"Vor dem Training",
             "Nach dem Training":"Nach dem Training"}

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

def baue(r, zutaten, schritte, tagname, slug):
    kcal, ew = de(r["kcal"]), de(r["eiweiss"])
    titel = esc(r["name"])
    lead  = f'{r["name"]} – ein Rezept von ASCENSUS. {kcal} kcal, {ew} g Eiweiß pro Portion.'

    badges = []
    if r["zeit_gesamt"]:
        badges.append(f'{int(r["zeit_gesamt"])} Min.')
    sichtbar = set(tagname)
    if "Vegan" in sichtbar:          # vegan impliziert vegetarisch
        sichtbar.discard("Vegetarisch")
    gewaehlt = [t for t in TAG_PRIO if t in sichtbar]
    badges += gewaehlt[:2]
    badges_html = "\n".join(f'        <span class="badge">{esc(TAG_ANZEIGE.get(b, b))}</span>' for b in badges)

    kurz = []
    if r["zeit_zubereitung"]:
        kurz.append(f'<span><strong>{int(r["zeit_zubereitung"])}</strong> Min. Zubereitung</span>')
    if r["zeit_gesamt"]:
        kurz.append(f'<span><strong>{int(r["zeit_gesamt"])}</strong> Min. gesamt</span>')
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
          "description":lead,
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
    if iso_dauer(r["zeit_gesamt"]):       ld["totalTime"] = iso_dauer(r["zeit_gesamt"])
    if iso_dauer(r["zeit_zubereitung"]):  ld["prepTime"]  = iso_dauer(r["zeit_zubereitung"])

    bild = (f'<div class="rezept-bild">\n      <img src="{SITE}/{slug}.jpg" alt="{titel}" '
            f'width="1200" height="900" loading="lazy">\n    </div>'
            if (ROOT / f"{slug}.jpg").exists() else "")
    t = (ROOT / "tools" / "rezept-template.html").read_text(encoding="utf-8")
    for k, v in {"TITLE":titel, "DESC":esc(lead), "LEAD":esc(lead), "SLUG":slug,
                 "KATEGORIE":esc(KATEGORIE.get(r["kategorie"], r["kategorie"])),
                 "BADGES":badges_html, "KURZINFO":"\n      ".join(kurz),
                 "PORTIONEN":str(r["portionen"]), "ZUTATEN":zut_html,
                 "SCHRITTE":sch_html, "ALLERGENE":allerg, "BILD":bild, "OGIMAGE":og,
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
    badges = ([f'{int(r["zeit_gesamt"])} Min.'] if r["zeit_gesamt"] else [])
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

def uebersicht(karten):
    """Grid in rezepte.html ersetzen und den Consent-Block ergaenzen, falls er fehlt."""
    f = ROOT / "rezepte.html"
    h = f.read_text(encoding="utf-8")
    neu = ('<div class="post-grid" id="rezept-grid">\n\n' + "\n\n".join(karten)
           + '\n\n      </div>')
    # Index-Suche statt Regex: zwischen Grid-Ende und dem Leer-Absatz steht ein Kommentar
    auf = '<div class="post-grid" id="rezept-grid">'
    zu  = '<p class="post-empty"'
    a, b = h.find(auf), h.find(zu)
    if a < 0 or b < 0:
        raise SystemExit("rezepte.html: Grid-Markierungen nicht gefunden")
    ende = h.rindex('</div>', a, b) + len('</div>')
    h2 = h[:a] + neu + h[ende:]
    if "klaro.js" not in h2:
        tpl = (ROOT / "tools" / "rezept-template.html").read_text(encoding="utf-8")
        block = re.search(r'<!-- Consent & Analytics -->.*?(?=<script type="application/ld\+json">)',
                          tpl, re.S).group(0)
        h2 = h2.replace("</head>", block + "</head>")
    # Muster statt Literal: sonst greift der Austausch nur solange dort 18 steht
    h2 = re.sub(r"mit allen \d+ Rezepten", f"mit allen {len(karten)} Rezepten", h2)
    if h2 != h:
        f.write_text(h2, encoding="utf-8"); return True
    return False

def sitemap(slugs_in_reihenfolge, heute):
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

    geaendert, karten = 0, {}
    for rid, slug, fest in sorted(aufgaben, key=lambda t: t[1]):
        r = fest if fest else api(f"rezepte/records/{rid}")
        if fest:
            zs, ss, tn = r["zutaten"], r["schritte"], set(r["tags"])
        else:
            zs = sorted(Z.get(rid, []), key=lambda z: z["zutat"].lower())
            ss = sorted(C.get(rid, []), key=lambda s: s["nummer"])
            tn = {tags.get(t) for t in r["tags"]} - {None}
        neu = baue(r, zs, ss, tn, slug)
        if not fest:                      # Grundrezepte stehen nicht im Grid
            karten[slug] = karte(r, tn, slug, 0)
        ziel = ROOT / f"{slug}.html"
        alt = ziel.read_text(encoding="utf-8") if ziel.exists() else ""
        if alt == neu:
            print(f"  =  {slug}")
        else:
            geaendert += 1
            print(f"  {'~' if check else '>'}  {slug}")
            if not check: ziel.write_text(neu, encoding="utf-8")
    print(f"\n{geaendert} von {len(aufgaben)} Seiten "
          + ("wuerden sich aendern" if check else "neu geschrieben"))

    if not check and karten:
        reihenfolge = json.loads((ROOT / "tools" / "reihenfolge.json").read_text(encoding="utf-8"))
        geordnet = [karten[s] for s in reihenfolge if s in karten] + \
                   [k for s, k in sorted(karten.items()) if s not in reihenfolge]
        geordnet = [re.sub(r"<!-- \d+\.", f"<!-- {i+1}.", k, count=1)
                    for i, k in enumerate(geordnet)]
        print("rezepte.html:", "aktualisiert" if uebersicht(geordnet) else "unveraendert")
        alle_slugs = [s for s in reihenfolge if s in karten] + \
                     sorted(s for s in karten if s not in reihenfolge) + \
                     sorted(g["slug"] for g in json.loads(
                         (ROOT / "tools" / "grundrezepte.json").read_text(encoding="utf-8")))
        heute = __import__("datetime").date.today().isoformat()
        print("sitemap.xml: ", "aktualisiert" if sitemap(alle_slugs, heute) else "unveraendert")

if __name__ == "__main__":
    main()
