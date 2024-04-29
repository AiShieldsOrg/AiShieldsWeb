#!/bin/bash
git clone https://github.com/AiShieldsOrg/AiShieldsWeb.git
python3.12 -m venv .venv
source /Users/pmk/Documents/AiShieldsWeb/.venv/bin/activate
cd AiShieldsWeb
pip3.12 install -r requirements.txt
export FLASK_APP=app.py
flask run --host=0.0.0.0 --port=8000
