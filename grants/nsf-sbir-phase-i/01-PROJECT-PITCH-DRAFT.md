# NSF SBIR Phase I Project Pitch (draft v3)

Draft for the CEO. This is the current version. Concept and research focus are now set: the innovation is the hover-to-airplane transition, and the Phase I research targets the control and stability of that maneuver.

The pitch is NSF's gate. It's a short online form you submit before you can write a full proposal. NSF reads it and invites a proposal or declines, usually within three weeks.

Anything in [[double brackets]] is a fact only you can confirm. I left those open instead of guessing.

---

## Topic area
Best fit is an aerospace, robotics, or advanced-manufacturing topic, depending on how NSF 26-510 splits its list this cycle. Confirm the exact topic at submission.

## 1. The technology innovation
The Model A flies in two modes. It lifts off and hovers like a multirotor on eight rotors set under a mesh top surface. Once it's high enough, the entire car body rolls 90 degrees so its sides become a box-wing biplane, while a gimbaled cabin counter-rotates to keep the driver upright and facing forward. In airplane mode the vehicle flies on its wings instead of forcing all of its lift from the rotors, and wing-borne cruise draws roughly [[~7x]] less energy than hovering. That efficiency is what lets the car carry real flight range on an ordinary off-the-shelf battery. Alef does not develop cells or chemistry; it buys cells and builds simple packs. The novel engineering is the transition and the rotating-body wing that makes the efficiency real.

## 2. The technical objectives and challenges
The transition from hover to wing-borne flight is the hardest and most safety-critical phase of the flight. During the 90-degree roll the vehicle hands its lift off from the rotors to the wings, its aerodynamics change moment to moment, and a gust at the wrong instant can put it outside a safe state. The vehicle has flown under an FAA Special Airworthiness Certificate (Experimental), so the maneuver is possible. What is not yet established is a validated understanding of when it is safe and a control strategy that holds it stable every time, including in disturbed air. That is the gap Phase I closes.

Objectives for the six months:

1. Build a dynamic model of the vehicle through the full 90-degree transition that captures the shift from rotor-borne to wing-borne lift, the counter-rotating cabin, and the coupling between the rotors and the wing.
2. Define the safe transition envelope, meaning the range of airspeed and altitude where the maneuver can be completed with enough control margin.
3. Develop and test transition control laws in simulation, then stress them against gusts, crosswinds, and off-nominal starting conditions.
4. Validate the model against [[flight-test data from the experimental aircraft]].

The risk to retire: whether a control strategy exists that keeps the vehicle stable and inside its structural and aerodynamic limits across the airspeed, altitude, and gust conditions a real flight will see. The flying prototype is the evidence base for this work, which makes the proposal stronger, since the research is about characterizing and guaranteeing the maneuver rather than attempting it for the first time. Phase I sets up a Phase II that takes the validated control approach to a full-envelope, hardware-in-the-loop demonstration.

## 3. The market opportunity
Alef holds about 3,500 pre-orders on the Model A. Those are small refundable deposits, so read them as demand, not revenue. The transition-control work also carries to other eVTOL and air-taxi designs, because the hover-to-cruise handoff is the common safety and efficiency bottleneck across the sector. Hard market-size numbers come from real sources in the full proposal, not from me here.

## 4. The company and team
Alef Aeronautics is a seed-stage company in San Mateo, California, building the Model A, a fully electric vehicle that drives on the road and takes off vertically. The company holds an FAA Special Airworthiness Certificate (Experimental) and has flown test articles under it. Tim Draper and his network back it. Ownership is majority US individuals, and headcount is [[X]], under the 500-employee SBIR cap. The PI would be [[name, title, and what they have built before]]. Core technical staff: [[names and roles]].

---

### For the CEO, not part of the pitch
Concept and focus are set. To turn this into the final paste-ready pitch I still need, from you: confirmation of the 7x figure, whether any flight-test data can back the model (objective 4), the PI name and credentials, and the headcount. None of those block your approval of the framing; they just fill the brackets.
