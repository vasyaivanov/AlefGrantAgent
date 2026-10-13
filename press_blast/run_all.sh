#!/bin/bash
# Full campaign: send on schedule, report right after the last send, bounce report at 6:00 PM Pacific.
cd /home/user/AlefGrantAgent/press_blast
python3 run_campaign.py send
python3 run_campaign.py report
# wait until 18:00 Pacific
while [ "$(TZ=America/Los_Angeles date +%H%M)" -lt 1800 ]; do [ -f STOP ] && exit 0; sleep 60; done
python3 run_campaign.py bounces
