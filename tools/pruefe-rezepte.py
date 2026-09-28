#!/usr/bin/env python3
"""Prueft die noch nicht veroeffentlichten Rezepte in PocketBase.

Geprueft werden alle rezepte-Datensaetze ausser den in tools/slug-map.json
eingetragenen, und zwar auf:

  1. Naehrwerte       Rezeptwerte gegen die Summe der Zutatenzeilen je Portion
  2. Tags             Vegan / Vegetarisch / Glutenfrei / Laktosefrei / EggFree gegen
                      die Zutatenliste, die berechneten Tags gegen die Naehrwerte
  3. Vollstaendigkeit Schritte, Zutaten, Zeiten, Mengen, Allergene, Rubrik
  4. Dubletten        gleiche Rezeptnamen

  python3 tools/pruefe-rezepte.py            # Zusammenfassung
  python3 tools/pruefe-rezepte.py --json     # vollstaendiger Befund als JSON

Authentifizierung wie beim Generator: PB_TOKEN als Umgebungsvariable, oder ein
Proxy, der den Authorization-Header selbst setzt.

Zum Datenmodell: zutaten.naehrwerte_pro_100g traegt trotz seines Namens die
absoluten Werte fuer die eingetragene Menge, nicht Werte je 100 g. Die
Gegenrechnung ist daher Summe der Zeilen geteilt durch portionen.
"""
import json, os, re, sys, collections, unicodedata, urllib.request
from pathlib import Path

PB   = "https://pb.ascensus.fit/api/collections"
ROOT = Path(__file__).resolve().parent.parent
SLUG = json.load(open(ROOT / "tools" / "slug-map.json"))

def api(path):
    r = urllib.request.Request(f"{PB}/{path}")
    if os.environ.get("PB_TOKEN"):
        r.add_header("Authorization", os.environ["PB_TOKEN"])
    with urllib.request.urlopen(r, timeout=60) as resp:
        return json.load(resp)

def all_records(coll):
    out, page = [], 1
    while True:
        d = api(f"{coll}/records?perPage=500&page={page}")
        out += d["items"]
        if page >= d["totalPages"]: break
        page += 1
    return out

rez, zut, sch, tags = (all_records(c) for c in ("rezepte", "zutaten", "schritte", "tags"))
TAG = {t["id"]: t for t in tags}
Z = collections.defaultdict(list); S = collections.defaultdict(list)
for x in zut: Z[x["rezept"]].append(x)
for x in sch: S[x["rezept"]].append(x)
UNP = [r for r in rez if r["id"] not in SLUG]

# ---------------------------------------------------------------- Naehrwerte
NW = re.compile(r"([\d.,]+)\s*g\s*K\s*/\s*([\d.,]+)\s*g\s*E\s*/\s*([\d.,]+)\s*g\s*F\s*/\s*([\d.,]+)\s*kcal", re.I)
def parse_nw(s):
    m = NW.search(s or "")
    if not m: return None
    return tuple(float(x.replace(",", ".")) for x in m.groups())   # K, E, F, kcal

def summe(zs):
    """Summe der Zutaten-Naehrwerte fuers ganze Rezept.

    Das Feld naehrwerte_pro_100g traegt trotz seines Namens die absoluten Werte
    fuer die angegebene Menge - gegen mehrere Rezepte gegengerechnet.
    -> (K,E,F,kcal), n_ohne_werte
    """
    tot = [0.0, 0.0, 0.0, 0.0]; offen = 0
    for q in zs:
        nw = parse_nw(q["naehrwerte_pro_100g"])
        if nw is None:
            offen += 1; continue
        for i in range(4): tot[i] += nw[i]
    return tot, offen

# ------------------------------------------------------------ Zutaten-Lexika
def norm(s):
    s = s.lower()
    for a, b in (("ä","ae"),("ö","oe"),("ü","ue"),("ß","ss"),("é","e"),("è","e"),("ê","e")):
        s = s.replace(a, b)
    return unicodedata.normalize("NFKD", s).encode("ascii","ignore").decode()

