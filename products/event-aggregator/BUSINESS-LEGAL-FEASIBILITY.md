# "Yelp for events" — business, competitive, monetization and legal feasibility

Assessment date: 31 August 2026. Companion to TECHNICAL-FEASIBILITY.md in this folder.

---

## Headline

**Technically feasible. As a business, the version in the spec is the one shape that has
reliably failed.** Every pure event aggregator has died; the companies that won in this
category own the *transaction* in a *narrow vertical*. The fix is not more engineering — it
is a different thesis, and the assets described in the spec support that better thesis well.

Two features should be cut on legal grounds alone: venue-owner background reports (FCRA) and
cross-platform friend/attendance data (privacy) — the latter already technically dead.

---

## 1. Business feasibility

### The category has a graveyard, and the numbers say why

Eventful, Zvents, Upcoming.org, Plancast, Sosh, YPlan, Nvite — every pure aggregator is gone.
Not from bad execution. From the model.

The clearest signal available today:

| Company | Model | 2025 result |
|---|---|---|
| **Eventbrite** | Listings + ticketing, 20 years, full supply integration | **$291.8M net revenue, down 10% YoY.** EBITDA $25.3M, down from $35.1M. |
| **Fever** | Produces and curates its *own* experiences | **>$500M revenue**, ~20x growth vs pre-pandemic, EBITDA-positive, $100M Series E |
| **Posh** | Nightlife ticketing, one vertical | 8M users, **$350M GMV**, $37M Series B |
| **Partiful** | Social planning first, ticketing added June 2026 | $27M raised (a16z) |

Read it plainly: **the incumbent listings business is shrinking while transaction-owning and
experience-producing businesses compound.** Fever is the instructive one — it is routinely
described as event discovery, but it won by abandoning aggregation as the product and
producing inventory it controls.

### The structural problem: events are ephemeral, and Yelp's model requires permanence

This is the deepest issue with the analogy, and it deserves to drive the strategy.

Yelp works because a restaurant is a **persistent object**. A review written in 2015 still has
value in 2026, still ranks in search, still compounds. An event happens once and is worthless
the next morning. A review of an event is a dead asset on arrival.

The consequence is actually clarifying: **the only durable reviewable objects here are venues
and organizers.** And that universe is small — a metro has perhaps 500–2,000 relevant venues
and active organizers, not millions of events.

That cuts both ways:
- **Good:** the cold-start problem is far smaller than it looks. You need review density on
  ~1,000 objects per metro, not on every event.
- **Bad:** a small object universe means a small SEO surface and a thinner moat than Yelp's.

**The strategically correct product is "Yelp for venues and organizers," with events as the
traffic driver.** Events bring people in; the accumulating asset is venue and organizer
reputation. The spec has this inverted.

### Cold start is three-sided, not two-sided

Attendees, organizers, *and* UGC contributors. Each needs the others. Yelp took roughly five
years to reach useful review density in San Francisco alone, with a simpler loop and no
competition for the concept.

### Frequency kills consumer economics

Event discovery is episodic — most people plan a night out once or twice a month. Yelp gets
weekly restaurant intent. Low frequency means weak retention, weak habit, and CAC that is hard
to pay back on consumer monetization alone.

### Google is the elephant

Google Search shows event rich results for free, sourced from the **same schema.org markup you
would be scraping**. It has distribution you cannot buy and answers the query without a click.
Google is a large part of why Zvents and Eventful died. Any thesis resting on "we aggregate
listings better" is competing with a free, pre-installed, zero-click incumbent.

---

## 2. Competitive feasibility

### The landscape is not empty — it is crowded and segmented

- **Horizontal:** Google Events, Facebook Events (still the largest event graph on earth, and
  closed to you), Eventbrite discovery, Time Out, Fever, AllEvents.in
- **Vertical:** Resident Advisor (electronic), Dice (music), Bandsintown and Songkick (touring),
  Meetup (community), Luma (tech), Partiful (social), Posh (nightlife US), Shotgun (nightlife
  EU), ClassPass (fitness), city guides in the Do312/DoNYC mould
