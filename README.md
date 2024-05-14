@Apprentices AiShields Draft Web Front End Setup:
BCAMP.dev Data and AI Cohort Spring 2024

Project: Data Sanitizer for AI
AiShields Web Front End:

Dependencies: Python 3.12.3, Sqlite3 

1. a) Unix/Linux/Mac: 
```commandline
mkdir aiShieldsLocal
cd aiShieldsLocal
```
Run the file: `AiShieldsWeb/cloneMostRecentAndSetupEnv.sh`

   b) Windows: 
```commandline
        git clone https://github.com/AiShieldsOrg/AiShieldsWeb.git
        cd AiShieldsWeb
        python3.12 -m venv .venv
        source /Users/pmk/Documents/AiShieldsWeb/.venv/bin/activate
        pip3.12 install -r requirements.txt
```

2. Certificate for Dev Encryption Setup
    a) Download the file located in our discord server: https://discordapp.com/channels/1229942715450523658/1229998804099403777/1234622867199758366
    Download and copy the file:
Patrick-5e39e57f-0550-49f3-8db6-d33cd139168f.pem
to helpers/Patrick-5e39e57f-0550-49f3-8db6-d33cd139168f.pem
(file from Discord Server App # desktop-web-frontend)
3. After you copy correct pem file, change the file setting to executable:
```commandline
chmod +x  helpers/Patrick-5e39e57f-0550-49f3-8db6-d33cd139168f.pem 
```
4. As soon as the file is executable, show the correct path in `self_protection.py` line 17:
```python
strPEMfileName = './helpers/Patrick-5e39e57f-0550-49f3-8db6-d33cd139168f.pem'
```
5. Download .env file from discord: https://discord.com/channels/1229942715450523658/1230004837845045369/1239983795839565905
Do not forget to rename file into `.env` (discord renames them into env). Put this file into project working directory.
Do not forget to set the correct local path to your sqllite 3 `sqlite3:////` in your .env file
6. Set the secret SQLite key to your_secret_key [optional]
```python
app.config['SECRET_KEY'] = 'your_secret_key' 
```
7. run in Flask or debug in IDE:

UNIX/MacOS/Linux 
run the `run_flask_app.sh`

Windows:
```commandline
$env:FLASK_APP = "app.py"
flask run --host=0.0.0.0 --port=5000
```



