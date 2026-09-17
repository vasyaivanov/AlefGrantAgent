# Architecture — iPhone app + cheap backend, SF Bay Area

Design date: 17 September 2026. Companion to the feasibility assessments in this folder.
No code; this is the design and the hosting decisions.

---

## The one decision everything else follows from

**The LLM never touches the request path.**

A background job crawls and extracts on a schedule and writes finished rows to a database. When
the phone opens, the backend does a database read and returns JSON. That's it.

Everything cheap about this design comes from that rule:

- The phone request is a single indexed query — **sub-100ms**, no LLM latency, no per-user
  inference cost, no rate limits, no timeouts.
- The LLM work becomes a **batch** job with no latency requirement — so it gets the Batch API's
  50% discount and can retry freely.
- The read API becomes so trivial that **any free tier can host it.**
- Limiting to one metro means there is exactly **one** precompute job. This is the real reason to
  start with the Bay Area only.

So the answer to "should we have a constant background process so responses are instant" is
**yes — but scheduled, not constant.** A permanently running process bills continuously on every
platform because it never scales to zero. A cron job that runs four times a day for twenty
minutes is effectively free.

Three different cadences, three different costs:

| Job | Cadence | Cost |
|---|---|---|
| Full crawl and LLM extraction | 2×/day | The only real spend |
| Freshness check on *today's* events (HTTP ETag / If-Modified-Since, no LLM) | every 2–3 hours | ~$0 |
| "Hasn't happened yet" filter | at read time, from the stored start time | $0 |

That last row matters for your open-the-app requirement: *"today, not yet started"* is a `WHERE`
clause, not a job.

---

## Hosting

### The recommendation

| Component | Service | Why | $/mo |
|---|---|---|---|
| Read API | **Google Cloud Run** | 2M requests/month always free, scales to zero, no credit-card surprise | $0 |
| Ingestion worker | **Cloud Run Jobs + Cloud Scheduler** | Same project, same free tier, cron built in | $0 |
| Database | **Neon** or **Supabase** Postgres free tier | Postgres + PostGIS for the radius query | $0 |
| Images | **Cloudflare R2** | No egress fees — the thing that bites you elsewhere | $0–5 |
| Domain | GoDaddy, Namecheap, Cloudflare — anyone | | ~$1 |

Cloud Run's free tier covers roughly **10,000–13,000 daily active users** before you pay anything.
The binding constraint is the 180,000 vCPU-seconds/month allowance rather than the 2M request
count — at ~100ms per request that works out to about 1.8M requests. Either way, a prototype will
not come close.

### Alternatives worth knowing

- **Cloudflare Workers** — 100,000 requests/day free, excellent edge performance. Good for the
  read API only; it forces JavaScript/TypeScript on a non-Node runtime, which fights the Python
  crawling stack.
- **Oracle Cloud Always Free** — a real always-free Linux VM you fully control, which suits a
  crawler well. Two caveats: Oracle **quietly halved the ARM allowance from 4 OCPU/24GB to
  2 OCPU/12GB on 15 June 2026 with no announcement**, and capacity in popular regions is often
  unavailable. Usable, but don't build something you can't move.
- **Render** — the last mainstream PaaS with genuinely free-forever compute. One trap: **the free
  Postgres expires after 30 days.** Free web services also sleep when idle.
- **Railway** — free tier gone. **Fly.io** — free tier retired October 2024. Both now require a
  card for anything real.

### Can GitHub be the backend?

**GitHub Pages: no.** It is explicitly static-only — no server-side code, no database.

**But GitHub Actions + Pages genuinely works as a $0 backend for your prototype**, and it's worth
taking seriously, because your data is precomputed and read-only:

- **GitHub Actions** runs the crawl on a cron — 2,000 free Linux minutes/month on private repos
  (~66 min/day), unlimited on public ones.
