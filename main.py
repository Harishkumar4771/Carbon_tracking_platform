from fastapi import FastAPI, Request, Form, Depends, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
import os
import json

from database import engine, Base, get_db
from models import ActivityLog, User
from assistant import assistant_engine
from auth import verify_password, get_password_hash, create_access_token, get_current_user_id, ACCESS_TOKEN_EXPIRE_MINUTES

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Carbon Tracking Platform")

# Ensure directories exist
os.makedirs("templates", exist_ok=True)
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- Dependency ---
def get_current_user(request: Request, db: Session = Depends(get_db)):
    user_id = get_current_user_id(request)
    if not user_id:
        return None
    return db.query(User).filter(User.id == user_id).first()

def login_redirect():
    return RedirectResponse(url="/login", status_code=303)

# --- Routes ---

@app.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login_post(response: Response, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        return RedirectResponse(url="/login?error=Invalid+credentials", status_code=303)
    
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    res = RedirectResponse(url="/", status_code=303)
    res.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return res

@app.get("/register", response_class=HTMLResponse)
async def register_get(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register_post(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        return RedirectResponse(url="/register?error=Username+taken", status_code=303)
    
    new_user = User(username=username, password_hash=get_password_hash(password))
    db.add(new_user)
    db.commit()
    return RedirectResponse(url="/login?msg=Registration+successful", status_code=303)

@app.get("/logout")
async def logout():
    res = RedirectResponse(url="/login", status_code=303)
    res.delete_cookie("access_token")
    return res

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user:
        return login_redirect()

    logs = db.query(ActivityLog).filter(ActivityLog.user_id == current_user.id).order_by(ActivityLog.timestamp.desc()).all()
    total_emission = sum(log.carbon_emission for log in logs)
    
    # Chart Data Preparation
    emissions_by_cat = {"transportation": 0, "food": 0, "energy": 0}
    for log in logs:
        if log.category in emissions_by_cat:
            emissions_by_cat[log.category] += log.carbon_emission
            
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "logs": logs[:10], # recent 10 
        "total_emission": round(total_emission, 2),
        "user": current_user,
        "chart_data_pie": json.dumps(list(emissions_by_cat.values()))
    })

@app.get("/log", response_class=HTMLResponse)
async def log_form(request: Request, current_user: User = Depends(get_current_user)):
    if not current_user:
        return login_redirect()
    return templates.TemplateResponse("log.html", {"request": request, "user": current_user})

@app.post("/log")
async def add_log(
    category: str = Form(...),
    subcategory: str = Form(...),
    value: float = Form(...),
    description: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        return login_redirect()

    emission = assistant_engine.calculate_emission(category, subcategory, value)
    new_log = ActivityLog(
        category=category,
        description=description or f"{subcategory} ({value})",
        value=value,
        carbon_emission=emission,
        user_id=current_user.id
    )
    db.add(new_log)
    db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.post("/set-goal")
async def set_goal(goal: float = Form(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user:
        return login_redirect()
    
    current_user.monthly_goal = goal
    db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.get("/assistant", response_class=HTMLResponse)
async def assistant_view(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user:
        return login_redirect()
        
    logs = db.query(ActivityLog).filter(ActivityLog.user_id == current_user.id).all()
    insights = assistant_engine.generate_insights(logs)
    return templates.TemplateResponse("assistant.html", {"request": request, "insights": insights, "user": current_user})
