"""Copy calendar invites addressed to press@alef.aero into a direct invite for jwizard@gmail.com.

Usage:
  python3 add_to_jwizard_calendar.py                 # process every new forwarded invite not yet copied
  python3 add_to_jwizard_calendar.py <gmail_msg_id>  # process one specific press@alef.aero message
It reads the invite.ics (text/calendar part) of the message, keeps the original time, title, location and
description, and sends a fresh METHOD:REQUEST invite from press@alef.aero with jwizard@gmail.com as the guest.
"""
import sys, os, re, json, uuid, base64, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gmail_sender as G
from email.message import EmailMessage
from email.utils import make_msgid, format_datetime
from zoneinfo import ZoneInfo

TO = "jwizard@gmail.com"
STATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jwizard_calendar_copied.json")

def find_ics(payload):
    if payload.get("mimeType", "").lower() in ("text/calendar", "application/ics"):
        b = payload.get("body", {})
        if b.get("data"): return base64.urlsafe_b64decode(b["data"]).decode("utf8", "ignore")
        if b.get("attachmentId"): return None  # fetched separately
    for p in payload.get("parts", []) or []:
        r = find_ics(p)
        if r: return r
    return None

def find_ics_att(msg_id, payload):
    if payload.get("mimeType", "").lower() in ("text/calendar", "application/ics") and payload.get("body", {}).get("attachmentId"):
        a = G.api("GET", f"messages/{msg_id}/attachments/{payload['body']['attachmentId']}")
        return base64.urlsafe_b64decode(a["data"]).decode("utf8", "ignore")
    for p in payload.get("parts", []) or []:
        r = find_ics_att(msg_id, p)
        if r: return r
    return None

def unfold(ics): return re.sub(r"\r?\n[ \t]", "", ics)

def build_copy(ics):
    ics = unfold(ics)
    blocks = re.findall(r"BEGIN:VTIMEZONE.*?END:VTIMEZONE", ics, re.S)
    ev = re.search(r"BEGIN:VEVENT(.*?)END:VEVENT", ics, re.S).group(1)
    keep = []
    title = "Interview"
    for line in ev.splitlines():
        k = line.split(":", 1)[0].split(";", 1)[0].upper()
        if k in ("DTSTART", "DTEND", "DURATION", "SUMMARY", "LOCATION", "DESCRIPTION", "RRULE"):
            keep.append(line)
            if k == "SUMMARY": title = line.split(":", 1)[1].replace("\\,", ",").replace("\\;", ";")
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = ["BEGIN:VCALENDAR", "PRODID:-//Alef Press//Calendar Copy//EN", "VERSION:2.0", "CALSCALE:GREGORIAN", "METHOD:REQUEST"]
    out += [l for b in blocks for l in b.splitlines()]
    out += ["BEGIN:VEVENT", f"UID:{uuid.uuid4()}@alef.aero", f"DTSTAMP:{now}"] + keep + [
        "ORGANIZER;CN=Alef Press Team:mailto:press@alef.aero",
        f"ATTENDEE;CUTYPE=INDIVIDUAL;ROLE=REQ-PARTICIPANT;PARTSTAT=NEEDS-ACTION;RSVP=TRUE;CN=Jim Dukhovny:mailto:{TO}",
        "SEQUENCE:0", "STATUS:CONFIRMED", "TRANSP:OPAQUE",
        "BEGIN:VALARM", "ACTION:DISPLAY", "DESCRIPTION:Reminder", "TRIGGER:-PT15M", "END:VALARM",
        "END:VEVENT", "END:VCALENDAR", ""]
    return title, "\r\n".join(out)

def send_copy(title, ics, desc=""):
    m = EmailMessage()
    m["From"] = "Alef Press Team <press@alef.aero>"; m["To"] = TO
    m["Subject"] = f"Invitation: {title}"
    m["Date"] = format_datetime(datetime.datetime.now(ZoneInfo("America/Los_Angeles")))
    m["Message-ID"] = make_msgid(domain="alef.aero")
    m.set_content(f"{title}\n\nCalendar copy for jwizard@gmail.com of an invite sent to press@alef.aero.\n{desc}")
    m.add_alternative(ics, subtype="calendar", params={"method": "REQUEST"})
    m.add_attachment(ics.encode(), maintype="application", subtype="ics", filename="invite.ics")
    return G.send(m).get("id")

def process(msg_id, state):
    full = G.api("GET", f"messages/{msg_id}", params={"format": "full"})
    ics = find_ics(full["payload"]) or find_ics_att(msg_id, full["payload"])
    if not ics or "BEGIN:VEVENT" not in ics:
        print("no calendar data in", msg_id); return
    if "METHOD:CANCEL" in ics.upper():
        print("skip cancellation", msg_id); return
    title, copy = build_copy(ics)
    sid = send_copy(title, copy)
    state[msg_id] = {"title": title, "sent_id": sid, "at": datetime.datetime.now(ZoneInfo("America/Los_Angeles")).isoformat()}
    print("copied:", title, "->", sid)

def main():
    state = json.load(open(STATE)) if os.path.exists(STATE) else {}
    if len(sys.argv) > 1:
        ids = sys.argv[1:]
    else:
        r = G.api("GET", "messages", params={"q": 'in:sent to:jwizard@gmail.com subject:("Fw: Invitation" OR "Fw: Updated invitation") newer_than:14d', "maxResults": 50})
        ids = [m["id"] for m in r.get("messages", [])]
    for i in ids:
        if i in state: continue
        process(i, state)
    json.dump(state, open(STATE, "w"), indent=1, ensure_ascii=False)

if __name__ == "__main__":
    main()
