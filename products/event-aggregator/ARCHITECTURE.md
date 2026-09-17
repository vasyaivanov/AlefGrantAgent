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

---

# Follow-up answers

## 1. Where do the 800 sources come from?

**They are *websites*, not search results.** A list of TV channels, not a list of tonight's shows.

You never ask anyone "give me events near Palo Alto". You keep a list of **places that publish
events** and visit all of them every 12 hours. Whatever is on those pages today becomes your
database. Entries look like: `eventbrite.com/d/ca--san-francisco/events`,
`theindependentsf.com/calendar`, `events.stanford.edu`, `sfpl.org/events`,
`russiancentersf.com/events`.

"Events near Palo Alto, 15 miles, tonight" is then a **database question, not a search** — every
event already has a lat/long, so it's one SQL `WHERE` clause.

**Why not let the LLM web-search it:**
- **You can't verify it.** No source page, no way to know it's real or cancelled. Every crawled
  event carries the URL it came from.
- **Search engines don't index event pages fast enough.** An event posted Tuesday for Thursday
  may never be indexed.
- **You'd see the top ten results** of an index that already decided what's worth listing —
  precisely the long tail you're trying to beat.

**Your instinct is right, one layer up.** Search and the LLM are how you *build and grow the
list*: "list venues in Palo Alto that host public events", run monthly, human-reviewed, new URLs
added to the source table.

| Question | Answered by | How often |
|---|---|---|
| Who publishes events around here? | Search + LLM + you | Monthly, ~100 queries |
| What's on today? | The crawler | 2×/day, 800 pages |
| What's near Palo Alto tonight? | SQL query | Per user, instant |

Start by hand — 50–100 obvious sources is one afternoon and covers a surprising share. It grows
via monthly discovery, links found inside pages you already crawl, and organizers emailing you.

## 2. Photos — what actually works

**Grabbing from a search engine:** technically possible, legally the riskiest thing in the
design. Google Images is a set of *links to other people's photographs*; re-hosting them means
copying copyrighted images with no licence, and unlike text, photos have identifiable owners and
a DMCA complaint takes ten minutes. There's also no API — Google Images never had one, and Bing's
Image Search API died with the rest of Bing Search in August 2025.

**Asking the LLM for photos:** no, and this is a hard technical limit. **An LLM returns text.** It
cannot hand you an image file. It can return image *URLs*, and those are frequently invented —
plausible links that 404 or point at the wrong venue. Even with search on, you'd fetch and verify
every one, and still have no licence.

**Caching in Postgres — two different answers:**
- **Licensed API photos (Google, Tripadvisor, Foursquare): you may not cache them.** Terms forbid
  storing the content. Google lets you keep `place_id` forever and lat/long 30 days; everything
  else is fetch-fresh.
- **Photos you have rights to** (crawled flyers, venue site images, Wikimedia, user uploads): keep
  them, **but not inside Postgres.** Never store image bytes in Postgres — it bloats the DB, blows
  the free tier, and makes backups enormous. **Files go in object storage (R2); Postgres stores
  only the key.** Postgres holds facts, R2 holds pixels.

**Does the iPhone call the photo API directly? No — every API call goes through your backend.**
1. **API keys.** A key shipped inside an app can be extracted from the download in minutes, and
   then strangers spend your money.
2. **Budget control.** Only the server can count calls and cascade Tripadvisor → Google →
   Foursquare. A phone can't know the global count.
3. **Swapping providers** server-side is a deploy; in the app it's an App Store review.

The one exception: the backend returns the photo *URL*, and the phone loads the image bytes
directly from it. That part is normal and saves your bandwidth.

## 3. One paid server instead of five free services?

**Reasonable, and I'd support it.** For ~$12/month you trade five dashboards for one machine you
understand completely. It collapses the architecture from five places to three: **iPhone → your
server → outside APIs.** Cron runs the crawler, FastAPI serves the app, same box.

| | Free services | One paid VPS |
|---|---|---|
| Cost | $0 | $6–12/mo |
| Places to understand | Five | **One** |
| Background jobs | Scheduled runs only | **Real cron, no cold starts** |
| Debugging | Several consoles | **SSH in, one log** |
| Free-tier surprises | Yes — Oracle halved its allowance in June with no notice | **None** |
| Ops you own | **None** | 2–5 hrs/mo |
| If it dies at 2am | **Auto-restarts** | Down until you fix it |
| Scales to zero | **Yes** | No |

Prices: DigitalOcean from $4/mo ($6 for 1GB), Linode Nanode $5, Hetzner roughly 3–4× cheaper than
either for the same specs. A $12/month 2GB box is comfortable.

