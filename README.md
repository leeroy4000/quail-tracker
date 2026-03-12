# Quail Tracker

Mobile-friendly self-hosted web app for tracking coturnix quail incubation timelines and daily egg production.

Built with Flask, served via Gunicorn, deployed via Docker on a home server.

## Features

- **Incubation Tracker** — Enter a start date, get a full day-by-day timeline with today highlighted and next-milestone countdown
- **Brooder & Grow-Out** — Auto-calculates from hatch date through 8-week grow-out
- **Egg Production Log** — Daily entry form with running totals and 7-day rolling average

---

## First-Time Setup

### 1. Clone the repo

```bash
git clone https://github.com/<your-username>/quail-tracker.git /opt/docker-compose/quail-tracker
```

### 2. Create the data directory

```bash
mkdir -p /opt/containers/quail-tracker/data
```

### 3. Build and start

```bash
docker compose -f /opt/docker-compose/quail-tracker/docker-compose.yml up -d --build
```

### 4. Access the app

Open `http://192.168.1.7:5055` in your browser (or over VPN when away from home).

---

## Updating

```bash
cd /opt/docker-compose/quail-tracker
git pull
docker compose up -d --build
```

---

## Caddy Reverse Proxy (Optional)

To access via a hostname instead of IP:port, add the contents of `Caddyfile-snippet.txt`
to the Caddyfile on your Caddy LXC (`192.168.1.11`), then reload:

```bash
caddy reload --config /path/to/Caddyfile
```

---

## Project Structure

```
quail-tracker/
├── app/
│   ├── app.py              # Flask backend
│   ├── requirements.txt    # Python dependencies
│   ├── Dockerfile
│   └── templates/
│       └── index.html      # Frontend (single-file HTML/CSS/JS)
├── docker-compose.yml
├── .env                    # Timezone and environment variables
├── .gitignore
├── Caddyfile-snippet.txt
└── README.md
```

---

## Data

App data is stored at `/opt/containers/quail-tracker/data/quail_data.json` on the host.
This path is mounted as a Docker volume and is excluded from git.
