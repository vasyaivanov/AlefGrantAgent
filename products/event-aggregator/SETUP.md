# Account setup — all eight services

Do these in order. Four need no credit card at all. Save every key into `.env`
(never into code, never committed).

**Before you start:** make sure `.gitignore` contains `.env`. It already does in this repo.

---

## 1. Ticketmaster Developer  ·  free  ·  no card

**https://developer.ticketmaster.com/**

1. Click **Sign Up** (top right)
2. Name, email, password. No card, no company details
3. Confirm your email, then sign in
4. Go to **My Apps** → **Add a new app**
5. Name it `eventjim`, add a one-line description
6. Your **Consumer Key** appears immediately

**Save as:** `TICKETMASTER_KEY`
**You get:** 5,000 calls/day, 5 requests/second, instantly.
**Bonus:** covers **LiveNation** events too — same company, same API.

---

## 2. SeatGeek Platform  ·  free  ·  no card

**https://seatgeek.com/build**  (docs: https://seatgeek.github.io/)

1. Create a normal SeatGeek account first if you don't have one
2. On the Platform page, register an application
3. You receive a **client_id** (public) and a client_secret

**Save as:** `SEATGEEK_CLIENT_ID`
**Usage:** passed in the URL as `?client_id=YOUR_ID`. The secret is not needed for read-only.

---

## 3. Google AI Studio (Gemini)  ·  free  ·  no card

**https://aistudio.google.com/apikey**

1. Sign in with your existing Gmail
2. Click **Create API key**
3. Choose **Create API key in new project**
4. **Copy it immediately** — it is shown once

**Save as:** `GEMINI_API_KEY`
**You get:** a free tier with **no expiry and no credit card**, covering Gemini Flash and
Flash-Lite — the exact models this project uses. Rate limits are shown per-project inside
AI Studio rather than published.

---

## 4. Neon (database)  ·  free  ·  no card

**https://neon.com**

1. **Sign up with GitHub** — fastest, no card
2. Create a project. Name it `eventjim`
3. Region: **AWS us-west-2 (Oregon)** — closest to the Bay Area and to DigitalOcean SF
4. Copy the **connection string** (starts `postgresql://`)
5. Open the SQL editor and run: `CREATE EXTENSION postgis;`

**Save as:** `NEON_DATABASE_URL`
**Free tier:** 0.5 GB storage. Plenty for text-only event data — that is roughly a million
photo *references*, though only ~170 actual photos, which is why photos never go in the
database.

---

## 5. Serper (web + image search)  ·  free to start  ·  no card

**https://serper.dev**

1. Click **Sign up**, use Google sign-in
2. The key appears on your dashboard immediately

**Save as:** `SERPER_KEY`
**You get:** **2,500 free credits, no credit card.**
**Do not buy credits yet** — 2,500 lasts months at prototype volume, and purchased credits
**expire 6 months after purchase**, which makes low-volume packs wasteful.

---

## 6. DigitalOcean (the server)  ·  ~$12/month  ·  card required

**https://cloud.digitalocean.com/** — already have an account

1. **Create → Droplet**
2. Region: **San Francisco (SFO3)**
3. Image: **Ubuntu 24.04 LTS**
4. Size: **Basic → Regular → 2 GB RAM / 1 vCPU** (~$12/month)
   - Go to 4 GB (~$24) only if Playwright/Chromium ends up doing heavy work
5. Authentication: **SSH key** (not password)
6. Hostname: `eventjim`
7. Enable **Monitoring** (free — this is DigitalOcean's own alerting layer)

**Do not create this until you are ready to deploy.** Week 1 runs on your laptop.
A droplet bills from the moment it exists.

---

## 7. Tripadvisor Content API (venue reviews)  ·  free tier  ·  **card required**

**https://www.tripadvisor.com/developers**

1. Sign up (Google sign-in works) or log in
2. Click **Create API key**
3. **A credit card is required** — overage bills to it
4. **Set a maximum daily budget during signup.** Do this deliberately — it is your hard cap
   against a surprise bill
5. **Restrict the key by domain name.** Tripadvisor requires it, and it stops a leaked key
   being usable

**Save as:** `TRIPADVISOR_KEY`
**Free allowance:** their docs say 5,000 calls/month; some sources say 1,000. **Check the
number shown at signup** rather than trusting either.
**Used for:** venue reviews and ratings only — never event discovery.

---

## 8. Apify (Facebook events, Instagram photos)  ·  free tier  ·  no card

**https://apify.com**

1. **Sign up free** — GitHub or Google sign-in, no card for the free plan
2. Go to **Settings → Integrations → API tokens**
3. Copy your personal API token
4. In **Apify Store**, find and note the IDs of:
   - a **Facebook Events Scraper**
   - an **Instagram Hashtag Scraper**

**Save as:** `APIFY_TOKEN`
**Free plan:** monthly credits covering roughly 2,000 Facebook events.
**Paid rates:** Facebook ~$13/1,000 events; Instagram hashtags $0.24–1.50/1,000 posts.

---

## Summary

| # | Service | Cost | Card? | Needed by |
|---|---|---|---|---|
| 1 | Ticketmaster | Free | No | Day 1 |
| 2 | SeatGeek | Free | No | Day 1 |
| 3 | Google AI Studio | Free | No | Day 4 |
| 4 | Neon | Free | No | Week 2 |
| 5 | Serper | Free 2,500 | No | Week 3 |
| 6 | DigitalOcean | ~$12/mo | Yes | When deploying |
| 7 | Tripadvisor | Free tier | **Yes** | Week 4 |
| 8 | Apify | Free tier | No | Week 4 |

**Four of the eight need no card at all.** Two are already owned (GitHub, DigitalOcean).

---

## After every registration

Paste the key into `.env` in this repo:

```
TICKETMASTER_KEY=...
SEATGEEK_CLIENT_ID=...
GEMINI_API_KEY=...
NEON_DATABASE_URL=...
SERPER_KEY=...
TRIPADVISOR_KEY=...
APIFY_TOKEN=...
```

Then confirm it is ignored by git:

```
git check-ignore -v .env
```

That must print a line naming `.gitignore`. If it prints nothing, **stop** — `.env` is not
protected and a commit would publish your keys. Bots scan public repositories for API keys
within minutes.

Every one of these services lets you revoke and reissue a key from the same dashboard if one
ever leaks.
