# NSF SBIR Phase I Project Pitch (draft v1)

Draft for the CEO to read and mark up. The pitch is NSF's gate: a short online form, about three pages, that you submit before you're allowed to write a full proposal. NSF reads it and says yes or no, usually inside three weeks. No pitch invite, no proposal.

Anything in [[double brackets]] is a fact only you can give me. I left those blank on purpose instead of guessing. You are the author of record, so rewrite anything that doesn't sound like you.

Anchor concept you picked: the battery. One pack that has to work both as a car battery and as an aircraft battery.

---

## Topic area
Best fit looks like Advanced Energy and Power Technologies (energy storage). Pin the exact topic against the NSF 26-510 list when you submit, since the names shift year to year.

## 1. The technology innovation
Alef is building one battery that has to do two jobs that normally need two different batteries. On the road the pack acts like a car battery. It wants range, long life, low cost, and it only delivers moderate power over a long stretch. The moment that same car lifts off and hovers, the pack has to behave like an aircraft battery instead: dump a lot of power right now, stay light, and throw off heat fast while it does it. Nobody sells a single pack that does both jobs well. The lazy answer is to carry extra cells, roughly two batteries' worth, which guts your road range and your flight time at the same time.

Our approach is a [[hybrid / reconfigurable]] pack that separates the energy job from the power job inside one system. High-energy cells hold the driving range. High-power elements cover the hover and climb spikes. A control and cooling scheme stitches them together so the car gets aircraft-grade power when it needs it and isn't dragging dead weight the rest of the time. The hard problems all sit at the seams between electrochemistry, power electronics, cooling, and safety. That is where the Phase I risk lives. [[cell chemistries / segmentation, topology, thermal method to confirm]]

## 2. Technical objectives and challenges
Phase I exists to answer one question. Can a single architecture cover both duty cycles without a weight penalty that kills the product? Six months of work:

1. Get the real numbers. Figure out what the Model A actually pulls while driving versus hovering and climbing, in both power and heat. [[need representative drive and flight power profiles]]
2. Build a handful of candidate architectures on paper and run a real trade study against weight, specific power, specific energy, safety, and cost. No hand-waving.
3. Take the best one to the bench as a single module and run it through a drive-then-hover cycle. Measure the burst power it actually puts out, how hot it gets, and how much driving range is left when the hover is done.
4. Break it on purpose. Dual use means it has to survive a car crash and stay trustworthy in flight, so we find out how it fails and what the battery management system has to watch for.

The whole thing hinges on one number: the mass penalty. If you can't get flight-grade burst power and keep it cool while still holding road range from one pack, the concept falls apart. Phase I is the cheap place to learn that.

## 3. Market opportunity
Alef holds about 3,500 pre-orders on the Model A. Those are small refundable deposits, so read them as interest, not money in the bank. For a battery program the more useful point is that this same two-jobs-one-pack problem shows up at every eVTOL and air-taxi company chasing this market, and in fast-charging high-power EVs besides. Crack it once and the result travels. (Hard market-size dollars get pulled from real sources for the full proposal. I'm not going to invent them here.)

## 4. Company and team
Alef Aeronautics is a seed-stage company in San Mateo, California, building the Model A, a fully electric vehicle that is both street-legal and able to take off vertically. The company holds an FAA Special Airworthiness Certificate in the Experimental category and flies test articles under it. Tim Draper and his network back it. Ownership is majority US individuals, and headcount is [[X]], well under the 500-employee SBIR cap. The PI would be [[name, title, and what they've actually built before]]. Core technical staff: [[names and roles]].

---

### For the CEO, not part of the pitch
Each pitch field has a character cap of a few thousand characters, so this draft runs a little long on purpose and trims down easily. I didn't put a single invented spec, chemistry, headcount, or market number in here. Those are the bracketed gaps. Once you approve the text and fill the brackets, I'll lock the pitch for you to paste into the portal and start the full Project Description and the NASA version in parallel.