**Recommendation if you go this way: one VPS for the Python, but keep managed Postgres (Neon
free) rather than running the database on the box.** Every other VPS mistake is recoverable;
losing a database you forgot to back up is not.

## 4. Where logic lives once you have users

**All logic lives on the backend. The phone displays things and sends taps.** The reason is
specific to mobile: **changing backend logic is a deploy; changing phone logic is an App Store
review** — one to three days, and users who never update keep your old rules forever.

| Layer | What belongs there | What must never go there |
|---|---|---|
| iPhone | Screens, gestures, GPS, image rendering, offline copy | API keys, business rules, ranking |
| Backend (Python) | **Everything that decides:** auth, permissions, ranking, budget guards, moderation, notifications, all outside API calls | Image files |
| Postgres | Facts and relationships: events, venues, users, preferences, follows, RSVPs, photo *references* | Image/video bytes |
| Object storage (R2) | Photo and video *files*, user uploads | Anything you need to query |
| Outside APIs | Rented things: LLM, Places photos and reviews | Anything you must store |

**What adding users changes:**
- **The static-JSON option dies for good.** Accounts, preferences and uploads are all *writes*;
  GitHub Pages only serves files. This is also where the single-server answer above starts looking
  clearly right.
- **Filtering moves server-side.** Fine to filter 40 events on the phone at MVP; once you rank by
  preferences you can't ship the whole city to the phone, and you'll want to tune ranking without
  an App Store release.
- **User uploads never pass through your API server.** Phone asks the backend for a short-lived
  signed upload URL, uploads *directly* to R2, tells the backend the key.
- **New tables, same database:** `user`, `user_photo`, `preference`, `follow`, `rsvp`, `review`.
  Nothing about the crawler changes.
- **Moderation becomes a real job** the moment strangers upload photos — reporting, blocking, a
  review queue. Budget it as work.

**The good news:** none of this disturbs steps 1–4. The robot keeps collecting events exactly as
before. You're adding a second, independent half — the user half — and the two meet only in the
database.

---

# Follow-up, round two

## 1. Eventbrite, Luma, Facebook — a source is a URL with parameters

**You're right and I was sloppy.** `eventbrite.com` shows you nothing. But you don't "search" it
either — **these sites have listing URLs you construct once and fetch forever.** The search
happens in the URL, not in a prompt.

| Site | What the crawler actually fetches | Notes |
|---|---|---|
| Eventbrite | `/d/ca--san-francisco/all-events/?page=1…` | Caps at ~49 pages (~1,000 events) per search — split by category or date range |
| Luma | `lu.ma/sf` | City pages public, plus a **public JSON API behind them** — no HTML parsing |
| Resident Advisor | `ra.co/events/us/sanfrancisco` | Clean listing, great for nightlife |
| Dice | `dice.fm/browse/san-francisco` | Music-heavy |
| Meetup | `/find/?location=us--ca--San Francisco` | Browsable without the gated API |
| Ticketmaster | Discovery API | **Real API**, 5,000 calls/day free — use it, don't scrape |
| Venue calendars | `.ics` / RSS feeds | **Underrated** — structured, free, no LLM needed |

A row in your `source` table is a URL template plus a page range. The crawler expands and fetches.
**That is the search** — done once at setup, not per user.

**Facebook, honestly:** `facebook.com/events/explore/` requires login; the Events API was cut in
2018; public event pages are partly viewable logged out but usually hit a wall. Practical route:
search-API queries like `site:facebook.com/events "San Francisco"` to find public URLs, then fetch
each logged out. Expect ~half to work. A bonus source, never core coverage — the blocker is
technical reliability, not just terms.

## 2. What the crawler requests, and new sites

**Two different jobs — this is what was unclear:**

- **The crawler is dumb.** Reads the `source` table, fetches every URL in it, discovers nothing.
  Runs 2×/day.
