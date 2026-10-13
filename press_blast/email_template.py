# Builds the exact email body (HTML + plain text) from the approved .docx text.
import html

SUBJECT = "Alef flying car vs Tesla Roadster press release"
CAPTION = "real photo, not AI, of Alef flying over Tesla Roadster, Cybertruck"
IMAGE_FILE = "alef_over_tesla_800.jpg"
IMAGE_CID = "alef_over_tesla_800.jpg"   # connector derives Content-ID from filename

def build_html(first_name: str) -> str:
    hi = f"Hi {html.escape(first_name)}." if first_name else "Hi."
    F = 'font-family:Arial,Helvetica,sans-serif;font-size:14px;line-height:1.4;color:#000'
    P = f'style="margin:0 0 1em 0;{F}"'
    return f"""<div>
<p {P}>{hi} We have a major Press Release from Alef, please let me know if you agree to an embargo.</p>
<p {P}><b>Elon Musk is scheduled to unveil a new <u>flying</u> Tesla Roadster on Thu, Oct 15</b>, and, if true, it will be the <b>second flying car after Alef</b>.</p>
<p {P}>Alef pre-emptively prepared a Press Release with:</p>
<p style="margin:0;{F}">1.<b> Videos of Alef flying over Tesla Roadster</b><br>
2. Comparison of Alef (1st flying car) vs Tesla Roadster (2nd flying car): drive + vertical takeoff</p>
<p style="margin:1em 0 0 0;{F}">The embargo is until after the Tesla Roadster Unveiling.<br>
Please let me know if you agree to the embargo and want the press release and videos.</p>
<p style="margin:1em 0 0 0;{F}">Thanks,<br>
Alef Press Team (Anna)</p>
<p style="margin:1em 0 0 0;{F}"><i>p.s. Alef’s CEO Jim Dukhovny is available for an interview any time during and after October 15.</i></p>
<p style="margin:1.5em 0 0 0;{F}"><img src="cid:{IMAGE_CID}" width="600" style="display:block;max-width:100%;height:auto;border:0" alt="Alef flying over Tesla Roadster and Cybertruck"><br>
<span style="font-size:12px;color:#444">{html.escape(CAPTION)}</span></p>
</div>"""

def build_text(first_name: str) -> str:
    hi = f"Hi {first_name}." if first_name else "Hi."
    return f"""{hi} We have a major Press Release from Alef, please let me know if you agree to an embargo.

Elon Musk is scheduled to unveil a new flying Tesla Roadster on Thu, Oct 15, and, if true, it will be the second flying car after Alef.

Alef pre-emptively prepared a Press Release with:

1. Videos of Alef flying over Tesla Roadster
2. Comparison of Alef (1st flying car) vs Tesla Roadster (2nd flying car): drive + vertical takeoff

The embargo is until after the Tesla Roadster Unveiling.
Please let me know if you agree to the embargo and want the press release and videos.

Thanks,
Alef Press Team (Anna)

p.s. Alef’s CEO Jim Dukhovny is available for an interview any time during and after October 15.

[photo: {CAPTION}]
"""

if __name__ == "__main__":
    import sys, json, base64
    name = sys.argv[1] if len(sys.argv) > 1 else ""
    out = {"subject": SUBJECT, "htmlBody": build_html(name), "body": build_text(name),
           "image_b64": base64.b64encode(open(IMAGE_FILE, "rb").read()).decode()}
    json.dump(out, open("test_payload.json", "w"))
    print(out["htmlBody"]); print(len(out["image_b64"]))
