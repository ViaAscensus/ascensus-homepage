---
name: leitstand
description: >-
  Check and work on tasks from Patrick's personal "Leitstand" project
  cockpit (a PocketBase-backed tracker at pb.ascensus.fit, unrelated to
  any specific repo). Trigger immediately whenever Patrick's message is,
  contains, or starts with "#doit" — including when the ENTIRE message
  is literally just "#doit" and nothing else, with no project name, no
  other text, no context in the conversation. That bare form is not an
  incomplete or ambiguous request needing clarification. It is a
  complete, specific instruction meaning "check PocketBase for anything
  flagged claude_auftrag and work on it" — never respond to it by asking
  what to work on or listing unrelated project guesses (e.g. "the
  homepage, the X pipeline, or something else?"); that question is
  exactly the wrong response and means this skill was skipped. Same for
  "#doit" followed by a project name (e.g. "#doit test", "#doit
  RunRebels") and for Patrick
  saying "Leitstand" in any form (e.g. "Projekt X im Leitstand", "schau
  im Leitstand nach Y", asking what's been handed off to Claude, or
  wanting to report results back into that tracker). Always use this
  skill for such requests even when no matching repo is attached to the
  session — the data lives in PocketBase, not in a git repo, so don't
  say you can't access it; follow this skill to read and write it
  directly.
---

# Leitstand

Patrick's personal project cockpit — a status tracker for everything he's
working on, independent of any single repo or coding session. It lives in
PocketBase, not in git, specifically so it survives across sessions and
tools. When he mentions it, he wants you to actually read and act on what's
in there, not just acknowledge the request.

## Check for the MCP connector first — before anything below

Patrick has a "Leitstand" custom connector (a remote MCP server, repo
`leitstand-mcp`) that some sessions — especially Chat/Cowork, which has no
environment secrets at all — have enabled. It exposes tools literally named
`mcp__Leitstand__leitstand_liste_projekte`,
`mcp__Leitstand__leitstand_projekt_schritte`,
`mcp__Leitstand__leitstand_schritt_anlegen`,
`mcp__Leitstand__leitstand_schritt_aktualisieren`,
`mcp__Leitstand__leitstand_projekt_aktualisieren`, and
`mcp__Leitstand__leitstand_anhang_lesen`.

**If those tools are present in this session (check the tool list, or run
`ToolSearch` for "Leitstand" if tools can be deferred here), use them
directly for everything below — reading projects, reading steps, writing
new steps, updating status — instead of raw HTTP calls to PocketBase.**
They already hold the PocketBase credentials server-side; nothing to
authenticate, no environment secret to look for or ask Patrick about. Skip
straight to "Finding the right record(s)" below and call the tools instead
of the `GET`/`POST`/`PATCH` examples shown there — same filters, same
field names, just as tool arguments instead of raw requests.

This isn't an edge case to fall back on if HTTP fails — a known real
failure looked exactly like that: a Chat/Cowork session had the connector
available and working, but followed the HTTP instructions below anyway,
hit a blocked network + missing env secrets, and reported the write step
as impossible even though the write tool was sitting right there in its
own tool list. Checking for the connector's tools is the first thing to
do in this skill, before reading any further.

Only when those `mcp__Leitstand__*` tools are *not* present in this
session's tool list does the rest of this section (raw PocketBase HTTP via
environment secrets) apply.

## Where the data lives

PocketBase instance: `https://pb.ascensus.fit`, two collections:
`projekte` (the projects themselves) and `projekt_schritte` (their next
steps — each one its own record, not a line in a text field; see below).

Authenticate as a record in the `api_clients` auth collection (the same
account used elsewhere for Ascensus automation). The credentials should be
available as an environment secret in this session, under these exact
names — check for them first:
- `PB_API_CLIENTS_EMAIL`
- `PB_API_CLIENTS_PASSWORD`

If they're not set (or set under different names in an older session),
ask Patrick to add them as an environment secret for this session under
those exact names, via the session's environment settings — never ask
him to paste a password into chat, and don't guess at other variable
names or block silently.

Auth call:
```
POST https://pb.ascensus.fit/api/collections/api_clients/auth-with-password
Body: {"identity": "<email>", "password": "<password>"}
→ {"token": "...", "record": {...}}
```
This instance expects the token raw in the `Authorization` header —
**no** `Bearer` prefix.

## Record shape

Each `projekte` record has:

| Field | Meaning |
|---|---|
| `name` | Project name |
| `status` | `offen` / `in_arbeit` / `wartet_auf_freigabe` / `erledigt` / `pausiert` |
| `stand` | Current state — one point per line (`\n`-separated), rendered as bullets in the Leitstand UI. Stays a flat text field by design, unlike `schritte` below |
| `quelle` | Where the record came from (usually `leitstand`) |
| `erstellt` / `aktualisiert` | Timestamps |
| `claude_auftrag` | Timestamp, nullable. Set when Patrick clicks "→ An Claude senden" in the UI — his explicit signal that this project is ready for you to work on |
| `anhaenge` | Array of uploaded filenames (0+), general attachments on the project itself (not tied to one step) |

Each `projekt_schritte` record (one per next-step item, not a line in a
field — Patrick deliberately split this out so a new step never has to be
squeezed into existing text and so a step can carry its own attachment):

| Field | Meaning |
|---|---|
| `projekt` | Relation to the `projekte` record this step belongs to |
| `text` | The step itself. Often *is* a direct instruction to you, not just a note (e.g. "bitte X erledigen") — especially the most recently created one — read it as a task, not as background |
| `erledigt` | Bool — ticked in the UI when done |
| `anhaenge` | Array of filenames, attachments on THIS step specifically. A `text` like "siehe Screenshot im Anhang" means the actual brief is IN this step's own file, not the project's — fetch it from `GET <PB_URL>/api/files/projekt_schritte/<step id>/<filename>` (same `Authorization` header) before doing the work, don't guess at what it shows |
| `erstellt` / `aktualisiert` | Timestamps |
| `antwort_auf` | Self-relation to another `projekt_schritte` record, nullable. When set, the Leitstand UI threads this step as a chat message continuing that step's conversation instead of showing it as an unrelated new one — this is how a task and its answer(s) stay visually and structurally grouped. See "Finishing the task" below: this is the field that makes your result land in the right place |
| `autor` | `"patrick"` or `"claude"` — who wrote this step. The Leitstand UI renders each branch as a chat (Patrick's messages left, Claude's right), so this is required on every step you create. Always `"claude"` for anything you write — never guess `"patrick"` on his behalf |

## "#doit" shorthand

Patrick's fast way to invoke this skill: `#doit <name>` means "look up
project `<name>` in the Leitstand and do what it says" — identical to him
spelling out "schau im Leitstand nach Projekt `<name>`". Bare `#doit` with
no name means "check what's been handed off to you generally" — the same
as the general `claude_auftrag` check below, nothing more ambiguous than
that. It is never a prompt to ask him what to work on, and never a cue to
guess at other projects (a known failure mode: one session answered bare
`#doit` with "no task specified in chat yet — want me to work on the
homepage, the Anamnese pipeline, or the weekly quiz?", which skipped
PocketBase entirely and defeated the whole point — the task lives there,
not in this chat's history). If the handoff query comes back empty, say
that plainly ("nichts im Leitstand markiert") — that's a fine answer;
inventing unrelated options to choose from is not.

## Finding the right record(s)

- **Named project** ("#doit test", "#doit RunRebels", "Projekt Test im Leitstand"):
  filter by name.
  ```
  GET /api/collections/projekte/records?filter=name~"<name>"
  ```
  (`~` does a partial/contains match, which is more forgiving of exact
  capitalization or punctuation than `=`.)
- **General check** ("was wurde an Claude übergeben", "was steht im Leitstand an"):
  filter by the handoff marker instead.
  ```
  GET /api/collections/projekte/records?filter=claude_auftrag!=""
  ```
  This is the whole point of that field: Patrick marks something as ready
  on his side, and this is how you find it without him having to repeat
  the instruction in chat.

Once you have the project's id, fetch its steps separately:
```
GET /api/collections/projekt_schritte/records?filter=projekt="<project id>"&sort=erstellt
```

## Doing the work

1. Read `stand` and the project's `projekt_schritte` carefully — the
   most recent step especially often *is* the task, phrased as a note to
   self rather than a formal request. If it references an attachment,
   read that step's own file too (see the `anhaenge` row above) before
   you start — the real brief may be in there, not in the text.
2. Actually do what's asked — research, write code, check something,
   whatever it calls for — the same way you would if Patrick had typed
   the instruction directly in this conversation. The record is a stand-in
   for that message, not a ticket to triage.

## Finishing the task — two parts, both required

A request that came in through the Leitstand is only done when **both**
of these have happened. Producing a great answer and only putting it in
chat is an *incomplete* response to this kind of request — Patrick opens
the Leitstand later expecting to find the result there, not a memory of
a chat he had once. Don't treat the PocketBase write as a courtesy
afterthought; it's the actual deliverable. The chat reply is just you
telling him you did it.

1. **Write the result into PocketBase as a new step, nested under the one
   that asked for it.** Create a new `projekt_schritte` record linked to
   the project — don't edit or append to an existing one, each step is
   its own record. If this is a reply to a specific existing step (the
   normal case — you read a step, did what it asked, now you're writing
   the result), also set `antwort_auf` to that step's id, so your answer
   nests inside its box in the UI instead of sitting as a disconnected
   sibling row below it (Patrick explicitly asked for this after the
   first version put task and answer side by side with no visible
   connection). Only omit `antwort_auf` when you're genuinely adding a
   new, independent next step rather than answering one. Update the
   project's `status` too if the work changes it. Do this *before*
   writing your chat reply, not after, so you can't skip it under time
   pressure once the "real" work feels finished.
   ```
   POST /api/collections/projekt_schritte/records
   Body: {"projekt": "<project id>", "antwort_auf": "<id of the step you're answering, or omit>",
          "text": "...", "erledigt": false, "autor": "claude",
          "erstellt": "<now, ISO 8601>", "aktualisiert": "<now>"}
   ```
   `"autor": "claude"` is always required on every step you create this
   way — it's how the Leitstand UI tells your messages apart from
   Patrick's own (chat-bubble layout, his on the left, yours on the
   right). Going through the `mcp__Leitstand__*` tools instead, this is
   set automatically — only relevant for this raw-HTTP fallback path.

   (separately, if needed: `PATCH /api/collections/projekte/records/<id>`
   with `{"status": "...", "aktualisiert": "<now>"}`)

   If the result is long-form content (e.g. drafted posts, a full plan),
   put the actual content in this step's `text`, not just a pointer to
   it — the whole point is that it's there the next time he opens the
   project, without needing this chat.

   If the work produced a file (a generated image, a PDF) and you're going
   through the `mcp__Leitstand__*` tools: there is currently no tool to
   upload an attachment, only `leitstand_anhang_lesen` to read existing
   ones. Send the file in chat as normal and say so explicitly in the step
   `text` (e.g. "Grafik als `post1.png` im Chat geschickt, hier nicht
   anhängbar") — don't silently skip it or claim it's attached when it
   isn't. Going through raw PocketBase HTTP, uploading is possible
   (multipart on the `anhaenge` field) and should actually be done.

   **Exception — correcting your own just-written step, same turn:**
   "don't edit an existing one" above is about Patrick's steps and about
   past answers from earlier sessions; it does not mean every small
   follow-up within the *same* piece of work has to become its own nested
   reply. If you wrote a step a moment ago in this same turn and now need
   to fix a typo in it, add a missed detail, or extend it before you're
   done — `leitstand_schritt_aktualisieren` (or `PATCH`) that same step
   instead of creating another one nested under it. Deeply nested chains
   of tiny self-corrections are exactly what made the Leitstand UI
   unreadable before it got collapse/indent-cap support (see `leitstand`
   repo's `CLAUDE.md`), so don't reproduce that by habit. This exception
   stops as soon as the content is a genuinely new answer — to a new
   instruction from Patrick, or to a different step entirely — that gets
   its own new step with `antwort_auf` as described above, same as ever.
2. **Then summarize in chat too**, so he knows it's done without having
   to go check.

Leave `claude_auftrag` as it is either way. Patrick clears it himself in
the UI ("Markierung entfernen") once he's seen the result — that's his
acknowledgment step, not yours to take away. Only clear it if he
explicitly asks you to.
