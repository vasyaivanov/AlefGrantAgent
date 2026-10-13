import sys, json, re, time; sys.path.insert(0,".")
import gmail_sender as G
from email.utils import parseaddr
def first_from_display(name):
    name = re.sub(r"\(.*?\)", "", name or "").strip().strip('"')
    if not name or "@" in name: return ""
    if "," in name:
        parts = [p.strip() for p in name.split(",")]
        name = parts[1] if len(parts) > 1 and parts[1] else parts[0]
    toks = [t for t in re.split(r"\s+", name) if t and not re.match(r"^(mr|ms|mrs|dr)\.?$", t, re.I)]
    return toks[0] if toks else ""
rows=json.load(open("send_list_resolved.json"))
for i,r in enumerate(rows):
    if r["mode"]!="reply": continue
    md=G.api("GET", f"messages/{r['reply_msg_id']}", params={"format":"metadata","metadataHeaders":["From","Subject","Message-ID","References","To","Cc"]})
    h={x["name"].lower():x["value"] for x in md["payload"]["headers"]}
    r["reply_message_id_hdr"]=h.get("message-id",""); r["references"]=h.get("references","")
    r["subject"]=h.get("subject",""); r["last_to"]=h.get("to",""); r["last_cc"]=h.get("cc","")
    disp,addr=parseaddr(h.get("from","")); r["from_display"]=disp
    fn=first_from_display(disp)
    if fn: r["first_name"],r["first_name_source"]=fn,"email From header"
    if i%50==0: print(i, r["email"], disp, "->", r["first_name"], flush=True)
    time.sleep(0.03)
json.dump(rows, open("send_list_resolved.json","w"), indent=1)
from collections import Counter
print(Counter(r["first_name_source"] for r in rows))
print("missing msgid:", sum(1 for r in rows if r["mode"]=="reply" and not r["reply_message_id_hdr"]))
