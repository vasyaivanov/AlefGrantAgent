# NSF SBIR Phase I Project Pitch (draft v2)

Draft for the CEO. This replaces v1. The v1 draft was built around battery architecture, which was wrong: Alef buys cells off the shelf and builds simple packs. The real innovation is the flight architecture, so the whole pitch now sits on the hover-to-airplane transition.

The pitch is NSF's gate. It's a short online form you submit before you're allowed to write a full proposal. NSF reads it and either invites a proposal or turns you down, usually inside three weeks.

Anything in [[double brackets]] is a fact or decision only you can give me. I left those open instead of guessing.

Anchor concept: the rotorcraft-to-airplane transition, where the car body rotates 90 degrees into a box-wing and cruise flight uses roughly 7 times less energy than hovering.

---

## Topic area
Best fit looks like Advanced Manufacturing, or an aerospace/robotics topic, depending on how NSF 26-510 splits its list this cycle. Confirm the exact topic when you submit.

## 1. The technology innovation
The Model A flies in two modes. It lifts off and hovers like a multirotor on eight rotors mounted under a mesh top surface. Once it's high enough, the entire car body rolls 90 degrees so its left and right sides become a box-wing biplane, while a gimbaled cabin spins the opposite way to keep the driver upright and facing forward. In that airplane mode the vehicle flies on its wings instead of forcing all its lift from the rotors. Wing-borne cruise draws on the order of [[~7x]] less energy than hovering, and that single fact is what lets the car carry a useful flight range on an ordinary off-the-shelf battery.

Alef does not develop cells or battery chemistry. It buys cells and builds straightforward packs. The novel engineering is the transition maneuver and the rotating-body wing that makes the efficiency gain real. No folding wings, no separate aircraft structure, the car body is the wing.

## 2. Technical objectives and challenges
The transition from hover to wing-borne flight is the hardest and most safety-critical part of the whole flight. The vehicle has flown under an FAA Special Airworthiness Certificate (Experimental), so basic feasibility is proven, but [[what is still open: pick the real research gap]]. Phase I would target that gap. Likely work, to be narrowed with the CEO:

1. Model the transition dynamics through the 90-degree roll and define the safe airspeed and altitude envelope for it.
2. Develop and test the control strategy that keeps the vehicle stable through the maneuver, including under gusts and crosswinds.
3. Quantify and improve the cruise aerodynamic efficiency, including how the eight rotors and the mesh surface interfere with the box-wing. This is what protects and grows the 7x.
4. Measure the energy and altitude lost during the transition itself and find ways to cut it.

The risk to retire in Phase I: [[the one specific thing the CEO says is genuinely unsolved]]. The existing flying prototype is evidence the approach works, which strengthens the proposal rather than weakening it, as long as the research question stays on what isn't yet characterized, optimized, or made robust.

## 3. Market opportunity
Alef holds about 3,500 pre-orders on the Model A. Those are small refundable deposits, so read them as demand, not revenue. The transition and box-wing work also carries to other eVTOL and air-taxi designs chasing efficient forward flight, since hovering the whole way is what kills range across the sector. (Hard market-size numbers come from real sources in the full proposal, not from me here.)

## 4. Company and team
Alef Aeronautics is a seed-stage company in San Mateo, California, building the Model A, a fully electric vehicle that drives on the road and takes off vertically. The company holds an FAA Special Airworthiness Certificate (Experimental) and has flown test articles under it. Tim Draper and his network back it. Ownership is majority US individuals, and headcount is [[X]], under the 500-employee SBIR cap. The PI would be [[name, title, and what they've built before]]. Core technical staff: [[names and roles]].

---

### For the CEO, not part of the pitch
The single most important thing I need from you is in section 2: what about the transition is genuinely still an open engineering problem? Control and stability, aerodynamic efficiency, or transition energy loss are the usual candidates. Pick one (or tell me the real one) and I'll write the research plan around it. Everything else here is ready once you fill the brackets.
