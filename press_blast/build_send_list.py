import sys, json, re, time, csv, urllib.parse
sys.path.insert(0, ".")
import gmail_sender as G
from email.utils import parseaddr

rows = json.load(open("send_list_raw.json"))
excl = {r[2].lower() for r in csv.reader(open("already_contacted_sep27-28.csv")) if "@" in r[2]}
excl |= {"kevin.nious@nbcuni.com","steve.patterson1@nbcuni.com","ashley.n.schwartzlavares@abc.com"}

def norm(e): return e.strip().lower()
def first_from_display(name):
    name = re.sub(r"\(.*?\)", "", name or "").strip().strip('"')
    if not name or "@" in name: return ""
    if "," in name:  # "Last, First"
        parts = [p.strip() for p in name.split(",")]
        name = parts[1] if len(parts) > 1 and parts[1] else parts[0]
    toks = [t for t in re.split(r"\s+", name) if t and not re.match(r"^(mr|ms|mrs|dr)\.?$", t, re.I)]
    return toks[0] if toks else ""
def first_from_sheet(name):
    n = re.sub(r"\(.*", "", name or "").strip()
    toks = n.split()
    if not toks: return ""
    if len(toks) == 1: return toks[0]
    return toks[0]

out = []
for i, r in enumerate(rows):
    emails = [norm(e) for e in re.split(r"[;,]", r["Email"]) if "@" in e]
    rec = {"name_sheet": r["Name"], "outlet": r["Media name"], "tab": r["tab"], "kind": r["kind"],
           "emails": emails, "email": emails[0], "mode": "new", "thread_id": "", "reply_msg_id": "",
           "reply_message_id_hdr": "", "references": "", "subject": "", "last_from_them": "",
           "first_name": "", "first_name_source": "", "note": "", "last_to": "", "last_cc": ""}
    best = None
    for e in emails:
        q = f"from:{e}"
        try:
            res = G.api("GET", "messages", params={"q": q, "maxResults": 5})
        except Exception as ex:
            rec["note"] += f"search error {e}: {ex}; "; continue
        for m in res.get("messages", []):
            md = G.api("GET", f"messages/{m['id']}", params={"format": "metadata",
                       "metadataHeaders": ["From","Subject","Message-ID","References","Date","To","Cc"]})
            hdr = {h["name"].lower(): h["value"] for h in md.get("payload", {}).get("headers", [])}
            ts = int(md["internalDate"])
            if best is None or ts > best["ts"]:
                best = {"ts": ts, "id": m["id"], "thread": md["threadId"], "hdr": hdr, "email": e}
        time.sleep(0.05)
    if best:
        h = best["hdr"]
        rec.update(mode="reply", thread_id=best["thread"], reply_msg_id=best["id"],
                   reply_message_id_hdr=h.get("message-id",""), references=h.get("references",""),
                   subject=h.get("subject",""), email=best["email"], last_to=h.get("to",""), last_cc=h.get("cc",""),
                   last_from_them=time.strftime("%Y-%m-%d", time.gmtime(best["ts"]/1000)))
        disp, addr = parseaddr(h.get("from",""))
        fn = first_from_display(disp)
        if fn: rec["first_name"], rec["first_name_source"] = fn, "email From header"
    if not rec["first_name"]:
        fn = first_from_sheet(r["Name"])
        rec["first_name"], rec["first_name_source"] = fn, "spreadsheet" if fn else "none"
    out.append(rec)
    if i % 25 == 0: print(i, rec["email"], rec["mode"], rec["first_name"], flush=True)
json.dump(out, open("send_list_resolved.json", "w"), indent=1)
from collections import Counter
print("modes:", Counter(r["mode"] for r in out)); print("name source:", Counter(r["first_name_source"] for r in out))
