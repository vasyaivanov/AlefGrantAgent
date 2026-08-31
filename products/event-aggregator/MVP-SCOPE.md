# Minimum MVP — scoped for lowest spend

Assessment date: 31 August 2026. Companion to the other assessments in this folder.

---

## The trap to avoid first

The instinct is to build the aggregator, because it is the fun engineering and it feels like
the product. **Don't.** The prior assessments established that aggregation is cheap
(~$12–50/month for one vertical), not defensible (anyone can rescrape), and not in doubt
(it obviously works). Building it first spends your money proving the one thing nobody
questions.

**The riskiest assumptions are elsewhere**, and they are cheap to test:

| Assumption | If false | Cost to test |
|---|---|---|
| Anyone wants a curated list at all | Product dies | **$0** |
| They come back a second and third time | Product dies (1–2×/month frequency) | **$0** |
| Anyone will write a review of a venue or organizer | The moat never forms | ~$90/month |
| Organizers will engage | No revenue path | ~$0 incremental |
| Organizers will pay | No business | Later |

The first two cost nothing and are the most likely to be false. Test them before writing
application code.

---

## Phase 0 — the $0 demand test (2–3 weeks, ~$50 total)

Before any product exists:

- **One vertical, one neighborhood.** Not the Bay Area, not 60 miles, not all events. Pick a
  category where the long tail is the whole point and incumbents are weakest — social dance,
  underground music, or lectures — in one part of San Francisco.
- **Hand-curate 30–50 events a week into a weekly email.** You, manually, in a spreadsheet.
- **A one-page site** to collect subscribers.

Cost: a domain and an email tool. **Under $50/month.**

What it measures: signup rate, open rate, click-through, and — the one that matters —
**repeat opens over six weeks**. If people don't open week four, no amount of engineering
saves this.

What it also produces, free: organizers will email asking to be included. That is inbound
supply and the beginning of your organizer relationship book — the actual moat — acquired at
zero cost. Every city guide worth anything started this way.

**If Phase 0 fails, you have spent $50 instead of $2M.** That is the entire point.

---

## Phase 1 — the MVP (8–12 weeks, ~$90/month)

Only if Phase 0 retains. Scope:

### The seven features

1. **Event list** — one vertical, one city, filtered by date. Aggregated from 5–10 easy sources
   plus manual entry as the fallback. Manual entry is not a failure; it is the thing that keeps
   quality high while coverage is small.
2. **Event detail page** — time, venue, price, link out to buy. Link the flyer, don't host it
   (see the copyright note in the legal assessment).
3. **Venue pages and organizer pages.** These are the durable objects. Events evaporate; venues
   and organizers persist and accumulate. This is the moat, and it is the single most important
   thing in the MVP.
4. **Reviews and photos** on venue and organizer pages. Login required to write, not to read.
5. **A "Going" button.** Cheap to build, disproportionately valuable: it is your intent signal,
   your retention hook, the seed of the in-app social graph (the only version that works), and
   the beginning of the attendance data you'd need years from now.
6. **Organizer self-serve** — claim your venue or organizer page, add an event. That's it.
7. **The weekly email digest**, carried over from Phase 0. For a product people use once or twice
   a month, this is the retention mechanism. Most founders drop it once the app exists; that is a
   mistake.

### The stack that keeps it at $90/month

| Item | Choice | $/mo |
|---|---|---|
| Hosting | Vercel or Railway | $20 |
| Database | Neon or Supabase Postgres + PostGIS | $25 |
| Object storage | Cloudflare R2 — no egress fees | $5 |
| Email | Resend or Buttondown | $20 |
| LLM extraction | Haiku 4.5, cached and batched | $15 |
| Place data | Overture Maps / OSM — **not Google Places** | $0 |
| Auth, analytics, error tracking | Free tiers | $0 |
| Domain | | $2 |
| | **Total** | **~$87** |

The extraction math: ~300 sources × 3 pages × 2 sweeps/week ≈ 7,700 pages/month, ~40% free via
schema.org JSON-LD, leaving ~4,600 LLM pages. On Haiku 4.5 with caching and the Batch API that
is **$12/month**. The data pipeline is not where your money goes.

**Web app only — a PWA, no native apps.** This is the single largest saving available. Native
iOS and Android roughly triples front-end cost, adds app-store review cycles to every release,
and buys nothing an MVP needs. Ship native when retention justifies it.

**No proxies, no anti-bot spend.** At this volume, scrape only the sources that don't fight you
and hand-enter the rest. Anti-bot infrastructure is a scale problem you do not have yet.

---

## What to cut, and why

Everything below is in the original spec and none of it belongs in the MVP.

| Cut | Reason |
|---|---|
| Native iOS and Android apps | PWA does the job; saves the largest single line item |
| The 60-mile radius | Start with a few neighborhoods. Coverage of a small area beats thin coverage of a large one |
| Full category taxonomy | One vertical. Breadth is what makes you indistinguishable from Google |
| Friend graph from social networks | Technically dead since 2015/2018 |
| Scraped reviews and venue photos | Blocked by platform terms, and event reviews don't exist to scrape |
| Attendance prediction | No training data exists yet, including yours |
| Discount code scraping | Mostly expired junk; dead codes destroy trust faster than the feature builds it |
| Venue owner background checks | FCRA exposure. Do not build this |
| Insurance, rentals, staffing, contracts | Ops-heavy, integration-heavy, teaches you nothing at this stage |
| Ticketing and payments | Money-transmitter licensing plus real scope. Link out for now |
| Live event features, "connect with someone" | Needs density you don't have, plus a trust-and-safety workstream |
| Multi-network posting for organizers | Per-platform approval gauntlet. Later, via an aggregation vendor |
| Sophisticated dedup | With 5–10 sources in one vertical, simple matching suffices |

---

## What this actually costs

| Line | Cost |
|---|---|
| Phase 0 (3 weeks) | **~$50 total** |
| Phase 1 services | **~$90/month** |
| Phase 1 engineering — you build it | **$0 cash**, 8–12 weeks |
| Phase 1 engineering — one contract engineer | **$15–30k** |
| Phase 1 engineering — agency | $60–120k — don't |

**The services are noise. The only real variable is whether you write the code.** If you can
build Phase 1 yourself, the entire experiment — demand test through working product — runs
under **$400 in cash** over four months.

---

## If you only need a demo

Different goal, different answer. To show something to investors or design partners:

- A clickable prototype with 50 **real, hand-entered** events in one neighborhood, plus two or
  three fully populated venue pages showing what reviews and photos look like once they exist.
- 1–2 weeks, **$0–500**.

Use real events and real venues. A demo full of invented data is obvious to anyone who knows the
scene, and the venue pages are the part worth showing — they are the thing that isn't just
another listings site.

Be clear with yourself about what this proves: a demo tests whether people find the idea
appealing, which they usually say they do. Phase 0 tests whether they'd actually use it. Only
one of those is information.

---

## The sequencing

```
Phase 0   newsletter, hand-curated, one vertical, one neighborhood     $50      3 weeks
             ↓  kill here if week-4 opens don't hold
Phase 1   web app: events + venue/organizer pages + reviews + digest   $90/mo   8-12 weeks
             ↓  kill here if nobody writes a review
Phase 2   second vertical, or organizer paid tools                     — only now
```

Each gate is designed to kill the idea before the next one costs more. The order matters more
than the feature list: **the cheapest tests come first, and they are the ones most likely to
fail.**