- It commits a file like `bay-area/2026-09-17.json` to the repo.
- **GitHub Pages** serves it over a CDN — 100GB/month soft bandwidth limit.
- The iPhone app downloads one day's file and **applies every filter locally**.

That last point is the trick. One metro-day is roughly 500 events × ~1.5KB ≈ **750KB, or ~150KB
gzipped.** All five of your filters — date, time, event type, language, 15-mile radius — are
client-side operations on a payload that small. You need no query API at all.

**Where it breaks:** no per-user state, so no reviews, no "Going", no accounts. Daily commits
bloat git history. 1GB repo and site limits. And using Actions as general-purpose compute is a
soft terms-of-service gray area — fine at prototype scale, not something to build a company on.

**Verdict:** legitimate for the read-only prototype, not for the MVP once users write anything.
Budget a weekend to move off it.

### Can GoDaddy, 101domains, or similar be the backend?

**No. Use them for the domain only** — which is what they're actually good at.

Their shared cPanel hosting will not do this job:

- **Node.js is not officially supported** on GoDaddy shared hosting; every path is an NVM
  workaround requiring terminal access you may not have.
- Python works via Passenger ("Setup Python App"), but fragilely.
- **The killer: you cannot run persistent background workers.** Shared hosts terminate
  long-running processes. Cron jobs exist but are constrained, and your crawler is exactly the
  kind of process they kill.
- No modern deploy pipeline, no scale-to-zero, no managed Postgres.

Their VPS tier would technically work, but costs $20–60/month for less capability than Cloud Run
gives you free.

---

## Node.js or Python?

**Python for the ingestion worker. Either for the read API. If you want one language, pick
Python.**

The split is natural because the two halves have genuinely different needs:

**Ingestion — Python wins clearly.** This is its home turf:
- `extruct` parses schema.org JSON-LD, which is your free extraction tier and handles ~40% of
  pages at zero LLM cost
- `httpx`, `selectolax` / BeautifulSoup for fetch and parse
- `playwright` for the handful of pages that need rendering
- `rapidfuzz`, `shapely`, `scikit-learn` when dedup and geo work start mattering

The JS equivalents exist but are thinner, and you'd be fighting the ecosystem for no gain.

**Read API — a coin flip.** It's database reads and JSON serialization. FastAPI or Express both
do it in an afternoon. TypeScript buys you shared types with the front end; Python buys you one
language across the whole backend.

**The LLM part is a wash** — Anthropic and OpenAI both ship first-class SDKs for Python and
TypeScript, with identical capabilities.

**Recommendation: Python for both**, unless your team is JavaScript-native, in which case Node for
the API and Python for the worker is fine. One exception: if you choose Cloudflare Workers for the
read API, that decision forces TypeScript.

---

## Self-hosted Qwen, or a paid API?

**Use the paid API. Self-hosting is both slower and more expensive here, and on a free tier it is
arithmetically impossible.**

Your extraction workload is roughly 35,000 pages/month for a Bay Area MVP, at ~600 output tokens
per page — **about 21 million output tokens a month.**

**On a free-tier CPU box** (Oracle Always Free, 2 OCPU / 12GB ARM after the June cut — and note
that no free tier anywhere includes a GPU), a quantized 7B model runs at maybe 3–15 tokens/sec:

| Throughput | Compute needed per month |
|---|---|
| 3 tok/s | **81 days** |
| 5 tok/s | **49 days** |
| 15 tok/s (optimistic) | **16 days** |

A month has 30. At realistic CPU speeds you cannot finish the work in the month it arrives.

**On a rented GPU**, the cheapest credible options run ~$0.35–0.55/hour — about **$256–400/month**
for an always-on RTX A6000 or 4090 class card. Cheaper spot capacity exists but adds
interruption handling.

**On Haiku 4.5, batched and cached: $44–147/month**, with a better model, no ops burden, and no
GPU to babysit.