# Je Kategorie: AUS = Zutat ist fuer diese Kategorie unbedenklich (wird uebersprungen),
#               TREFFER = Zutat schlaegt an.
LEX = {
 "fleisch": dict(
   aus = ["vegan","veganes","vegane","like chicken","like doener","soja","tofu","tempeh","seitan",
          "huehnerei","lupinen","erbsenprotein","pflanzlich","vetain","weizen","rinderfond",
          "huehnerbruehe","gemuesebruehe"],
   tref = ["haehnchen","huehnchen","huehner","\\bhuhn","pute","truthahn","rind","kalb","schwein",
           "hackfleisch","\\bhack\\b","rinderhack","speck","bacon","schinken","cevapcici","gulasch",
           "steak","leber","doener","salami","wurst","geschnetzeltes","schnitzel","gelatine",
           "\\blamm","\\bente\\b","\\bgans","filetstueck","hackfleisch","frikadelle","poulet",
           "hueftsteak","rinderfilet","rindergulasch","bolognese \\(fleisch"]),
 "fisch": dict(
   aus = ["fischfrei","vegan"],
   tref = ["lachs","thunfisch","kabeljau","rotbarsch","forelle","\\bfisch",
           "sardelle","anchovis","hering","makrele","seelachs","surimi","sardine","dorsch",
           "zander","forellenfilet"]),
 "krebstier": dict(aus = [], tref = ["garnele","scampi","shrimp","krebs","hummer","krabbe",
                                     "frutti di mare","frutti Di mare"]),
 "weichtier": dict(aus = [], tref = ["muschel","tintenfisch","calamari","auster"]),
 "milch": dict(
   aus = ["laktosefrei","vegan","veganes","vegane","simply v","mandelmilch","mandeldrink",
          "mandel cuisine","kokosmilch","kokos drink","kokosdrink","kokos joghurt","kokosjoghurt",
          "kokosghurt","kokosjogurt","reismilch","reisdrink","hafermilch","haferdrink","sojamilch",
          "sojadrink","soja-joghurt","sojajoghurt","joghurtalternative","cashewmilch","mandeldrink",
          "kokos-mandel-milch","kokosnuss mit reis drink","erdnussbutter","erdnusscreme","erdnussmus",
          "kokosbutter","kakaobutter","kokosmus","mandelmus","cashewmus","nussmus","tahini",
          "butternut","butternuss","milchreis","butterkuerbis","kokosfett","kokosoel","kokosmehl",
          "kokosraspel","kokoschips","kokosflocken","kokoswasser","kokos natur","kokosbluete",
          "milchsaeure","buttermilch","hefe flocken","coconut spread","sojaghurt","reisprotein",
          "erbsenprotein","milch- schokostreusel"],
   tref = ["milch","kaese","quark","joghurt","jogurt","skyr","sahne","butter","feta","mozzarella",
           "mozarella","parmesan","gouda","cheddar","ricotta","mascarpone","schmand","creme fraiche",
           "ghee","whey","molke","huettenkaese","halloumi","burrata","camembert","harzer","hirtenkaese",
           "sour creme","saure sahne","cremefine","creme leicht","kefir","kondensmilch","rahm",
           "kinder bueno","kinder pingui","schokostreusel","protein pudding","milchpulver",
           "cottage cheese","creme fine","schlagsahne","frischkaese","streichkaese","reibekaese",
           "gratinkaese","gratin-kaese","pizzakaese","streukaese","kaeseaufschnitt","mini mozarella"]),
 "ei": dict(
   aus = ["eiweissbrot","eiweissriegel","eiweisspulver","vegan","veganes","eiweiss brot",
          "sojaeiweiss","weizeneiweiss","milcheiweiss"],
   tref = ["\\bei\\b","\\beier\\b","eiklar","huehnerei","eigelb","mayonnaise","\\bmayo\\b","mayo ",
           "loeffelbiskuit","biskuitmasse","eiernudeln","mit ei\\b","\\bei "]),
 "honig": dict(aus = ["kunsthonig"], tref = ["honig"]),
 # Schalenfruechte im Sinne der LMIV - Kokos und Muskat zaehlen nicht dazu
 "nuss": dict(
   aus = ["muskatnuss","kokosnuss","kokos","erdmandel","butternuss","butternut","erdnuss","erdnuesse",
          "nussmus \\(erdnuss"],
   tref = ["mandel","walnuss","walnuess","cashew","haselnuss","pistazie","macadamia","paranuss",
           "pekan","\\bnuss","\\bnuess","marzipan","hazelnut","almond","mandeln"]),
 "erdnuss": dict(aus = [], tref = ["erdnuss","erdnuess","peanut"]),
 "sesam": dict(aus = [], tref = ["sesam","tahini"]),
 "soja": dict(aus = [], tref = ["soja","tofu","tempeh","edamame","tamari","\\bmiso"]),
 "gluten": dict(
   aus = ["glutenfrei","gluten frei","tamari","mandelmehl","kokosmehl","kichererbsenmehl","reismehl",
          "leinmehl","buchweizen","linsennudeln","linsen nudeln","rote linsen","linsenwaffeln",
          "kichererbsen pasta","kichererbsenpasta","glasnudeln","reisnudeln","reispapier","maiswaffel",
          "reiswaffel","maismehl","tapiokastaerke","speisestaerke","\\bstaerke","mix b brot-mix",
          "risoni aus huelsenfruechten","gruene erbsen, penne","erbsen, penne","pasta, rote linsen",
          "pasta rote linsen","protein wrap","hirseflocken","hirse flocken","reisflocken",
          "puddingpulver","pudding pulver","tortenguss","quinoa","backpulver","mungbohnen",
          "mung dal","kokos","4 korn flocken","polenta","hirse"],
   tref = ["weizen","dinkel","roggen","gerste","hafer","seitan","couscous","bulgur","griess","panko",
           "paniermehl","semmelbroesel","nudel","pasta","spaghetti","penne","fusilli","fussili",
           "farfalle","conchiglie","tortellini","lasagne","gnocchi","orzo","kritharaki","spirelli",
           "risoni","\\bbrot","broetchen","toast","bagel","baguette","ciabatta","panini","pita",
           "fladenbrot","\\bbuns\\b","\\bbun\\b","wrap","tortilla","knoedel","mehl","muesli","granola",
           "keks","biskuit","spekulatius","salzstangen","lebkuchen","sojasauce","sojasosse",
           "soja sauce","soja sosse","cracker","maultaschen","waffel","teigwaren","malz","\\bbier\\b",
           "hartweizen","crunchy","sandwich","burger bun","lasagneblaetter","nudelplatten"]),
}
# Hafer ist von Natur aus glutenfrei, aber regelmaessig kontaminiert - eigene Klasse
HAFER = ["hafer"]

