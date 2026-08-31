# "Yelp for events" — technical feasibility

Assessment date: 31 August 2026. Scope: **technical feasibility only.** Business and legal
feasibility are assessed separately; where a technical path runs into a legal wall I note the
collision and move on rather than analyzing it.

This document is unrelated to the Alef Aeronautics grant work in the rest of this repository.
It lives here because it was requested in this workspace.

---

## 1. The verdict

**Half of this product is buildable today. A quarter of it is buildable but is a permanent,
expensive maintenance obligation rather than a project. A quarter of it cannot be built as
specified, and no amount of engineering fixes it.**

The thing to understand before anything else: this spec is three different products wearing one
coat.

1. **An event aggregator.** Scrape, normalize, dedupe, classify, serve. This is real engineering
   with a known shape. It is tractable. It is also never finished.
2. **A Yelp layer** — reviews, photos, friend graph, venue Q&A. This is written in the spec as a
   scraping problem. It is not a scraping problem. It is a cold-start supply problem, and the
   specific data sources it assumes have been closed off by the platforms that hold them. This is
   where the plan breaks.
3. **A B2B organizer services marketplace** — insurance, rentals, printing, staffing, contracts,
   flyer distribution. Technically the easiest part of the whole spec. Operationally the heaviest.
   Almost none of the difficulty here is code.

The failure mode I would expect is a team spending eighteen months building (1) very well,
discovering that (2) is empty because nobody has written a review yet, and never getting to (3).

The single most important finding: **the marquee differentiator — "shows your friends who attended
this venue, this organizer, and who RSVPed to this event" — is technically blocked, not
technically hard.** Details in section 4.

---

## 2. Feature triage

Every requirement in the spec, sorted by what kind of problem it actually is.

### Tier A — buildable now, low technical risk

| Feature | Notes |
|---|---|
| Standardized event info (time, description, flyer, price) | Solved shape. LLM extraction made this cheap; see §3.2. |
| Event classification (dancing, lectures, theater, networking…) | Embeddings + few-shot LLM. A ~40-class taxonomy is a two-week problem, not a research problem. |
| Links to buy tickets | Trivial. Deep-link out or affiliate. |
| Organizer creates event natively on the platform | Ordinary CRUD. |
| Organizer offers platform-specific discounts | Ordinary CRUD. |
| Flyer / poster generation | Image generation plus templating. Genuinely easy in 2026 and genuinely good. |
| Print-and-mail flyers | Commodity print-on-demand APIs. Integration, not invention. |
| Contract generation (venue ↔ organizer) | Templates plus LLM fill. Technically trivial. Legally loaded — flagged for the legal pass. |
| Aggregation from the ~10 large API-bearing sources | See §3.1. Straightforward, but covers a narrow slice. |

### Tier B — buildable, but they are ongoing obligations, not features

| Feature | Notes |
|---|---|
| Long-tail scraping ("all public events in a 60-mile radius") | The core engineering lift. Asymptotic coverage, permanent maintenance. §3. |
| Deduplication across sources | The silent killer. Gets you good or gets you dead. §3.3. |
| Venue and organizer canonical database | Needs a licensed or open place spine. §3.4. |
| Cancellation and change detection | Harder than initial ingestion. Sites delete pages silently. |
| Discount code scraping | Doable, mostly worthless without validation. §5.3. |
| Live/post-event photo feed | Only as first-party UGC. The scraped version is blocked. §4.2. |
| Multi-network social posting on organizer's behalf | Per-platform approval gauntlet, permanently fragile. §5.1. |
| Connect with someone you saw at the event | Easy code, hard safety design. §5.4. |

### Tier C — technically blocked. Engineering does not solve these.

| Feature | Why it's blocked |
|---|---|
| Friends (from social networks) who attended this venue/organizer | Facebook's friends-data API shut down 30 April 2015. There is no third-party friend graph on Instagram or TikTok. §4.1. |
| Friends who RSVPed on any site to this event | Facebook cut third-party access to event guest lists in April 2018. Every other platform treats attendee lists as private. §4.1. |
| Photos of other events at this venue / by this organizer (scraped) | Instagram removed the Places tab in 2026 and has been stripping location fields from the API; there is no supported venue-photo harvesting path. §4.2. |
| User reviews for venue and organizer (scraped) | Google Places allows ~5 reviews with no storage rights; Yelp Fusion allows 3 excerpts with no storage. Both are technically fenced. And event reviews do not exist to scrape in the first place. §4.3. |

