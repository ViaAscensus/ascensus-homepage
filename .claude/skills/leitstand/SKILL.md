---
name: leitstand
description: Check and work on tasks from Patrick's personal "Leitstand" project cockpit (a PocketBase-backed tracker at pb.ascensus.fit, unrelated to any specific repo). Use this whenever Patrick writes "#doit" (alone, or followed by a project name, e.g. "#doit test", "#doit RunRebels") or says "Leitstand" in any form (e.g. "Projekt X im Leitstand", "schau im Leitstand nach Y"), asks what's been handed off to Claude, asks about the status or next steps of a personal project that isn't part of the currently attached repository, or wants to report back results into that tracker. "#doit" is his short form for this skill — treat it exactly like a full "check the Leitstand" request, never as a literal hashtag or formatting instruction. Always use this skill for such requests even when no matching repo is attached to the session — the data lives in PocketBase, not in a git repo, so don't say you can't access it; follow this skill to read and write it directly.
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

## "#doit" shorthand

Patrick's fast way to invoke this skill: `#doit <name>` means "look up
project `<name>` in the Leitstand and do what it says" — identical to him
spelling out "schau im Leitstand nach Projekt `<name>`". Bare `#doit` with
no name means "check what's been handed off to you generally" — the same
as the general `claude_auftrag` check below. Don't ask him to rephrase it;
`#doit` is the point, not a shortcut to question.

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
2. Actually do what's asked — research, write code, check something,
   whatever it calls for — the same way you would if Patrick had typed
   the instruction directly in this conversation. The record is a stand-in
   for that message, not a ticket to triage.
3. Report the result back into PocketBase, not just in chat, so it's
   visible the next time he opens the Leitstand: append a new line to
   `schritte` (don't delete the existing ones — the history matters) and
   update `status` if the work changes it.
   ```
   PATCH /api/collections/projekte/records/<id>
   Body: {"schritte": "<existing schritte>\n<new line>", "aktualisiert": "<now, ISO 8601>", "status": "..."}
   ```
4. Leave `claude_auftrag` as it is. Patrick clears it himself in the UI
   ("Markierung entfernen") once he's seen the result — that's his
   acknowledgment step, not yours to take away. Only clear it if he
   explicitly asks you to.
5. Still summarize what you did in the chat reply too — PocketBase is the
   durable record, but he's waiting on a response here as well.