So self-hosting costs **2–9× more** for worse extraction quality. The break-even for self-hosting
generally lands somewhere around millions of tokens *per day*; you're at under a million. Add
10–20 hours/month of maintenance and the gap widens further.

Revisit this only if volume grows by roughly two orders of magnitude, and even then, the first
thing to self-host is *classification* (short outputs, high volume, simple) — not extraction.

---

## Web search — yes, but not where you think

Add search, but understand what it's for. **Search is how you discover sources you don't know
about. Crawling is how you get events.** Keep them separate:

| Job | Tool | Cadence |
|---|---|---|
| Get events from known sources | Your crawler + LLM extraction | 2×/day |
| Find *new* sources you're missing | Search API | weekly or monthly |
| Answer a user's query | Database read | per request |

Search must never be in the request path or the per-event path. Used for discovery it's a few
hundred queries a month; used per-event it's the quadratic cost problem from the earlier cost
model.

### Can you use Google Search API free, and fall back when it starts charging?

**No — and not because of the budget logic, which is sound. The APIs are simply gone.**

- **Google Custom Search JSON API is closed to new customers** and **shuts down 1 January 2027.**
  You cannot sign up. Existing customers pay $5/1,000 after 100 free queries/day.
- **Bing Search API was retired 11 August 2025.** No Microsoft replacement.
- **Brave killed its free tier in February 2026**, moving to ~$5/1,000 with a $5 monthly credit —
  effectively about 1,000 free queries a month.

**There is no free web search API left.** The cheapest credible paid options are **Serper** (~$1
per 1,000 at a $50 prepaid minimum, less at volume) and **Parallel** (~$1 per 1,000). Exa runs ~$7
and is AI-native.

**Your fallback pattern is still exactly right — just point it at Serper or Brave.** Implement it
as a budget guard: store a monthly query allowance in the database, decrement it atomically per
call, and when it hits zero the discovery job skips search entirely and continues crawling. Roughly
twenty lines, and it makes the spend a hard ceiling rather than a surprise. Do this regardless of
provider.

---

## Should you use an agent?

**No — not for ingestion.**

An agent earns its cost when the steps can't be specified in advance. Yours can: fetch → try
JSON-LD → fall back to one structured-output LLM call → validate against schema → write row. A
deterministic pipeline is cheaper, faster, debuggable, reproducible, and trivially retryable.

An agentic loop would reintroduce exactly the problem from the cost model — accumulated tool
results re-billed on every turn, so input cost grows with the square of the tool-call count — in
exchange for flexibility a fixed pipeline doesn't need.

