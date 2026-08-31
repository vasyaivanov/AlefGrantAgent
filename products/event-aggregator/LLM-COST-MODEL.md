# LLM cost model — San Francisco Bay Area launch

Assessment date: 31 August 2026. Companion to TECHNICAL-FEASIBILITY.md.
Pricing verified against Anthropic's published rates, August 2026.

---

## The finding that comes before the arithmetic

**An LLM does not know what is happening in Oakland next Friday.** Event listings are not
memorized training data — they change weekly and were never in the corpus. Prompt Claude or
ChatGPT for local events with no tools attached and you get **fluent, well-formatted, entirely
fabricated events** — real-sounding venue names, plausible times, invented prices.

That version costs almost nothing and is worth nothing. So both proposed approaches implicitly
require the model to have **web search**, and that changes the cost structure completely:

- **Web search is billed separately: $10 per 1,000 searches** — one search is one use regardless
  of how many results come back.
- **Search results bill as input tokens in that turn *and every later turn*.** This is the
  multiplier most budgets miss. An 8-search agentic turn does not cost 8 × one snippet; the
  accumulated results are resent on each subsequent round, so the input cost grows with the
  square of the search count, not linearly.

A single 8-search "find all events near X" call therefore carries **~145,000 cumulative input
tokens** and ~10,000 output tokens, not the ~5,000 people assume.

### Per-call cost, 8 searches, 20 events returned

| Model | Token cost | Search fee | **Per call** |
|---|---|---|---|
| Opus 5 ($5/$25 per MTok) | $0.83 | $0.08 | **$0.91** |
| Sonnet 5 ($2/$10) | $0.33 | $0.08 | **$0.41** |
| Haiku 4.5 ($1/$5) | $0.17 | $0.08 | **$0.25** |

Token cost already assumes prompt caching on the 4K system prompt. Note how little that saves —
about 3% — because the volatile search results dominate the context and cannot be cached. This
is the opposite of the usual intuition about caching.

---

## Your "50-mile radius" grid is one cell

Worth settling before costing approach 2. The nine-county Bay Area is roughly **7,000 sq mi**.
A 50-mile-radius circle covers **7,854 sq mi**.

**One 50-mile circle covers the entire Bay Area.** So "every 50 miles radius, twice a week" is
literally 2 calls per week — about $8/month, returning perhaps 20 events for a region with
thousands. The grid granularity, not the sweep frequency, is the entire cost driver, and it
swings the answer by more than 500×:

| Cell radius | Cell area | Cells to cover the Bay Area |
|---|---|---|
| 50 mi | 7,854 sq mi | **1** |
| 25 mi | 1,963 sq mi | 4 |
| 10 mi | 314 sq mi | 23 |
| 5 mi | 79 sq mi | 90 |
| 2 mi | 13 sq mi | 558 |

---

## Approach 1 — real time, then cached

**Model:** user searches a location; on a cache miss, fire an LLM+search call; cache the result
per (tile × category × week).

Cache-key cardinality is what actually determines spend. Assume 60 meaningful Bay Area tiles
(cities and distinct neighborhoods), 12 top-level categories from the spec, and a 4-week forward
window — **2,880 live keys**, each refreshed weekly ≈ **3,100 calls/month** at full population.

| Model | Full population | Early stage (20% of keys touched) |
|---|---|---|
| Opus 5 | **$2,820/mo** | $560/mo |
| Sonnet 5 | **$1,280/mo** | $255/mo |
| Haiku 4.5 | **$760/mo** | $150/mo |

**The cost is fine. The design is not**, for two reasons that have nothing to do with money:

- **Cold-start latency.** The first user to hit an uncached key waits 30–90 seconds for an
  eight-search agentic turn. That is fatal in a search box.
- **Staleness.** A weekly cache shows cancelled events and misses new ones. The highest-traffic
  query — "this weekend" — is exactly the one a week-old cache serves worst.

In practice you would pre-warm every key to avoid both. **Pre-warming *is* approach 2**, so the
two options collapse into one.

---

## Approach 2 — background sweep, twice weekly

Calls/month = cells × 2 sweeps × 12 categories × 4.3 weeks.

