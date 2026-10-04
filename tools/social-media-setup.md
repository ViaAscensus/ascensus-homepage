# Social-Media-Planer einrichten

`social-planer.html` ist Patricks eigenes Werkzeug, um Instagram-, Facebook- und
LinkedIn-Beiträge zu planen und zu veröffentlichen. Es ist kein Kundenfeature und
taucht deshalb nirgends in der öffentlichen Navigation oder im Mitglieder-Dashboard
auf. Zugriff ist auf `patrick@ascensus.fit` beschränkt.

## Architektur

```
social-planer.html  →  PocketBase (social_posts)  ←→  n8n  →  Meta Graph API / LinkedIn API
```

* Die Seite selbst spricht nur mit PocketBase (lesen, anlegen, ändern, löschen).
* Das eigentliche Veröffentlichen übernimmt n8n (`tools/n8n-social-publish.json`):
  entweder sofort per Klick auf „Jetzt veröffentlichen" (Webhook) oder automatisch
  für vorgeplante Beiträge (Cron, alle 5 Minuten).
* n8n braucht eigene Zugänge zu Meta und LinkedIn – die kann diese Umgebung nicht
  für Dich einrichten, das sind die Schritte unten.

## 1. PocketBase: Collection `social_posts` anlegen

In der PocketBase-Admin-Oberfläche (`pb.ascensus.fit/_/`) eine neue Collection
`social_posts` mit folgenden Feldern anlegen:

| Feld | Typ | Hinweis |
|---|---|---|
| `text` | Text (mehrzeilig) | Beitragstext |
| `plattformen` | Select, mehrfach | Werte: `instagram`, `facebook`, `linkedin` |
| `medien` | Datei, mehrfach | Bilder (jpg/png/webp). Videos sind vorerst nicht unterstützt (siehe unten) |
| `geplant_am` | Datum | optional – leer heißt „nur Entwurf, kein Termin" |
| `status` | Select, einfach | Werte: `entwurf`, `geplant`, `veroeffentlicht`, `teilweise_veroeffentlicht`, `fehler`; Default `entwurf` |
| `ergebnis` | JSON | wird von n8n befüllt: `{instagram:{ok,url,fehler}, facebook:{...}, linkedin:{...}}` |
| `fehler` | Text | letzte Fehlermeldung, von n8n befüllt |
| `notiz` | Text | optionale interne Notiz, nie veröffentlicht |

**API-Regeln** – nur Patrick darf lesen/schreiben:

```
List/Search:  @request.auth.email = "patrick@ascensus.fit"
View:         (leer – siehe Hinweis unten)
Create:       @request.auth.email = "patrick@ascensus.fit"
Update:       @request.auth.email = "patrick@ascensus.fit"
Delete:       @request.auth.email = "patrick@ascensus.fit"
```

**Warum `View` leer bleibt:** Instagram und Facebook holen sich das Bild beim
Veröffentlichen selbst über eine öffentliche URL ab (`image_url` bei der Graph
API) – sie können sich nicht als Patrick einloggen. Mit leerer `View`-Regel kann
jeder die Bild-/Datei-URL eines Posts abrufen, *wenn* er die zufällige Record-ID
kennt – aber niemand kann die Liste durchsuchen oder Entwürfe aufzählen (die
`List`-Regel bleibt geschützt). Das ist die gleiche Abwägung wie bei einem
„Jeder mit dem Link"-Freigabelink. Reicht Dir das nicht, bräuchte es einen
eigenen Datei-Proxy – das ist in dieser Vorlage nicht enthalten.

## 2. Meta (Instagram + Facebook)

