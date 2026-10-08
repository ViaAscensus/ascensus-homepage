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
  "#doit <name>" (e.g. "#doit test", "#doit RunRebels") and for Patrick
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

## Where the data lives

PocketBase instance: `https://pb.ascensus.fit`, collection `projekte`.

Authenticate as a record in the `api_clients` auth collection (the same
account used elsewhere for Ascensus automation). The credentials should be
available as an environment secret in this session — check environment
variables for something PocketBase-related first. If nothing is set, ask
Patrick to add one as an environment secret for this session (never ask him
to paste a password into chat) rather than guessing or blocking silently.

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
| `stand` | Current state — one point per line (`\n`-separated), rendered as bullets in the Leitstand UI |
| `schritte` | Next steps — same one-point-per-line format. Often the *last* line is a direct instruction to you, not just a note (e.g. "bitte X erledigen") — read it as a task, not as background |
| `quelle` | Where the record came from (usually `leitstand`) |
| `erstellt` / `aktualisiert` | Timestamps |
| `claude_auftrag` | Timestamp, nullable. Set when Patrick clicks "→ An Claude senden" in the UI — his explicit signal that this project is ready for you to work on |
| `anhaenge` | Array of uploaded filenames (0+), stored by PocketBase's file field. A `schritte` line like "siehe Screenshot im Anhang" means the actual task content is IN that file, not fully spelled out in text — fetch and read it (`GET <PB_URL>/api/files/projekte/<record id>/<filename>`, same `Authorization` header) before doing the work, don't guess at what it shows |

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

## Doing the work

1. Read `stand` and `schritte` carefully — `schritte` especially often
   *is* the task, phrased as a note to self rather than a formal request.
   If it references an attachment, read that file too (see the `anhaenge`
   row above) before you start — the real brief may be in there, not in
   the text.
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

1. **Write the result into PocketBase.** Append a new line to `schritte`
   (don't delete the existing ones — the history matters) and update
   `status` if the work changes it. Do this *before* writing your chat
   reply, not after, so you can't skip it under time pressure once the
   "real" work feels finished.
   ```
   PATCH /api/collections/projekte/records/<id>
   Body: {"schritte": "<existing schritte>\n<new line>", "aktualisiert": "<now, ISO 8601>", "status": "..."}
   ```
   If the result is long-form content (e.g. drafted posts, a full plan),
   put the actual content in `schritte`, not just a pointer to it — the
   whole point is that it's there the next time he opens the project,
   without needing this chat.
2. **Then summarize in chat too**, so he knows it's done without having
   to go check.

Leave `claude_auftrag` as it is either way. Patrick clears it himself in
the UI ("Markierung entfernen") once he's seen the result — that's his
acknowledgment step, not yours to take away. Only clear it if he
explicitly asks you to.