### Tier D — not engineering problems. Data, liquidity, or operations problems.

| Feature | The real constraint |
|---|---|
| User reviews for venues and organizers | Nobody has written them yet. This is Yelp's twenty-year moat and it is made of users, not code. §4.3. |
| Venue common-question answers (coat check, entry rules, food/alcohol) | No source exists. Must be user-contributed structured Q&A. |
| Attendance prediction for organizers | No labeled training data exists anywhere, including inside your platform on day one. §4.4. |
| Venue demographics | Purchasable (foot-traffic vendors), not derivable. §5.2. |
| Suggests and connects collaborating organizers/promoters | Needs a dense two-sided network before the matching means anything. |
| Physical flyer distribution (guerrilla marketing) | A gig-labor operations business. Roughly zero of the hard part is software. |
| Hiring through a third-party system with local ratings | Upwork's public API is not meaningfully open to this. Realistically you build a light marketplace yourself. |
| Venue insurance / alcohol insurance | Feasible only as a broker referral or embedded-insurance integration. You are not underwriting. |
| Full due diligence background on the venue owner | Data is purchasable from registry and court aggregators. Selling it as a background report on a person collides hard with FCRA. Flagged for the legal pass. |

---

## 3. The aggregator: what it actually takes

This part is feasible. Here is the honest shape of it.

### 3.1 Coverage is an asymptote, and the valuable part is the tail

"All public events within 60 miles" is not achievable. What is achievable is a coverage curve, and
the curve has a nasty property: **the sources that are easy to ingest carry the events your users
care least about.**

- **Roughly 10 sources with APIs or stable feeds** — Ticketmaster/Live Nation, AXS, SeatGeek,
  Dice, Eventbrite (partial), Bandsintown, Songkick, Luma, Meetup, StubHub — cover most *ticketed*
  volume. These are arena shows, comedy clubs, and tech meetups. They are also already well served
  by existing apps.
- **The long tail** — the warehouse party, the salsa night, the gallery opening, the church
  fundraiser, the university lecture — lives on a few thousand heterogeneous websites per metro,
  plus municipal and library calendars, plus alt-weekly listings. This is where a "Yelp for
  events" earns its existence, and it is the expensive half.
- **The invisible tier** — Facebook Events, Instagram posts, Discord and WhatsApp groups. A large
  share of nightlife and party culture lives here, and it is behind walls that do not open. You
  will not get it, and competitors will not either.

Two API constraints worth knowing before planning around them:

- **Eventbrite killed public event search in February 2020.** You can retrieve an event by ID or
  list events by venue, but there is no supported way to ask "what's happening near me." For an
  aggregator this is a significant hole in one of the most obvious sources.
- **Meetup consolidated onto a gated GraphQL API in February 2025.** Access is tied to OAuth and,
  for anything beyond basic search, a Meetup Pro subscription — and approval is discretionary.
- Ticketmaster's Discovery API defaults to 5,000 calls/day at 5 req/s. Commercial volume is a
  conversation with their developer relations team, not a self-serve upgrade.

Realistic target: **60–75% of the discoverable long tail in a launch metro after a year of work.**
Anyone promising more is not counting the group chats.

### 3.2 Extraction is the part that got cheap

This is the genuine change that makes the idea more feasible in 2026 than it was in 2016. You no
longer write a bespoke parser per site.

Build a three-tier extraction ladder and always try the cheap tier first:

1. **schema.org/Event JSON-LD.** Google's event rich-results program pushed adoption hard;
   a large share of venue and ticketing pages emit structured event markup. Free, instant,
   high precision. This should be your first attempt on every page.
2. **Site-specific adapters** for the ~50 highest-volume sources per market, where the volume
   justifies the maintenance.
3. **Generic LLM extraction** — cleaned DOM to a JSON schema — for everything else.

Cost arithmetic for tier 3, since this is usually where people assume the project dies:

- A cleaned page is roughly 4k input tokens and 600 output tokens of JSON.
- At small-model pricing (~$1/MTok in, ~$5/MTok out) that is about **$0.007 per page.**
- One metro with a 3,000-site tail, five pages each, recrawled twice weekly ≈ **130k pages/month.**
- Extraction: **~$900/month.** Fetching: **$250–1,000/month** depending on how much of the tail
  sits behind bot management.