- **Reputation:** Yelp and Google Reviews already own venue reviews. Instagram is the de-facto
  discovery layer for nightlife.

### Aggregated public data is not a moat

Anything you scrape, a competitor can rescrape. Coverage is a cost centre, not a defence. The
spec's implicit moat theory — "we will have the most complete listings" — is the weakest one
available.

The three moats that actually hold in this category:
1. **A UGC corpus** (reviews, photos) — slow to build, genuinely hard to copy
2. **Transaction and supply relationships** with organizers — switching costs
3. **Brand ownership of one vertical** — Resident Advisor for electronic, Posh for nightlife

Note that all three are on the *hard* side of the technical assessment. That is not a
coincidence: what is easy to build is easy to copy.

### Channel conflict is structural

Eventbrite, Dice and Posh would be simultaneously your data source and your competitor. They
can and do cut access — Eventbrite already killed public event search in 2020, Meetup gated its
API in 2025. **You would be building on land your competitors own.** Every integration is a
dependency someone else can revoke on a product-strategy whim.

### If you succeed, the aggregation is trivially copied

Google, Eventbrite and Meta can replicate listings coverage quickly. What they cannot replicate
quickly is an organizer relationship book and a review corpus. Build those first, or the win
gets taken.

---

## 3. Monetization

Ranked by how real each line is:

