# Architecture — plain language

Design date: 17 September 2026. SF Bay Area MVP. Rewritten for clarity; supersedes the earlier
version of this file.

---

## The whole thing in one sentence

**A robot collects events twice a day. The app just reads what the robot collected.**

The robot is a Python script on a timer. It visits event websites, uses an LLM to turn messy
pages into clean records, and saves them to a database. Hours later a user opens the app and the
backend hands over rows that are already sitting there. **No crawling and no LLM happen while the
user waits** — that is what makes it fast and cheap.

The one exception is photos and reviews. Those come from licensed APIs that forbid storing their
data, so they get fetched live when a user taps an event. That's step 7.

---

## The five places everything runs

| | Place | What it is |
|---|---|---|
| **A** | The user's iPhone | The app. Swift/SwiftUI. Shows the list, applies filters, displays photos and reviews |
| **B** | GitHub Actions | A free computer that wakes on a schedule, runs your Python crawler, shuts down. This is the robot |
| **C** | Neon (hosted Postgres) | Where collected events live. Always on, free at this size |
| **D** | Google Cloud Run | A small always-available Python program that answers the app by reading the database |
| **E** | Outside companies | Anthropic/Google/OpenAI for the LLM. Google Places/Tripadvisor for photos and reviews |

Nothing here is a server you rent, patch, or pay for by the hour.

---

## The seven steps

| # | What happens | Where it runs | Language | Cost | Alternative, same step |
|---|---|---|---|---|---|
| 1 | Timer fires | GitHub Actions | YAML | $0 | Google Cloud Scheduler — $0 |
| 2 | Download ~800 event pages | GitHub Actions | Python | $0 (2,000 free min/mo) | Cloud Run Job — $0 |
| 3 | **Turn pages into event records ← LLM** | Anthropic API | Python calls it | ~$62/mo | Gemini Flash-Lite ~$6 · GPT-5-nano ~$4 |
| 4 | Save events | Neon Postgres | SQL | $0 | Supabase $0 · GitHub Pages JSON $0 |
| 5 | App asks for today's events | iPhone | Swift | $99/yr Apple | Mobile web app (PWA) — $0 |
| 6 | Read database, return JSON | Google Cloud Run | Python | $0 to ~10k users/day | Render $0 · Heroku $5/mo |
| 7 | Fetch photos + reviews | Google Places API | Python calls it | $0 up to 1,000/mo | Tripadvisor 5,000 free · Foursquare 500 free |

**On Heroku, since you asked:** it works, but has had **no free tier since November 2022**. The
cheapest Eco dyno is $5/month and sleeps when idle. Cloud Run does the same job for $0.

---

## How it comes together

### 4:00 AM — nobody is using the app

1. **GitHub Actions wakes up.** A schedule in `.github/workflows/crawl.yml` says "run at 4am and
   4pm". GitHub starts a free Linux machine.
2. **Your Python script runs.** It reads ~800 Bay Area sources from the database and downloads
   their pages. About **40% already contain machine-readable event data** (schema.org JSON-LD,
   which sites add for Google) — parsed free, **no LLM needed**.
3. **The other 60% go to the LLM.** Messy pages are sent with "return this page as JSON with
   these exact fields". Out comes title, start time, venue, price, ticket link, category **and
   language**. This is **LLM use #1** and the only real cost in the system.
4. **Results are cleaned and saved.** Python matches venues to real places, drops duplicates,
   writes rows to Neon. The machine shuts down. Runtime: ~20 minutes.

### 7:30 PM — a user opens the app in the Mission

1. **One request.** iPhone → Cloud Run: "events starting between now and midnight, within 15
   miles of this GPS point."
2. **One database query.** Indexed lookup on start time plus a geography index for the radius.
   **Under 100ms.** No crawling, no LLM.
3. **The app filters locally.** Date, time, category and language are applied on the phone — the
   result set is small enough that this is instant and free.
4. **User taps an event.** Cloud Run calls **Google Places** with the venue's saved place ID and
   gets rating, up to five reviews, and photos. Displayed with attribution and **not saved**,
   which is what their terms require.

**The key idea:** the slow expensive work happened at 4am when nobody cared. The user's request
only reads what was already there.

---

## Where the LLM is used

**Exactly two places, and one is optional.**

- **LLM use #1 — turning pages into event records (step 3).** Required. It replaces writing a
  custom parser for each of 800 sites. ~21,000 pages/month.
- **LLM use #2 — translation (optional).** Since you want Chinese, Russian, Spanish and Arabic,
  you may want English summaries. One extra field in the same call, so nearly free. Skip at
  first — original-language display is often what those users want.
- **Nowhere else.** Not for search, not for filtering, not for photos or reviews.

### Which LLM — all options

