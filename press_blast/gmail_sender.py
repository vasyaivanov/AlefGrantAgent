"""Send via the Gmail API with the press@alef.aero OAuth token (multipart/related inline image, true replies)."""
import json, os, time, base64, urllib.request, urllib.parse, mimetypes
from email.message import EmailMessage
from email.utils import make_msgid, formatdate

SECRETS = "/tmp/claude-0/-home-user-AlefGrantAgent/e458df72-e1db-5bd3-9535-10dd87daee1a/scratchpad/secrets"
_tok = None

def access_token():
    global _tok
    if _tok and _tok["exp"] > time.time() + 60:
        return _tok["access_token"]
    c = json.load(open(SECRETS + "/client_secret.json"))["installed"]
    t = json.load(open(SECRETS + "/token.json"))
    data = urllib.parse.urlencode({"client_id": c["client_id"], "client_secret": c["client_secret"],
                                   "refresh_token": t["refresh_token"], "grant_type": "refresh_token"}).encode()
    r = json.load(urllib.request.urlopen(urllib.request.Request(c["token_uri"], data=data), timeout=30))
    _tok = {"access_token": r["access_token"], "exp": time.time() + r.get("expires_in", 3600)}
    return _tok["access_token"]

def api(method, path, body=None, params=None):
    url = "https://gmail.googleapis.com/gmail/v1/users/me/" + path
    if params: url += "?" + urllib.parse.urlencode(params, doseq=True)
    req = urllib.request.Request(url, method=method, headers={"Authorization": "Bearer " + access_token(),
                                                             "Content-Type": "application/json"})
    r = urllib.request.urlopen(req, data=json.dumps(body).encode() if body is not None else None, timeout=60)
    return json.load(r)

def build(to, subject, text, html, image_path=None, cid=None, in_reply_to=None, references=None, cc=None):
    msg = EmailMessage()
    msg["From"] = "Alef Flying Car Press <press@alef.aero>"
    msg["To"] = to
    if cc: msg["Cc"] = cc
    msg["Subject"] = subject
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain="alef.aero")
    if in_reply_to:
        msg["In-Reply-To"] = in_reply_to
        msg["References"] = (references + " " if references else "") + in_reply_to
    msg.set_content(text)
    if image_path and cid:
        html = html.replace("cid:" + cid, "cid:" + cid)  # html already references cid
        msg.add_alternative(html, subtype="html")
        with open(image_path, "rb") as f:
            data = f.read()
        mt = mimetypes.guess_type(image_path)[0] or "image/jpeg"
        maintype, subtype = mt.split("/")
        msg.get_payload()[1].add_related(data, maintype, subtype, cid="<" + cid + ">",
                                         filename=os.path.basename(image_path), disposition="inline")
    else:
        msg.add_alternative(html, subtype="html")
    return msg

def send(msg, thread_id=None):
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    body = {"raw": raw}
    if thread_id: body["threadId"] = thread_id
    return api("POST", "messages/send", body)

if __name__ == "__main__":
    import sys
    print(api("GET", "profile"))