So a launch metro runs roughly **$2–4k/month** in fetch-and-extract infrastructure, all in. Top-50
metros nationally lands around **$40–80k/month**, and the JSON-LD tier plus batch and prompt
caching cuts that materially.

**The compute is not the problem. The headcount is.** Rule of thumb: one ingestion engineer per
150–300 actively maintained bespoke sources. Generic LLM extraction is what makes that ratio
survivable — before it, the number was closer to 50. National long-tail coverage still implies a
permanent 3–6 person ingestion team whose entire job is that sites keep changing.

### 3.3 Deduplication is the thing that will actually hurt you

One salsa night appears on Eventbrite, Resident Advisor, the venue's own site, a city guide, and
Instagram. Five different titles, three different start times (doors versus set time), four
different prices (tiered), and venue strings that don't match. If you show it five times, users
leave. If you merge two genuinely different events, you send someone to the wrong room.

The asymmetry matters: **you need very high precision on merges, and you can afford softer
recall.** A visible duplicate is annoying. A bad merge is a broken promise.

The workable pipeline is blocking on (geo, date) → embedding similarity on title and description →
deterministic checks on venue and time → LLM adjudication only on the borderline pairs. That last
tier is affordable precisely because blocking keeps the candidate set small.

Budget two engineers for six months to reach acceptable, and accept that it is never done. In
every aggregator I know of, duplicate listings are the number one user-visible quality complaint.

### 3.4 You need a venue master database, and you should not build it from scratch

Everything in the spec keys off the venue: photos at that venue, reviews of that venue, friends who
went to that venue, capacity, demographics. So venue identity has to be rock solid, and free-text
venue names from scraped pages will not get you there.

Note a trap: **Google Places terms restrict caching and storing most fields beyond the place ID**,
which makes it a poor spine for a product whose whole design is built on persistent venue records.
The better options are the open place datasets — Foursquare's open-sourced Places data and Overture
Maps — as the canonical spine, with a geocoder for resolution and your own enrichment layer on top.
Decide this early; retrofitting venue identity later is brutal.

### 3.5 Reference architecture

```
source registry (per-source: API | feed | sitemap | headless render | manual)
        ↓
fetch layer — proxy pool + anti-bot service, per-domain politeness budgets, robots handling
        ↓
extraction ladder — JSON-LD → site adapter → LLM structured extraction
        ↓
canonicalization — venue resolver (Overture/FSQ spine) · organizer resolver · geocoding
        ↓
entity resolution — blocking → embeddings → LLM adjudication → event cluster
        ↓
enrichment — classification · price normalization · flyer extraction · freshness & cancellation
        ↓
serving — Postgres + PostGIS, geo/time faceted search, pgvector or OpenSearch
        ↓
apps — iOS · Android · web · organizer console
        ↓
UGC layer — reviews, photos, RSVPs, in-app social graph, moderation pipeline
```

Nothing here is exotic. That is the point: the aggregator is a known quantity, and the risk sits in
maintenance load and data quality, not in architecture.

---

## 4. The four things that don't work as written

### 4.1 The friend graph is closed

The spec's most differentiating feature depends on data that no longer leaves the platforms.

- **Facebook friends.** The friends-data API was announced dead at F8 2014 and shut off
  **30 April 2015**. What survives is `user_friends`, which returns only friends who have *also*
  installed your app and granted permission, and requires App Review. For a new app that set is
  empty, and it stays near-empty until you are already huge.
- **Facebook event guest lists.** Cut off in **April 2018** — apps lost access to guest lists and
  event walls in the post-Cambridge-Analytica lockdown. Meta has only tightened since, deprecating
  Groups API endpoints in 2024.
- **Instagram / TikTok.** No third-party friend or following graph exists at all.
- **"Who RSVPed on any site to this particular event."** Attendee lists are private on Eventbrite,
  Meetup, Luma, Partiful, and Dice. There is no consented, supported path to them.

What you can actually build:

- An **in-app social graph** (follow / mutual follow) — real, and the only durable version.
- **Contact-book matching** via hashed phone/email — works, is increasingly friction-laden on iOS,
  and is privacy-hostile enough to deserve care.