| Model | In / out per 1M tokens | Your cost/month | Verdict |
|---|---|---|---|
| GPT-5-nano | $0.05 / $0.40 | **~$4** | Cheapest — try first |
| Gemini 2.5 Flash-Lite | $0.10 / $0.40 | **~$6** | Cheapest — try first |
| GPT-5-mini | $0.25 / $2.00 | ~$19 | Middle ground |
| Claude Haiku 4.5 | $1.00 / $5.00 | ~$62 | Safe default, strongest small model |
| Claude Sonnet 5 | $2.00 / $10.00 | ~$123 | Overkill for extraction |
| Self-hosted Qwen | GPU rental | $256–400 | No — see below |

All assume 21,000 pages/month with batching and caching on. Both roughly halve the raw price;
turn them on from day one.

**Cheapest isn't automatically right, because of your language requirement.** Nano-class models
degrade on messy HTML and non-English pages — exactly your Chinese, Russian and Arabic sources.
**Test properly:** 100 real pages including 30 non-English, run through GPT-5-nano and Claude
Haiku, count errors. If nano gets 95%+ right, the $58/month difference is free money. If it
mangles Cyrillic venue names, pay for Haiku.

**Why not self-host Qwen:** ~21 million output tokens/month. No free hosting tier includes a GPU,
so CPU-only means **about 49 days of computing per month** — a month has 30. A rented GPU is
$256–400/month against $4–62 for an API. Revisit at ~100× the volume.

---

## Photos and reviews

You get them by **calling licensed APIs, not by scraping.** Three services return venue photos
and reviews legally, each with a free monthly allowance:

| Service | Free per month | What you get | After free tier |
|---|---|---|---|
| Tripadvisor Content API | **5,000 calls** | Photos, reviews, details. Best free allowance | Paid; card required |
| Google Places (Enterprise+Atmosphere) | **1,000 calls** | Rating, up to 5 reviews, photos. Best coverage | $40 / 1,000 |
| Foursquare Places (Pro) | **500 calls** | Photos, tips, venue attributes | $15 / 1,000 |
| **All three combined** | **6,500 calls** | Enough for an MVP without paying anything | |

### Three rules that keep this free and legal

1. **Fetch only when a user taps an event**, never for the whole list. A 40-event list costs zero
   calls; only the opened one costs a call. That's what makes 6,500 go a long way.
2. **Store the place ID, nothing else.** Google's terms let you keep `place_id` forever and
   lat/lng for 30 days, but not reviews, names or ratings. Save the ID during the 4am crawl,
   fetch the rest live.
3. **Cascade through the free tiers.** Tripadvisor (5,000) → Google (1,000) → Foursquare (500).
   Track the count in your database and stop when exhausted — your budget-guard idea, and it
   works perfectly here.

### Free extras, no API needed

| What | Where it comes from | Cost |
|---|---|---|
| Event flyer image | Already on the listing page your crawler read | $0 |
| Venue photos | The venue's own website, linked with attribution | $0 |
| **Organizer's past events** | **Your own database** — a query over events you already have | $0 |
| Organizer's Instagram posts | Instagram oEmbed — the sanctioned way to embed public posts | $0 |
| Notable venue photos | Wikimedia Commons, openly licensed | $0 |

**The one honest limit:** these APIs cover *venues* (bars, clubs, theaters) well, because that's
what Google, Tripadvisor and Foursquare index. They do **not** cover *organizers* — a promoter or
dance collective has no Google Places entry. Venue reviews you can have on day one; organizer
reviews have to come from your own users, starting empty.

---

## Total cost

| Item | Cheapest setup | Safe setup |
|---|---|---|
| GitHub Actions (crawler) | $0 | $0 |
| Database (Neon or Supabase) | $0 | $0 |
| Read API (Cloud Run) | $0 | $0 |
| LLM extraction | $4 (GPT-5-nano) | $62 (Claude Haiku) |
| Photos + reviews | $0 within free tiers | $0–40 |
| Image storage (Cloudflare R2) | $0 | $5 |
| Domain | $1 | $1 |
| Apple Developer ($99/yr) | $8 | $8 |
| **Total** | **~$13/mo** | **~$76–116/mo** |

Start with the cheapest column. Move one line at a time, only when something breaks. The most
likely upgrade is the LLM, and only if non-English extraction disappoints.

---

## Build order

1. **The Python crawler, on your laptop.** No hosting, no app, no GitHub. A script that produces
   a clean list of today's Bay Area events in a file. If this doesn't work, nothing else matters.
2. **Move it to GitHub Actions.** Add the schedule file. Now it runs twice a day without you.
3. **Add the database.** Neon free tier; the crawler writes there instead of a file.
4. **The read API.** One endpoint on Cloud Run, one query. Test in a browser before any app exists.
5. **The iPhone app.** List, detail, five filters. The $99 Apple fee starts here.
6. **Photos and reviews on the detail screen.** Wire Tripadvisor first — largest free allowance.
7. **Accounts and your own reviews.** Last. Where it stops being a listings app and starts being
   yours.
