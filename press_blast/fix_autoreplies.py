import sys, json, re, time; sys.path.insert(0,".")
import gmail_sender as G
from email.utils import parseaddr
AUTO = re.compile(r"^\s*(re:\s*)?(automatic reply|auto(matic)?[- ]?reply|autoreply|auto:|out of (the )?office|ooo\b|away from|abwesenheit|automatische antwort|r[ée]ponse automatique|risposta automatica|respuesta autom|自動|thank you for your email|delivery status|undeliverable)", re.I)
def is_auto(h):
    return bool(AUTO.search(h.get("subject",""))) or h.get("auto-submitted","no").lower()!="no" or "x-autoreply" in h or "x-autorespond" in h
def first_from_display(name):
    name = re.sub(r"\(.*?\)", "", name or "").strip().strip('"')
    if not name or "@" in name: return ""
    if "," in name:
        parts=[p.strip() for p in name.split(",")]; name = parts[1] if len(parts)>1 and parts[1] else parts[0]
    toks=[t for t in re.split(r"\s+", name) if t and not re.match(r"^(mr|ms|mrs|dr)\.?$", t, re.I)]
    return toks[0] if toks else ""
rows=json.load(open("send_list_final.json"))
changed=[]; auto_only=[]
for i,r in enumerate(rows):
    if r["mode"]!="reply": continue
    res=G.api("GET","messages",params={"q":f"from:{r['email']}","maxResults":15})
    cands=[]
    for m in res.get("messages",[]):
        md=G.api("GET",f"messages/{m['id']}",params={"format":"metadata","metadataHeaders":["From","Subject","Message-ID","References","To","Cc","Auto-Submitted","X-Autoreply","X-Autorespond"]})
        h={x["name"].lower():x["value"] for x in md.get("payload",{}).get("headers",[])}
        cands.append((int(md["internalDate"]), m["id"], md["threadId"], h))
    cands.sort(reverse=True)
    if not cands: continue
    real=[c for c in cands if not is_auto(c[3])]
    was_auto = is_auto({"subject": r.get("subject","")})
    if real:
        ts,mid,tid,h=real[0]
        if mid!=r["reply_msg_id"]:
            changed.append((r["email"], r.get("subject","")[:50], "->", h.get("subject","")[:50]))
            r.update(reply_msg_id=mid, thread_id=tid, reply_message_id_hdr=h.get("message-id",""), references=h.get("references",""),
                     subject=h.get("subject",""), last_to=h.get("to",""), last_cc=h.get("cc",""),
                     last_from_them=time.strftime("%Y-%m-%d", time.gmtime(ts/1000)))
            d,_=parseaddr(h.get("from","")); fn=first_from_display(d)
            if fn and r["first_name_source"]!="manual review": r["first_name"]=fn; r["first_name_source"]="email From header"
    else:
        auto_only.append((r["email"], cands[0][3].get("subject","")[:60]))
    if i%50==0: print(i, flush=True)
    time.sleep(0.02)
json.dump(rows, open("send_list_final.json","w"), indent=1)
print("changed:", len(changed)); [print("  ", c) for c in changed]
print("auto-reply only (no real email exists):", len(auto_only)); [print("  ", a) for a in auto_only]
