# BIMI setup for alef.aero (logo in Yahoo, Apple Mail, and later Gmail inboxes)

Do this AFTER the press blast finishes (after 12:00 PM Pacific, Oct 13).

## 1. Host the logo file

Upload `alef-logo-bimi.svg` (or the inverted variant) to the alef.aero website at an https address, for example:

    https://alef.aero/bimi/alef-logo.svg

Open that address in a browser and confirm the logo shows. The file is SVG Tiny Portable/Secure, 3.8 KB, square, with a solid background, as BIMI requires.

## 2. Check who else sends mail as @alef.aero

BIMI requires DMARC in quarantine mode. Once set, any mail claiming to be from @alef.aero that is NOT sent through Google Workspace (or another service listed in your SPF/DKIM) will land in recipients' spam folders.

Before step 3, list every system that sends as @alef.aero: website contact form, CRM, newsletter tool, support desk, accounting software. Each must either send through Google Workspace or be added to the SPF record / have its own DKIM. If unsure, keep `p=none` for two weeks and read the DMARC reports that arrive at press@alef.aero (they list every sending source), then switch.

## 3. DNS records (at the DNS provider for alef.aero)

Change the existing DMARC record:

    Type: TXT
    Name: _dmarc.alef.aero   (some providers want just "_dmarc")
    Value: v=DMARC1; p=quarantine; pct=100; rua=mailto:press@alef.aero

Add the BIMI record:

    Type: TXT
    Name: default._bimi.alef.aero   (some providers want just "default._bimi")
    Value: v=BIMI1; l=https://alef.aero/bimi/alef-logo.svg; a=;

Use the exact URL where you uploaded the SVG in step 1.

## 4. Validate

After DNS propagates (minutes to 24 hours), check at https://bimigroup.org/bimi-generator/ by entering `alef.aero`. It reports DMARC, the record, and whether the SVG passes.

## 5. What each mail provider needs

- Yahoo, AOL: logo appears with steps 1 to 4 alone, usually within a few days of sending mail.
- Apple Mail (iOS/macOS): same as Yahoo.
- Gmail: additionally requires a certificate. Verified Mark Certificate (VMC) from DigiCert or Entrust, about 1,500 USD/year, requires a registered trademark on the logo. Or a Common Mark Certificate (CMC), cheaper, no trademark needed if the logo has been in public use for 12+ months. Add `a=https://alef.aero/bimi/alef-vmc.pem` to the BIMI record once issued. Until then Gmail shows the Google account profile photo already set on press@alef.aero.

## Files

- `alef-logo-bimi.svg`: blue logo on white (brand version).
- `alef-logo-bimi-inverted.svg`: white logo on blue (more visible as a small circle).