**Where an agent might earn its place later**, neither at MVP:
- **Source discovery** — genuinely open-ended ("find Russian-language event sources in the Bay
  Area I don't already have"), run monthly, small volume.
- **Dedup adjudication** on borderline pairs, where the candidate set is small and a wrong merge
  is costly.

Use structured outputs with a strict JSON schema for extraction. That gives you the reliability
people reach for agents to get.

---

## The part of your spec that can't be built as described

You asked for, on each event: venue info, organizer info, **photos of the organizer's previous
events, photos of the venue, and reviews of the venue and organizer.**

Two of those cannot be obtained by crawling at any price, per the technical and legal assessments:

- **Photos.** Instagram removed the Places tab in 2026 and has stripped location fields from the
  API; there is no supported venue-photo harvesting path. Stories have no third-party read access
  at all. And harvested photos arrive with no licence to display.
- **Reviews.** Google Places returns ~5 reviews with no storage rights; Yelp Fusion returns 3
  excerpts with none. More fundamentally, reviews *of events and organizers* don't exist anywhere
  to take.

**What to build instead, all of it legal and free:**

| Field | Honest source |
|---|---|
| Venue info | Overture Maps / OSM as the spine, plus the venue's own site. Not Google Places — its terms restrict storing fields beyond the place ID |
| Venue photos | The venue's own site images, hot-linked with attribution, or your own photographs |
| Organizer info | Their own public page, extracted like any other |
| Organizer's past events | **You already have this** — it's a query over your own events table once you've been crawling a few weeks. This one is free and genuinely good |
| Reviews | Start empty with a "be the first" state. Seed by writing honest first-party notes on the top ~50 venues yourself |
| Star rating | You *may* be able to show a Google or Yelp rating number with attribution and a link out under their terms — but you cannot store or mirror review text. Check the current terms before depending on it |

The organizer's-past-events row is worth dwelling on: it costs nothing, requires no third party,
and gets better every week you run. It is the closest thing in this spec to a compounding asset.

---

## Your language filter is the best idea in the spec

English, Chinese, Russian, Spanish, Arabic — in the Bay Area this is not a nice-to-have, it's a
wedge:

- These communities are **geographically concentrated** (Chinese in the Sunset, Richmond and
  Millbrae; Russian in the Richmond; Spanish in the Mission), which works *with* your 15-mile
  radius instead of against it.
- Their events are **precisely the long tail Google and Eventbrite miss** — WeChat groups,
  community centres, churches, cultural associations.
- **Nobody offers this filter.** It is a real, defensible differentiator, unlike "more complete
  listings."

Detection is free: add a `language` field to the extraction schema. The model is already reading
the page.

**Recommendation: pick one language community and go deep** rather than shipping all five thin.
That gives you the single-vertical focus the MVP assessment argued for, with a sharper edge than
picking an event category.

---

## Data model sketch

Five tables carry the whole MVP:

```
venue        id, name, geog(Point), address, overture_id, website, photos[], attrs{}
organizer    id, name, website, socials{}, claimed_by
event        id, venue_id, organizer_id, starts_at, ends_at, title, description,
             price_min, price_max, ticket_url, flyer_url, category, language,
             source_id, dedup_key, last_seen_at, cancelled_at
source       id, url, kind(api|feed|jsonld|render), last_crawled_at, failure_count
review       id, subject_type(venue|organizer), subject_id, user_id, rating, body
```

The open-the-app query is one indexed read:

```
WHERE starts_at BETWEEN now() AND end_of_local_day
  AND cancelled_at IS NULL
  AND ST_DWithin(venue.geog, user_point, 24140)   -- 15 miles in metres
ORDER BY starts_at
```

Index on `(starts_at)` and a GiST index on `venue.geog`. Everything else — type, language, time
band — is a filter on an already-small result set.

---

## What this costs

| Line | $/mo |
|---|---|
| Apple Developer Program ($99/year — required for TestFlight and the App Store) | $8 |
| Cloud Run (API + jobs) | $0 |
| Postgres (Neon / Supabase free) | $0 |
| Cloudflare R2 | $0–5 |
| LLM extraction (Haiku 4.5, batched + cached) | $30–60 |
| Search API for source discovery, hard-capped | $0–10 |
| Domain | $1 |
| **Total** | **~$40–85/month** |

Plus the one-time Apple Developer signup. Everything else is your time.

---

## Build order

1. **The ingestion worker first, run locally.** No hosting, no app. Prove you can produce a clean
   table of today's Bay Area events with a language field. If this doesn't work, nothing else
   matters.
2. **Put it on a schedule** — Cloud Run Job, or GitHub Actions if you want to defer even that.
3. **The read API** — one endpoint, one query.
4. **The iPhone app** — list, detail, the five filters. Filters run client-side at this size.
5. **Accounts, reviews and "Going"** — only now, and this is the point where you must be off
   GitHub Pages.

Steps 1–4 have no user state, which is what keeps them nearly free. Step 5 is where the real
product starts and where the moat begins to form.

One note on the front end: you've specified a native iPhone app, and this design assumes it. Be
aware it roughly triples front-end effort versus a PWA and adds App Store review to every release.
If that's a deliberate call — native feel, push notifications, camera for photo upload — it's a
reasonable one. Just make it knowingly.
