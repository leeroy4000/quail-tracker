# Quail Tracker

A mobile-friendly, self-hosted web app for managing coturnix quail incubation batches and daily egg production. Built for homesteaders running a home server.

![App icon](app/static/icon-192.png)

---

## Features

- **Multi-batch calendar** — Track multiple incubation batches simultaneously on a shared calendar view. Each batch generates its full incubation and brooder milestone timeline automatically.
- **Milestone guidance** — Every key event (candling, lockdown, hatch, sexing, harvest window) includes temperature targets, humidity targets, and practical tips.
- **Egg production log** — Log daily egg counts with hen count and notes. Tap any past date to review or edit entries.
- **Calendar export** — Download a `.ics` file or subscribe via URL to sync milestones into Google Calendar, Apple Calendar, or Outlook.
- **Print view** — Print-optimized layout expands the calendar to show full event labels in each day cell.
- **Home screen installable** — Includes a web app manifest for adding to your Android or iOS home screen as a standalone app.
- **Craftsman aesthetic** — Warm earth tones, serif headings, designed to feel at home on a homestead.

---

## Stack

- **Backend:** Python / Flask / Gunicorn
- **Frontend:** Single-file HTML + CSS + JS (no framework)
- **Storage:** JSON file on the host (mounted as a Docker volume)
- **Deployment:** Docker + Docker Compose

---

## Setup

### Prerequisites

- Docker and Docker Compose installed on your server
- A directory structure like `/opt/docker-compose/` and `/opt/containers/` (or adjust paths to your preference)

### 1. Clone the repo

```bash
git clone https://github.com/leeroy4000/quail-tracker.git /opt/docker-compose/quail-tracker
```

### 2. Create the data directory

```bash
mkdir -p /opt/containers/quail-tracker/data
```

### 3. Create your `.env` file

```bash
cat > /opt/docker-compose/quail-tracker/.env << 'EOF'
TZ=America/Chicago
EOF
```

Adjust the timezone to your local zone.

### 4. Build and start

```bash
cd /opt/docker-compose/quail-tracker
docker compose up -d --build
```

### 5. Open the app

```
http://<your-server-ip>:5000
```

---

## Updating

```bash
cd /opt/docker-compose/quail-tracker
git pull
docker compose up -d --build
```

---

## Reverse Proxy (Optional)

To serve the app via a hostname instead of IP:port, see `Caddyfile-snippet.txt` for an example Caddy configuration.

---

## Project Structure

```
quail-tracker/
├── app/
│   ├── app.py                  # Flask backend + ICS calendar endpoint
│   ├── requirements.txt        # Python dependencies
│   ├── Dockerfile
│   ├── static/
│   │   ├── icon-180.png        # Apple touch icon
│   │   ├── icon-192.png        # Android home screen icon
│   │   ├── icon-512.png        # High-res icon
│   │   └── manifest.json       # Web app manifest
│   └── templates/
│       └── index.html          # Frontend (single-file HTML/CSS/JS)
├── docker-compose.yml
├── Caddyfile-snippet.txt
├── .gitignore
└── README.md
```

---

## Data

App data is stored at `/opt/containers/quail-tracker/data/quail_data.json` on the host, mounted into the container as a volume. This file is excluded from git and persists across container rebuilds.

---

## Calendar Subscription

Once running, your milestones are available as a live iCalendar feed at:

```
http://<your-server-ip>:5000/calendar.ics
```

Paste this URL into any calendar app's "subscribe to calendar" feature. New batches you add will automatically appear on your next sync.

---

## Coturnix Quick Reference

| Event | Timeline |
|---|---|
| Incubation | 17–18 days |
| Lockdown | Day 15 |
| Hatch | Days 17–18 |
| Move to brooder | Day 0 post-hatch |
| Sexing window | Week 3 |
| Harvest window | Weeks 6–8 |
| Egg production begins | Weeks 6–8 |
| Colony ratio | 1 rooster : 4–5 hens |

---

## License

MIT