- **A separate discovery job finds new sources.** Monthly. Four ways: search-API queries; **link
  mining** (while crawling, note outbound links to domains you don't have); LLM triage ("is this
  an event listing page?"); and you, by hand.
- **New sources land in a pending queue** you approve before they go live. Ten minutes a month,
  keeps junk out.

## 3. Event-goer only — confirmed

Drops out entirely: organizer accounts and verification; all organizer tools; attendance
prediction and venue analytics; payments and ticketing (link out instead).

**Keep one thing anyway:** still extract and store the organizer *name* on every event. Costs
nothing now, and it's what later powers "other events by this organizer" — free from your own
database. Throwing it away means re-crawling everything later.

## 4. Search-engine photos for the prototype

Understood — prototype, non-commercial, not shipping publicly.

**There's no Google Images API**, so go through a SERP provider. **Serper** has an images
endpoint: 1 credit per call, **~$1 per 1,000** (to $0.30 at volume), returning image URLs,
thumbnails, source page, dimensions and alt text as JSON.

- **Hot-link first, don't download.** Store the URL, let the phone load it. Zero storage, zero
  copying. Links rot, so re-fetch on a schedule.
- **If you cache bytes, cache to R2 with a TTL** — `photo_cache(venue_id, source_url, r2_key,
  fetched_at, expires_at)`, purged after 30 days. Never into Postgres.
- **Put it behind one interface** — a single `get_venue_photos(venue)` function. Going commercial
  later means changing one file, not twenty.

Keep it to TestFlight rather than a public App Store listing while this is the photo source. The
swap is cheap if the interface exists now.

## 5. Multimodal models — vision changes the answer

**A multimodal model can *look at* images. It still can't *find* them** — it has no photo library
of real places. Ask for "photos of Cafe Cocomo" and you get invented URLs, or a *generated*
picture that isn't the real venue.

Feed it images you already have and it becomes genuinely useful:

| Use | Value |
|---|---|
| **Read text out of flyer images** | **Big win.** Many events are posted as a picture with date, time and price *only* in the image. Nothing else can read that |
| Pick the best photo | "Which of these 10 shows the venue interior, which is a logo, which is a flyer?" |
| Sanity-check a match | "Does this plausibly show a nightclub?" — cheap filter against junk |
| Moderate uploads | Later |

Images cost ~1,000–1,600 input tokens each, so vision calls are a few times a text call — still
cents. Flyer-reading alone probably pays for itself in events you'd otherwise miss.

## 6. Python everywhere — confirmed

Nothing here needs JavaScript. Crawling: `httpx`, `selectolax`, `playwright`. Free extraction
tier: `extruct` (schema.org JSON-LD), `icalendar` (.ics). LLM: `anthropic` / `openai` /
`google-genai`. API: `FastAPI` + `uvicorn`. Database: `psycopg` or `SQLAlchemy` with
`GeoAlchemy2`. Dedup: `rapidfuzz`. The only Swift is the iPhone app.

## 7. What "dies" means, and what "ops" means

A VPS is **one computer**. Cloud Run runs many copies and replaces a broken one automatically; a
droplet doesn't unless you tell it to. Things that stop it: your Python process crashes and
nothing restarts it; the disk fills with logs or cached images; the OS needs a reboot.

**Nearly all of it is solved by two things:** a five-line `systemd` service file that restarts
your app whenever it exits, and a free uptime monitor that emails you if the site stops answering.
Do both on day one and "it dies" becomes "it restarted itself and I got an email."

**Correction to what I said earlier:** I quoted 2–5 hours/month of ops, which is a production
figure. For a prototype with systemd, Caddy for automatic HTTPS, and managed Postgres so backups
aren't yours, it's realistically **about an hour a month** — run updates, glance at disk space.

**"Ops" is just the chores of keeping a server running.** You *are* paying for hosting; hosting
buys you **the machine**, not someone to administer it. Shared hosting (GoDaddy) includes
administration but forbids background workers. A VPS is the opposite trade.

**What one droplet replaces:**

| Currently | On a VPS |
|---|---|
| GitHub Actions (crawler schedule) | → cron on the box |
| Google Cloud Run (read API) | → FastAPI behind Caddy |
| GitHub Pages (static files) | → Caddy, or not needed |
| Neon Postgres | Keep it — do not self-host the database |
| Cloudflare R2 | Keep it — $0 egress beats droplet bandwidth |
| Outside APIs | Unchanged |

One $6–12 box replaces **three** of six pieces: **iPhone → your droplet → Neon + R2 + outside APIs.**

## 8. Can Neon store photos and videos?

Technically yes. In practice it's the fastest way to destroy this setup — **Neon's free tier is
0.5 GB total.**

- **171 photos** at 3MB fill the entire free database
- **13 videos** at 40MB fill it
- **1,000,000 photo *references*** fit, and use only 190MB

Beyond space, blobs in Postgres hurt in ways that surface late: every backup copies them, every
restore downloads them, and Postgres caches table data in RAM — so photo bytes evict the event
rows your queries need and everything slows at once.

| Photos | Size | On R2 | In Neon free |
|---|---|---|---|
| 1,000 | 2.9 GB | $0 (within free 10GB) | Impossible |
| 10,000 | 29 GB | $0.29/mo | Impossible |
| 100,000 | 293 GB | $4.24/mo | Impossible |

**The rule:** Postgres stores the *row* — `venue_id, r2_key, width, height, source, license`,
about 200 bytes. R2 stores the *file*.