- **Public attendance signals** where a platform genuinely exposes them (a few niche music
  platforms show public "interested" counts) — thin, inconsistent, not a friend graph.

So the honest version of this feature is: *your friends on this app who went to this venue.* That
only becomes valuable at local density, which is a network-effects problem, not an engineering one.
**Do not put this feature in the pitch as though it works on day one.**

### 4.2 Event and venue photos cannot be harvested

"Photos of other events at that venue," "photos by other events of this organizer," and "scrapes
for photos and live stories from this particular event" all assume Instagram is queryable by place
and moment. It is not.

- Instagram **removed the Places tab from search in 2026**, and has been stripping location fields
  from the Graph API to reduce privacy exposure.
- Hashtag search requires approved Graph API access, is heavily rate-limited, returns recent media
  only, and does not give you venue-accurate results.
- **Stories are ephemeral and have no third-party read path.** "Live stories from this event" has
  no supported implementation.
- Even setting access aside, harvested photos arrive with no license to display them.

The buildable version is **first-party UGC**: users post photos to an event page, and those photos
roll up to the venue and organizer over time. Same feature on the screen, completely different
supply model — and it is empty until you have users at events.

### 4.3 Reviews have to be grown, and that's the whole ballgame

The spec treats reviews as something to scrape. Two independent reasons that fails:

1. **The APIs are fenced.** Google Places returns about five reviews with no storage rights. Yelp
   Fusion returns three excerpts, no storage, and is now paid. Neither permits building a review
   corpus.
2. **More fundamentally, the reviews you want do not exist anywhere.** Yelp has restaurant reviews.
   Google has business reviews. Nobody has a large corpus of reviews *of events and event
   organizers*. You cannot scrape a thing into existence.

So the review layer is technically trivial to build and existentially hard to fill. Writing the
review UI is a sprint. Getting the first ten thousand honest reviews per metro is the actual
company. Any feasibility plan that does not have a concrete answer for cold-start supply — seeded
content, an import path, an incentive design, a narrow launch wedge — is not a plan.

The same applies to the venue Q&A ("coat check, face control, food/alcohol"). There is no source.
It is a structured, user-contributed venue wiki, and it starts empty.

### 4.4 Attendance prediction has no training data

"Uses an LLM to estimate how many people may show up, given venue, event type, date, time, and
weather" — you can ship a number tomorrow, and it will be confidently wrong.

Supervised prediction needs labeled outcomes: features in, *actual attendance* out. That data does
not exist publicly. Venues and organizers do not publish door counts. Your own platform has none
until you have processed a lot of ticketing across years and seasons — and even then it is biased
toward events that chose to sell through you.

What is honestly buildable now:

- **Interval estimates from visible signals** — remaining-ticket counts on Eventbrite, public
  "attending" counts, stated capacity, historical listings density for that venue and weekday.
  "Fridays at this venue typically run 80–200" is defensible and useful.
- **A ranged forecast with stated uncertainty**, never a point estimate.

Presenting an LLM's guess as a forecast is the fastest way to lose organizer trust — they will
check it against reality on the first event, and one bad number poisons the tool.

---

## 5. Notes on the remaining features

### 5.1 Posting to social networks on the organizer's behalf
Feasible, permanently fragile. Instagram content publishing works for Business accounts; Facebook
Pages works; TikTok's posting API exists behind approval; X's API is now priced meaningfully for
real volume. Each platform is a separate review process with its own revocation risk. **Do not
build five direct integrations** — use a social-posting aggregation API and let a vendor absorb the
churn.

### 5.2 Venue demographics
Not derivable from scraped data. It is purchasable: foot-traffic analytics vendors sell venue-level
visitation and visitor demographics. This is a real, feasible path with a real enterprise price
tag. Buy it; don't try to infer it from listings.

### 5.3 Discount codes
Scraping coupon sites is easy and mostly returns expired codes and affiliate spam. Validating a
code means attempting it at checkout on someone else's site — brittle and hostile. Realistic
design: organizer-supplied codes as the trusted tier, plus a clearly-labeled low-confidence scraped
tier. Surfacing dead codes damages trust faster than the feature builds it.

### 5.4 "Connect with someone you saw at this event"
The code is easy — an event-scoped, opt-in roster with mutual consent to connect. The engineering
that matters is safety: consent defaults, blocking, reporting, rate limits, and abuse response.
This surface attracts harassment by design. Budget for trust-and-safety as a real workstream, not a
checkbox.

