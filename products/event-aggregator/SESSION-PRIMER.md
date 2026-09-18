# Starting a new Claude Code session on this project

## Step 1 — install Claude Code on the Mac (once)

Desktop app: **https://claude.com/download**

Or in Terminal:

```
npm install -g @anthropic-ai/claude-code
```

## Step 2 — open a session in the project directory

```
cd ~/Documents/eventjim
claude
```

The working directory is now `/Users/vityavitechkin/Documents/eventjim`. That session can read
your files, run the collector and see the output — none of which a remote session can do.

## Step 3 — load the context

Paste this as the first message:

---

> Read these files before doing anything, in this order:
>
> 1. `README.md` — what this project is and the decisions already made
> 2. `docs/ARCHITECTURE.md` — the full design, including three rounds of follow-up questions at the bottom
> 3. `docs/SETUP.md` — the accounts and API keys
> 4. `docs/MVP-SCOPE.md` — what to build first and what to cut
> 5. `docs/stack-diagram.png` — the whole system in one picture
>
> These came from a long planning session. Every decision in them is settled — do not re-open
> them unless I ask. In particular: Python only, DigitalOcean for the server, Neon for the
> database, Gemini or ChatGPT for the LLM, native iPhone app, photos never stored on the server,
> no videos, event-goer features only (no organizer tools yet), SF Bay Area with a 15-mile radius.
>
> Once you have read them, tell me in three sentences what we are building and what the first
> milestone is. Then wait.

---

## Step 4 — then start work

Once it has confirmed, the first real task:

> Build the day-1 collector described in README.md. Python. It reads keys from `.env`, pulls
> Bay Area events for the next 7 days from Ticketmaster and SeatGeek, and writes them to a CSV
> with these columns: source, event_id, title, starts_at, ends_at, venue_name, address, lat,
> lon, price_min, price_max, ticket_url, image_url, category, language, location_type.
>
> No database, no LLM, no dedup yet. Just those two APIs and a CSV I can open.

---

## What lives where

| Thing | Where |
|---|---|
| Project code and docs | `~/Documents/eventjim` → `supertranslator/eventjim` on GitHub |
| API keys | `.env` in that folder — gitignored, never committed |
| The system diagram | `docs/stack-diagram.png`, editable source `docs/stack-diagram.svg` |

## Ground rules worth repeating to any new session

- **The LLM is never in the request path.** Collection happens on a schedule; the app only reads.
- **Photos are never stored on the server or in the database** — links only, the phone caches them.
- **No image bytes in Postgres, ever.** The free tier is 0.5 GB; that is about 170 photos.
- **`.env` is never committed.** Check with `git check-ignore -v .env` before the first commit.
- **Start with 10 sources, not 800.** The ten are listed in README.md and chosen to exercise
  all five collection techniques.