def klassifiziere(zs):
    f = {k: {} for k in LEX}
    for q in zs:
        n = norm(q["zutat"])
        for key, lex in LEX.items():
            if any(re.search(a, n) for a in lex["aus"]):
                continue
            t = [k for k in lex["tref"] if re.search(k, n)]
            if t: f[key].setdefault(q["zutat"], t[0])
    return f

# ------------------------------------------------------------------ Schwellen
SCHWELLE = {
  "High-Protein":   "Eiweiss >= 20 % der kcal (EU-Claim 'hoher Proteingehalt')",
  "Low-Carb":       "Kohlenhydrate <= 20 % der kcal",
  "High-Carb":      "Kohlenhydrate >= 55 % der kcal",
  "Kalorienarm":    "<= 400 kcal pro Portion",
  "Ballaststoffreich": "Ballaststoffe >= 3 g / 100 kcal (EU-Claim 'hoher Ballaststoffgehalt')",
  "Schnell und einfach": "zeit_gesamt <= 30 Min.",
}

befund = collections.defaultdict(list)

for r in UNP:
    rid = r["id"]; name = r["name"]
    zs = sorted(Z.get(rid, []), key=lambda q: q["created"])
    ss = S.get(rid, [])
    tn = {TAG[t]["name"] for t in r["tags"] if t in TAG}
    port = r["portionen"] or 1

    # --- 3. Vollstaendigkeit
    if not zs: befund["ohne_zutaten"].append((name, rid, ""))
    if not ss: befund["ohne_schritte"].append((name, rid, ""))
    if not r["zeit_gesamt"]: befund["zeit_null"].append((name, rid, ""))
    if not (r["kategorie"] or "").strip(): befund["ohne_kategorie"].append((name, rid, ""))
    if r["zeit_gesamt"] and r["zeit_zubereitung"] and r["zeit_zubereitung"] > r["zeit_gesamt"]:
        befund["zeit_widerspruch"].append((name, rid, f'{r["zeit_zubereitung"]} Min. Zubereitung > {r["zeit_gesamt"]} Min. gesamt'))
    nullmenge = [q for q in zs if not q["menge"] and (parse_nw(q["naehrwerte_pro_100g"]) or (0,0,0,0))[3] >= 5]
    if nullmenge:
        befund["menge_null"].append((name, rid, "; ".join(f'{q["zutat"]} ({q["einheit"] or "ohne Einheit"})' for q in nullmenge)))

    kl = klassifiziere(zs)
    allerg = norm(r["allergene"] or "")
    fehlt = []
    for key, wort, feld in (("milch","Milch","milch"), ("ei","Eier","ei"), ("nuss","Nuesse","nuss"),
                            ("erdnuss","Erdnuesse","erdnuss"), ("fisch","Fisch","fisch"),
                            ("gluten","Gluten","gluten"), ("sesam","Sesam","sesam"),
                            ("soja","Sojabohnen","soja"), ("krebstier","Krebstiere","krebstier"),
                            ("weichtier","Weichtiere","weichtier")):
        if kl[key] and norm(wort)[:5] not in allerg:
            fehlt.append(f'{wort} ({list(kl[key])[0]})')
    if fehlt:
        befund["allergen_fehlt"].append((name, rid, "; ".join(fehlt)))

    # --- 1. Naehrwerte
    tot, offen = summe(zs)
    if zs and tot[3] > 0:
        pp = [v / port for v in tot]
        ist = [r["kohlenhydrate"], r["eiweiss"], r["fett"], r["kcal"]]
        abw = []
        for lbl, i in (("kcal",3), ("Eiweiss",1), ("KH",0), ("Fett",2)):
            soll, hab = pp[i], ist[i]
            if soll < 1 and hab < 1: continue
            base = max(soll, hab, 1)
            d = (hab - soll) / base * 100
            floor = 20 if lbl == "kcal" else 3     # kcal bzw. Gramm - darunter ist es Rundung
            if abs(d) > 15 and abs(hab - soll) >= floor:
                abw.append(f'{lbl} {hab:g} vs {soll:.0f} ({d:+.0f} %)')
        if abw:
            sev = max(abs((ist[i]-pp[i])/max(pp[i],ist[i],1)*100) for i in range(4))
            befund["naehrwert_abweichung"].append((name, rid, "; ".join(abw), sev, offen))
        # Atwater-Gegenprobe auf den Rezeptwerten selbst
        atw = 4*ist[0] + 4*ist[1] + 9*ist[2]
        if ist[3] and abs(atw - ist[3]) / max(ist[3], 1) * 100 > 20:
            befund["atwater"].append((name, rid, f'{ist[3]:g} kcal angegeben, Makros ergeben {atw:.0f} kcal ({(atw-ist[3])/ist[3]*100:+.0f} %)'))
    if offen:
        befund["nw_fehlt"].append((name, rid, f'{offen} Zutat(en) ohne Naehrwerte'))

    # --- 1b. Plausibilitaet der einzelnen Zutatenzeilen
    for q in zs:
        nw = parse_nw(q["naehrwerte_pro_100g"])
        if not nw: continue
        K, E, F, kc = nw
        atw = 4*K + 4*E + 9*F
        # Nur Ueberschuss melden: ein Minus erklaeren Ballaststoffe und Zuckeralkohole,
        # ein Plus laesst sich nicht erklaeren. Suessungsmittel ganz ausklammern.
        suess = re.search("erythrit|xylit|birkenzucker|xucker|inulin|flohsamen", norm(q["zutat"]))
        if kc >= 30 and not suess and (atw - kc) / kc * 100 > 25:
            befund["zutat_atwater"].append((name, rid,
                f'{q["zutat"]}: {kc:g} kcal, Makros ergeben {atw:.0f} kcal ({(atw-kc)/kc*100:+.0f} %)'))
        if (q["einheit"] or "").strip().lower() in ("g", "ml") and q["menge"]:
            dichte = kc / q["menge"] * 100
            makro = (K + E + F) / q["menge"] * 100
            if dichte > 950:
                befund["zutat_dichte"].append((name, rid,
                    f'{q["zutat"]}: {kc:g} kcal auf {q["menge"]:g} {q["einheit"]} = {dichte:.0f} kcal/100 g'))
            elif makro > 105:
                befund["zutat_dichte"].append((name, rid,
                    f'{q["zutat"]}: {K+E+F:.0f} g Makros auf {q["menge"]:g} {q["einheit"]} = {makro:.0f} g/100 g'))

    # --- 2. Tags gegen Zutaten
    if "Vegan" in tn:
        bad = {**kl["fleisch"], **kl["fisch"], **kl["krebstier"], **kl["weichtier"],
               **kl["milch"], **kl["ei"], **kl["honig"]}
        if bad: befund["vegan_falsch"].append((name, rid, ", ".join(sorted(bad))))
    if "Vegetarisch" in tn:
        bad = {**kl["fleisch"], **kl["fisch"], **kl["krebstier"], **kl["weichtier"]}
        if bad: befund["vegetarisch_falsch"].append((name, rid, ", ".join(sorted(bad))))
    if "Glutenfrei" in tn and kl["gluten"]:
        befund["glutenfrei_falsch"].append((name, rid, ", ".join(sorted(kl["gluten"]))))
    if "Laktosefrei" in tn:
        bad = {k: v for k, v in kl["milch"].items() if "laktosefrei" not in norm(k)}
        if bad: befund["laktosefrei_falsch"].append((name, rid, ", ".join(sorted(bad))))
    if "EggFree" in tn and kl["ei"]:
        befund["eggfree_falsch"].append((name, rid, ", ".join(sorted(kl["ei"]))))
    if "Fisch" in tn and not (kl["fisch"] or kl["krebstier"] or kl["weichtier"]):
        befund["fisch_ohne_fisch"].append((name, rid, ""))
    # fehlende Vegetarisch-Auszeichnung bei Vegan
    if "Vegan" in tn and "Vegetarisch" not in tn:
        befund["vegan_ohne_vegetarisch"].append((name, rid, ""))

    # --- 2b. berechnete Tags
    kcal, ew, kh, fe = r["kcal"], r["eiweiss"], r["kohlenhydrate"], r["fett"]
    if kcal:
        ewp, khp = 4*ew/kcal*100, 4*kh/kcal*100
        if "High-Protein" in tn and ewp < 20:
            befund["highprotein_falsch"].append((name, rid, f'{ew:g} g EW bei {kcal:g} kcal = {ewp:.0f} E%'))
        if "Low-Carb" in tn and khp > 20:
            befund["lowcarb_falsch"].append((name, rid, f'{kh:g} g KH bei {kcal:g} kcal = {khp:.0f} E%'))
        if "High-Carb" in tn and khp < 55:
            befund["highcarb_falsch"].append((name, rid, f'{kh:g} g KH bei {kcal:g} kcal = {khp:.0f} E%'))
        if "Kalorienarm" in tn and kcal > 400:
            befund["kalorienarm_falsch"].append((name, rid, f'{kcal:g} kcal / Portion'))
    if "Ballaststoffreich" in tn:
        if not r["ballaststoffe"]:
            befund["ballast_unpruefbar"].append((name, rid, "ballaststoffe = 0, nicht pruefbar"))
        elif kcal and r["ballaststoffe"]/kcal*100 < 3:
            befund["ballast_falsch"].append((name, rid, f'{r["ballaststoffe"]:g} g / {kcal:g} kcal'))
    if "Schnell und einfach" in tn and r["zeit_gesamt"] and r["zeit_gesamt"] > 30:
        befund["schnell_falsch"].append((name, rid, f'{r["zeit_gesamt"]:g} Min.'))

# --- 4. Dubletten
def key(n): return re.sub(r"[^a-z0-9]", "", norm(n))
dub = collections.defaultdict(list)
for r in rez: dub[key(r["name"])].append(r)
DUB = {k: v for k, v in dub.items() if len(v) > 1}

if "--json" in sys.argv:
    json.dump({"n_unveroeffentlicht": len(UNP), "befund": dict(befund),
               "dubletten": {k: [(x["name"], x["id"], x["id"] in SLUG) for x in v]
                             for k, v in DUB.items()},
               "schwellen": SCHWELLE},
              sys.stdout, ensure_ascii=False, indent=1)
    sys.exit(0)

print(f"{len(UNP)} unveroeffentlichte Rezepte geprueft\n")
for k in sorted(befund, key=lambda k: -len(befund[k])):
    print(f"{len(befund[k]):4d}  {k}")
print(f"{sum(len(v) for v in DUB.values()):4d}  dubletten ({len(DUB)} Namensgruppen)")