1. Auf [developers.facebook.com](https://developers.facebook.com) eine App vom
   Typ „Business" anlegen.
2. Die Facebook-Seite von ASCENSUS mit der App verbinden; das verknüpfte
   Instagram-Konto muss ein **Business- oder Creator-Konto** sein (kein privates).
3. Berechtigungen, die der Zugriffstoken braucht: `pages_show_list`,
   `pages_manage_posts`, `pages_read_engagement`, `instagram_basic`,
   `instagram_content_publish`.
4. Für die eigene Seite/den eigenen Account reicht i.d.R. der Entwicklungsmodus
   der App (Du bist Admin/Entwickler) – **App Review** wird nur nötig, wenn
   andere Personen/Seiten das nutzen sollen.
5. Einen langlebigen Page Access Token erzeugen (Graph API Explorer: Token
   anfordern → „Access Token Debugger" → „Extend Access Token"; läuft nach ca.
   60 Tagen ab und muss erneuert werden. Für Dauerbetrieb lohnt ein System-User
   in der Meta Business Suite mit eigenem, nicht ablaufendem Token).
6. Seiten-ID (`FACEBOOK_PAGE_ID`) und Instagram-Business-Account-ID
   (`INSTAGRAM_USER_ID`) notieren – beide stehen im Graph API Explorer unter
   `/me/accounts` bzw. `/{page-id}?fields=instagram_business_account`.

**Einschränkung dieser Vorlage:** Nur das erste Bild eines Posts wird verwendet,
keine Mehrbild-Alben, keine Videos/Reels (Reels brauchen einen asynchronen
Verarbeitungsschritt mit Status-Abfrage, der hier fehlt). Reicht für Foto- und
Text-Posts.

## 3. LinkedIn

LinkedIns API ist seit 2023 stark eingeschränkt. Organisations-Posting braucht
die Berechtigung `w_organization_social`, die Meta-ähnlich über eine LinkedIn-App
freigeschaltet werden muss; persönliches Profil-Posting ist über die normale API
praktisch nicht mehr öffentlich zugänglich (das läuft über die „Community
Management API", die einen Partner-Antrag bei LinkedIn voraussetzt).

**Praktische Konsequenz:** Bau Dir keine Erwartung auf, dass LinkedIn zuverlässig
automatisch postet. Die Vorlage versucht es trotzdem (Organisations-Posting via
`ugcPosts`), meldet aber bei fehlender Berechtigung einen klaren Fehler zurück.
Der „Text kopieren"-Button in `social-planer.html` ist für LinkedIn der
verlässliche Standardweg – manuell in LinkedIn einfügen, geht in zwei Klicks.

## 4. n8n: Workflow importieren

1. `tools/n8n-social-publish.json` in n8n importieren.
2. Jedem HTTP-Request-Node seine Credential zuweisen (Import bringt keine
   Zugangsdaten mit, die sind instanzgebunden):
   * **PocketBase Social Token** – Header Auth, Name `Authorization`, Wert =
     Token aus `api_clients` (gleiches Prinzip wie in `tools/README.md`
     beschrieben, pur ohne `Bearer`-Präfix). Für die Nodes „Post laden
     (manuell)", „Fällige Posts laden", „Status in PocketBase speichern".
   * **Meta Graph Access Token** – Query Auth, Parametername `access_token`,
     Wert = der Page Access Token aus Schritt 2. Für die Facebook- und
     Instagram-Nodes.
   * **LinkedIn Access Token** – Header Auth, Name `Authorization`, Wert
     `Bearer <Token>`. Für den LinkedIn-Node.
3. In den Code-Nodes die Platzhalter ersetzen: `FACEBOOK_PAGE_ID`,
   `INSTAGRAM_USER_ID`, `LINKEDIN_ORG_ID`.
4. Workflow aktivieren.
5. Die Webhook-URL des Nodes „Webhook: Einzelbeitrag" kopieren (Produktions-URL,
   nicht die Test-URL) und in `social-planer.html` bei `N8N_WEBHOOK_URL`
   eintragen.
6. Cron-Intervall (Standard: 5 Minuten) bei Bedarf anpassen.

## 5. Testen

* Entwurf mit Text + einem Bild anlegen, nur „Facebook" anhaken, auf „Jetzt
  veröffentlichen" klicken, auf der Seite prüfen.
* Gleiches für Instagram.
* Einen Post mit `geplant_am` in 5–10 Minuten anlegen, offen lassen – prüfen,
  ob der Cron ihn automatisch holt.
* LinkedIn separat testen und realistisch einschätzen, ob es bei Dir
  funktioniert (siehe Abschnitt 3).