| Line | Verdict | Notes |
|---|---|---|
| **Ticketing take rate** | **The actual business.** | 3–10% plus fees. Requires owning the transaction, which means competing directly with Eventbrite, Dice and Posh. Posh's $350M GMV shows the size available in one vertical. |
| **Organizer services** (the spec's back half) | **Real, underrated.** | Flyers, posting, insurance referral, rentals, staffing. Plausible $50–300/month per serious organizer. Universe of maybe 200–1,000 serious organizers per metro — small, but high-margin and sticky. Insurance referral commissions run 10–20% of premium. |
| **Venue and organizer ads** | Real, but only at scale. | Yelp's actual model. Eventbrite Ads grew ~30% YoY, so it works — once you have traffic density. Not a launch revenue line. |
| **Affiliate on outbound ticket links** | Thin and shrinking. | 2–8% where programs exist. The long tail that differentiates you has no affiliate programs at all. |
| **Consumer subscription** | **Don't.** | Willingness to pay for event discovery is near zero. |
| **Data licensing** | Small and legally the most exposed. | Selling scraped compilations is where copyright and database-rights claims land hardest. |

### The unit economics that decide it

Discovery traffic monetizes at roughly **$0.50–3 per user per year** via affiliate and ads. CAC
for a low-frequency consumer app runs **$5–20**. That does not close, and no amount of coverage
makes it close.

**Therefore: monetization has to be organizer-side B2B. The consumer app is a
customer-acquisition channel for the organizer business, not a revenue line.** Once that is
accepted, most of the spec's "organizer features" stop being nice-to-haves and become the
product.

---

## 4. Legal feasibility

### The scraping core is more defensible than most assume

The case law has moved in your favour:

- **Van Buren v. United States (2021)** narrowed the CFAA substantially.
- **hiQ v. LinkedIn (9th Cir. 2022)** — scraping public data is unlikely to violate the CFAA.
  But hiQ then **lost on breach of contract** in late 2022. The contract claim, not the CFAA,
  is the live risk.
- **Meta v. Bright Data (N.D. Cal., Jan 2024)** — Judge Chen granted Bright Data summary
  judgment: **logged-out scraping of public data did not breach Meta's terms**, and a survival
  clause purporting to bind forever was held unenforceable.

The operating rule that falls straight out of this: **never log in, never create accounts,
never accept terms of service, touch only public pages.** Logged-in scraping is where companies
lose. Design the crawler around that constraint from day one — it is cheap to honour early and
expensive to retrofit.

### Risks that remain, ranked

1. **Copyright on scraped content.** Facts are not copyrightable (*Feist*) — time, place, price
   are safe. Event descriptions, flyers and photos are **not**. Ingest facts, link out for prose
   and imagery, and do not host flyers or photos you have no licence to. This directly
   constrains the spec's "flyer" field. Thumbnails have a fair-use argument (*Perfect 10*);
   hosting full creative works does not.
2. **EU/UK sui generis database rights.** Protects compilations regardless of copyright, and is
   unaffected by the text-and-data-mining exception. **EU expansion is materially riskier than
   the US.**
3. **Privacy on personal data.** The Dutch DPA calls scraping personal data "almost always a
   violation"; **Clearview was fined €30.5M (NL) and €20M (IT); CNIL fined KASPR €240K** — all
   for scraping *public* personal data. CNIL's 2025 guidance does permit legitimate-interest
   scraping, so it is navigable, but needs a documented balancing test, notice and deletion
   paths. **The friend-graph and contact-book matching features carry the highest privacy
   exposure in the entire product** — compounding the technical finding that they don't work.
4. **FCRA — the venue-owner background report.** The single most dangerous feature in the spec.
   Assembling background reports on individuals for other people's business decisions likely
   makes you a **consumer reporting agency**, triggering permissible-purpose limits, accuracy
   duties, dispute procedures and adverse-action notices. FCRA liability is non-delegable and
   highly class-action-friendly. **Cut it, or route it through a licensed CRA and stay out of
   report assembly entirely.**
5. **Defamation and review liability.** Section 230 protects you for user-posted reviews in the
   US, but expect sustained takedown pressure from venues. Two aggravating factors: **Section
   230 does not travel** — the EU and UK have no equivalent — and reviews of *organizers*
   (often individuals, not businesses) are far more defamation-exposed than restaurant reviews.
6. **"Connect with someone you saw at this event."** Dating-adjacent. Several states (NY, NJ,
   TX, IL) have online-dating safety-disclosure statutes; add minor-safety obligations and
   app-store age-verification rules. A real compliance surface.
7. **Insurance.** You cannot sell or solicit insurance without a **producer licence in each
   state**. Be a referral partner to a licensed agency, and watch anti-rebating rules on how
   you take compensation.
8. **Contract generation — UPL.** LegalZoom-style fixed templates have survived challenge with
   clear disclaimers and no individualised advice. **LLM-generated bespoke contract terms edge
   much closer to practising law.** Keep it to fixed templates with a lawyer-reviewed library.
9. **Payments.** Holding organizer funds triggers state money-transmitter licensing. Standard
   fix is a payment-facilitator structure (Stripe Connect and similar) — solvable, but a real
   setup cost, not an afterthought.
10. **Discount codes.** Publishing scraped codes invites tortious-interference and
    breach-of-terms claims from merchants. Low severity, steady annoyance.
11. **C&Ds as a running cost.** Even post-*Bright Data*, individual sites will block you and
    send letters. Build a delisting and takedown process before you need it.

### Legal verdict

**The aggregation core is workable in the US with discipline.** Two features should be cut or
restructured on legal grounds alone — venue-owner background reports and cross-platform
friend/attendance data. **EU expansion is a materially harder legal problem than the US**
(database rights, GDPR, no Section 230), and should be a deliberate later decision rather than
an assumed next market.

---

## 5. Synthesis

| Axis | Verdict |
|---|---|
| **Technical** | Feasible. Two features blocked by platform policy, not engineering. |
| **Business** | The spec's model is the one that has reliably failed. The assets support a better model. |
| **Competitive** | Aggregation is not a moat. Winners own the transaction in one vertical. |
| **Monetization** | Consumer discovery does not pay. Organizer-side B2B does. |
| **Legal** | Workable in the US with discipline. Two features to cut. EU much harder. |

### The thesis that survives all four

> **A venue-and-organizer reputation platform for one vertical in one city, using aggregated
> event listings as top-of-funnel, monetized through ticketing take rate and organizer
> services.**

That version is feasible technically, defensible competitively, has a real revenue line from
month one, and is legally clean. Every asset described in the original spec has a role in it —
the aggregator becomes the acquisition channel, the reviews accumulate on objects that persist,
and the organizer tools become the business rather than the epilogue.

The spec as written — universal coverage, scraped social proof, monetization unspecified — is
the shape the graveyard is full of.