| Grid | Calls/mo | Opus 5 | Sonnet 5 | Haiku 4.5 | Haiku + Batch |
|---|---|---|---|---|---|
| 50 mi (as specified) | 103 | $94 | $43 | $25 | **$17** |
| 25 mi | 413 | $376 | $170 | $102 | **$67** |
| 10 mi | 2,374 | $2,160 | $978 | $584 | **$387** |
| 5 mi | 9,288 | $8,452 | $3,827 | $2,285 | **$1,514** |
| 2 mi | 57,586 | $52,403 | $23,725 | $14,166 | **$9,386** |

**Use the Batch API here.** A background sweep has no latency requirement, and batch is 50% off
token cost — it is free money for this workload. It does not discount the search fee, which
becomes a floor: at a 5-mile grid, **$743/month in search fees alone, regardless of model**.

A 5-mile grid is the coarsest that plausibly surfaces neighborhood-level events. So the honest
range for approach 2 is **$1,500–8,500/month**, depending mostly on model choice.

---

## Approach 3 — what the technical assessment recommends, for comparison

Fetch pages yourself, take the free schema.org JSON-LD tier first, and use the LLM only to
extract from what is left. Bay Area: ~3,000 long-tail sites × 5 pages × 2 sweeps/week ≈
**130,000 pages/month**, of which ~40% carry JSON-LD and cost nothing to parse.

| Model | Raw | With caching | Cached + Batch |
|---|---|---|---|
| Opus 5 | $2,730 | $2,028 | $1,014/mo |
| Sonnet 5 | $1,092 | $811 | $406/mo |
| Haiku 4.5 | $546 | $406 | **$203/mo** |

Plus $250–1,000/month for fetching and proxies. **All-in: $450–1,400/month.**

Caching matters *here* — 30–50% savings — because the stable extraction schema is a large share
of a small prompt. The inverse of approach 1 and 2.

---

## The comparison that decides it

| | Coverage | Cost/month | Freshness | Fabrication risk |
|---|---|---|---|---|
| **1. Real-time LLM + search** | Poor — only what the search index surfaces | $150–2,800 | Cache-stale | High |
| **2. Background LLM + search**, 5-mi grid | Poor to moderate | $1,500–8,500 | 2×/week | High |
| **3. Own crawl + LLM extract** | Good — 60–75% of long tail | **$450–1,400** | 2×/week, tunable | Low — grounded in the page |

**Approach 3 is simultaneously the cheapest and the best.** That is not a close call, and the
reason is structural: in approaches 1 and 2 you pay $10 per 1,000 searches to see the top ten
results of an index that has already decided what is worth listing. In approach 3 you decide
what to read.

There is also a hidden double-charge in the LLM-search approaches: because output is
ungrounded, anything you publish must be verified against the source page — and fetching that
page *is* approach 3. You end up building it anyway, having paid twice.

---

## Practical notes

- **Don't use Opus 5 for extraction.** Schema-filling from a fetched page is mechanical work.
  Haiku 4.5 costs one-fifth of Opus 5 and does it as well. Reserve the expensive model for
  genuinely hard judgment — deduplication adjudication on borderline pairs, for instance, where
  the candidate set is small and a wrong merge is costly.
- **Batch everything that isn't user-facing.** 50% off, no quality cost.
- **Cache placement is the opposite of what you'd guess.** Caching is nearly useless in the
  search-based approaches and worth 30–50% in the crawl-based one.
- **The search-fee floor is model-independent.** Once you commit to LLM-driven search, a chunk
  of the bill cannot be optimized away by picking a cheaper model.

## The headline number

**LLM spend is not the constraint on this product in any scenario.** The worst case here —
Opus 5, 2-mile grid, no batching — is about $52,000/month, and the sensible configurations run
**$200–1,500/month for the entire Bay Area**. Against the $1.8–2.5M engineering cost of a V1 in
one metro, inference is a rounding error.

What the LLM budget *cannot* buy is coverage or truthfulness. Those come from controlling which
pages get read — which is an engineering decision, not a spending one.

---

*Pricing note: figures are Anthropic's published API rates as of August 2026 (Opus 5 $5/$25,
Sonnet 5 $2/$10, Haiku 4.5 $1/$5 per MTok; web search $10 per 1,000 searches; Batch API 50% off;
cache reads ~0.1× base input, writes 1.25× at 5-minute TTL). OpenAI's current rates were not
independently verified for this model, but the structure is the same and the conclusion —
that self-directed crawling beats LLM-driven search on both cost and coverage — is
provider-independent.*
