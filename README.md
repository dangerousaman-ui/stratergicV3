# Strategic Dashboard for Uttarakhand

A Flask-based, Render-ready executive dashboard with a Spline-inspired hero section and a live public-information dashboard for Uttarakhand.

## Included
- Cinematic landing page inspired by the attached visual reference
- Main heading: Strategic Dashboard for LT. GEN. GURMIT SINGH AVSM, PVSM, UYSM, VSM
- Subtitle: Governor of Uttarakhand
- Governor, Chief Minister, Prime Minister, and PMO source cards
- Uttarakhand local news feed
- Uttarakhand law and policy watch feed
- Chief Minister watch feed
- Prime Minister / PMO public updates
- Dehradun weather via Open-Meteo
- NASA GIBS satellite image panel
- Finance snapshot
- PWA manifest and service worker
- Render deployment config

## Project structure
```text
strategic-dashboard-render-v2/
├── app.py
├── requirements.txt
├── render.yaml
├── README.md
├── .gitignore
├── templates/
│   └── index.html
└── static/
    ├── styles.css
    ├── app.js
    ├── manifest.json
    └── service-worker.js
```

## Run locally
### macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

### Windows PowerShell
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Then open:
```text
http://127.0.0.1:8000
```

## Push to GitHub
```bash
git init
git add .
git commit -m "Initial strategic dashboard"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
git push -u origin main
```

## Publish on Render
1. Create a new GitHub repository and push all files.
2. Sign in to Render.
3. Click **New** → **Web Service**.
4. Connect your GitHub account.
5. Select your repository.
6. Confirm these settings:
   - Runtime: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
7. Click **Create Web Service**.
8. Wait for the deploy to finish.
9. Open the generated `onrender.com` URL.

## Notes
- The app reads the `PORT` environment variable automatically, so it works on Render without extra changes.
- News uses Google News RSS search results.
- Weather uses Open-Meteo.
- Satellite imagery uses NASA GIBS.
- Finance uses Frankfurter and CoinGecko.

## Troubleshooting
### Build fails on Render
Check that `requirements.txt` and `app.py` are in the repo root.

### App starts but some cards are empty
One of the public upstream APIs may be temporarily rate-limited or unavailable. Refresh the page and try again.

### Local server does not start
Make sure your virtual environment is activated and dependencies installed first.

## Clean hero note
This package keeps the same dashboard and styling, but removes any dependency on manually uploaded hero screenshots. The landing screen uses CSS-generated beams/background only.