### 5.5 Due diligence on venue owners
Technically this is entity resolution against corporate registries, liquor license records, court
records, liens, and property records — all purchasable from data aggregators. The technical work is
ordinary. Selling the result as a background report on an individual puts you squarely in FCRA
territory. Noted here as a technical/compliance coupling and deferred to the legal assessment.

---

## 6. Cost and timeline

**A credible V1** — one metro; ~10 API sources plus ~200 long-tail sites; dedup; classification;
consumer apps on iOS, Android, and web; organizer console; UGC scaffolding for reviews and photos:

- 6–8 senior engineers, 1 designer, 1 PM
- **9–12 months** to a product that is genuinely good in one city
- roughly **$1.8–2.5M** fully loaded
- plus **$25–50k/year** in fetch and extraction infrastructure for that metro

**The full spec as written** is 25+ distinct products, several of which are two-sided marketplaces
in their own right. Honest estimate: **35–60 engineer-years, 3–4 years, $15–30M** — and a
meaningful share of that spend would go to features in Tier C that cannot ship as described.

**The permanent tax** is ingestion maintenance: a 3–6 person team forever, once you are national.
Scrapers rot. That cost never converts to capex.

---

## 7. What I would actually build first

If the goal is to prove technical viability rather than to build the whole spec:

1. **One metro. One vertical.** Pick a category where the long tail is the whole point and the
   incumbents are weakest — social dance, or underground music, or lectures. Coverage in one
   vertical is provable; coverage of "all events" is not.
2. **Ingestion plus dedup plus classification, done genuinely well.** If duplicates and staleness
   are visible, nothing downstream matters.
3. **First-party UGC from day one** — reviews, photos, RSVPs — with an explicit cold-start plan.
   Not scraped. This is the part that becomes the moat, and it takes the longest to fill, so it has
   to start first.
4. **The in-app social graph**, framed truthfully as in-app. Never promise the Facebook version.
5. **Organizer tools that work with zero network density**: flyer generation, native event
   creation, multi-network posting. These deliver value to organizer number one, which makes them
   the right acquisition wedge.

Defer everything requiring liquidity (collaboration matching, staffing, rentals, distribution) and
everything requiring accumulated outcome data (attendance prediction) until the data exists to make
them non-embarrassing.

---

## 8. Risk register

| Risk | Severity | Notes |
|---|---|---|
| Friend-graph features are unbuildable as specified | **Critical** | Marquee differentiator. Blocked by platform policy since 2015/2018. No workaround. |
| Review and photo cold start | **Critical** | The Yelp half is empty on launch and cannot be seeded by scraping. |
| Dedup quality | High | Visible, trust-destroying, and never finished. |
| Ingestion maintenance load | High | Permanent headcount, not a project. Scales with coverage. |
| Anti-bot arms race on the long tail | Medium | Managed services handle most of it; cost is real but not fatal. Vendors report ~95–98% success against major bot management at roughly $8 per 1,000 successful requests worst case. |
| Attendance prediction accuracy | Medium | Ship as ranges or not at all. A wrong point estimate loses the organizer permanently. |
| Platform API revocation (Meta, X, TikTok, Meetup) | Medium | Any single integration can vanish. Don't build a core dependency on one. |
| Venue identity spine choice | Medium | Google Places caching limits make it the wrong foundation. Decide early. |
| Trust and safety on person-to-person connection | Medium | Real workstream. Underestimating it is how this surface goes wrong. |

---

## 9. Bottom line

**Technically feasible, with two named exceptions that need the product rethought rather than
re-engineered.**

The aggregation engine is buildable, and cheap LLM extraction makes it meaningfully more buildable
than it was five years ago — a single metro runs a few thousand dollars a month in infrastructure.
The organizer services layer is mostly integration work whose difficulty is operational, not
technical.

But the two features that make it *Yelp* for events rather than *another* event listing site —
the social graph and the review corpus — are precisely the two that cannot be scraped into
existence. The friend graph is closed by platform policy and will not reopen. Reviews and photos
have to be grown from your own users, one metro at a time.

That is not a reason to stop. It is a reason to sequence the product around UGC accumulation from
day one instead of treating it as a layer to add once the scraper works.
