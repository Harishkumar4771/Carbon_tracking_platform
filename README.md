# Carbon Footprint Awareness Platform

A smart, dynamic web application designed to help individuals understand, track, and reduce their carbon footprint through simple actions and personalized insights.

## Live Demo
[https://carbon-tracking-platform-264552446639.us-central1.run.app](https://carbon-tracking-platform-264552446639.us-central1.run.app)

## Features
- **Dynamic Assistant:** Context-aware rule-based recommendations based on your daily activities.
- **Activity Logging:** Track emissions from transportation, food, and energy usage.
- **Beautiful UI:** Modern Glassmorphism design and fully responsive layout.
- **Lightweight Architecture:** Uses FastAPI and SQLite, making the entire project well under 10MB.

## Technology Stack
- **Backend:** FastAPI (Python)
- **Database:** SQLite
- **Frontend:** Vanilla HTML, CSS, JavaScript
- **Deployment:** Google Cloud Run (Docker)

## Local Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application:
   ```bash
   uvicorn main:app --reload
   ```
3. Open `http://127.0.0.1:8000` in your browser.

## Deployment on Google Cloud Run

This project includes a `Dockerfile` for easy containerization.
To deploy via Google Cloud SDK:

```bash
gcloud run deploy carbon-tracker --source . --platform managed --allow-unauthenticated
```
