from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import os

from database import engine, Base, get_db
from models import ActivityLog
from assistant import assistant_engine

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Carbon Tracking Platform")

# Ensure directories exist
os.makedirs("templates", exist_ok=True)
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    logs = db.query(ActivityLog).order_by(ActivityLog.timestamp.desc()).all()
    total_emission = sum(log.carbon_emission for log in logs)
    return templates.TemplateResponse("index.html", {"request": request, "logs": logs, "total_emission": round(total_emission, 2)})

@app.get("/log", response_class=HTMLResponse)
async def log_form(request: Request):
    return templates.TemplateResponse("log.html", {"request": request})

@app.post("/log")
async def add_log(
    category: str = Form(...),
    subcategory: str = Form(...),
    value: float = Form(...),
    description: str = Form(""),
    db: Session = Depends(get_db)
):
    emission = assistant_engine.calculate_emission(category, subcategory, value)
    new_log = ActivityLog(
        category=category,
        description=description or f"{subcategory} ({value})",
        value=value,
        carbon_emission=emission
    )
    db.add(new_log)
    db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.get("/assistant", response_class=HTMLResponse)
async def assistant_view(request: Request, db: Session = Depends(get_db)):
    logs = db.query(ActivityLog).all()
    insights = assistant_engine.generate_insights(logs)
    return templates.TemplateResponse("assistant.html", {"request": request, "insights": insights})
