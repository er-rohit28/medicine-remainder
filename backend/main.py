"""
main.py - FastAPI Backend for Medicine Reminder System
Endpoints:
  Auth       : POST /signup, POST /login
  Medicines  : POST /medicines, GET /medicines, PUT /medicines/{id}, DELETE /medicines/{id}
  Reminders  : POST /reminders, GET /reminders/today, PUT /reminders/{id}/status
  History    : GET /history
  Dashboard  : GET /dashboard/stats
"""

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
import hashlib
import os
import sys

# Ensure backend directory is in sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from database import get_supabase

# ── App setup ──────────────────────────────────────────────────────────────────
app = FastAPI(title="Medicine Reminder API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # allow the frontend (opened as file://) to call the API
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = get_supabase()


# ── Helpers ────────────────────────────────────────────────────────────────────
def hash_password(password: str) -> str:
    """Simple SHA-256 hash (good enough for a college prototype)."""
    return hashlib.sha256(password.encode()).hexdigest()


def get_user_from_token(token: str):
    """
    In this prototype the 'token' is just the user's id (as a string).
    In a real app you'd use JWT. Keeping it simple for viva explanation.
    """
    try:
        user_id = int(token)
        result = db.table("users").select("*").eq("id", user_id).execute()
        if result.data:
            return result.data[0]
        return None
    except Exception:
        return None


# ── Pydantic schemas (request bodies) ─────────────────────────────────────────
class SignupRequest(BaseModel):
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class MedicineCreate(BaseModel):
    name: str
    dosage: str
    frequency: str
    reminder_time: str          # "HH:MM"
    start_date: str             # "YYYY-MM-DD"
    end_date: str
    instructions: Optional[str] = ""


class MedicineUpdate(BaseModel):
    name: Optional[str] = None
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    reminder_time: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    instructions: Optional[str] = None


class ReminderCreate(BaseModel):
    medicine_id: int
    scheduled_time: str   # "HH:MM"
    scheduled_date: str   # "YYYY-MM-DD"


class StatusUpdate(BaseModel):
    status: str           # "taken" or "skipped"
    medicine_name: str    # used to write to dose_history


# ── Auth Routes ────────────────────────────────────────────────────────────────
@app.post("/signup")
def signup(req: SignupRequest):
    """Register a new user."""
    # Check if email already exists
    existing = db.table("users").select("id").eq("email", req.email).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = hash_password(req.password)
    result = db.table("users").insert({
        "username": req.username,
        "email": req.email,
        "password_hash": hashed,
    }).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Could not create user")

    user = result.data[0]
    return {"message": "Account created!", "user_id": user["id"], "username": user["username"]}


@app.post("/login")
def login(req: LoginRequest):
    """Login and return user_id as token."""
    hashed = hash_password(req.password)
    result = (
        db.table("users")
        .select("*")
        .eq("email", req.email)
        .eq("password_hash", hashed)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user = result.data[0]
    # Token = user_id string (simple, beginner-friendly approach)
    return {
        "message": "Login successful",
        "token": str(user["id"]),
        "user_id": user["id"],
        "username": user["username"],
    }


# ── Medicine Routes ────────────────────────────────────────────────────────────
@app.post("/medicines")
def add_medicine(req: MedicineCreate, authorization: str = Header(...)):
    """Add a new medicine for the logged-in user."""
    user = get_user_from_token(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    result = db.table("medicines").insert({
        "user_id": user["id"],
        "name": req.name,
        "dosage": req.dosage,
        "frequency": req.frequency,
        "reminder_time": req.reminder_time,
        "start_date": req.start_date,
        "end_date": req.end_date,
        "instructions": req.instructions,
    }).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Could not add medicine")

    return {"message": "Medicine added!", "medicine": result.data[0]}


@app.get("/medicines")
def get_medicines(authorization: str = Header(...)):
    """Get all medicines for the logged-in user."""
    user = get_user_from_token(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    result = (
        db.table("medicines")
        .select("*")
        .eq("user_id", user["id"])
        .order("created_at", desc=True)
        .execute()
    )
    return {"medicines": result.data}


@app.put("/medicines/{medicine_id}")
def update_medicine(medicine_id: int, req: MedicineUpdate, authorization: str = Header(...)):
    """Update a medicine."""
    user = get_user_from_token(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Build only the fields that were provided
    update_data = {k: v for k, v in req.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = (
        db.table("medicines")
        .update(update_data)
        .eq("id", medicine_id)
        .eq("user_id", user["id"])
        .execute()
    )
    return {"message": "Medicine updated!", "medicine": result.data[0] if result.data else {}}


@app.delete("/medicines/{medicine_id}")
def delete_medicine(medicine_id: int, authorization: str = Header(...)):
    """Delete a medicine."""
    user = get_user_from_token(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    db.table("medicines").delete().eq("id", medicine_id).eq("user_id", user["id"]).execute()
    return {"message": "Medicine deleted!"}


# ── Reminder Routes ────────────────────────────────────────────────────────────
@app.post("/reminders")
def create_reminder(req: ReminderCreate, authorization: str = Header(...)):
    """Create a reminder entry for a specific date."""
    user = get_user_from_token(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    result = db.table("reminders").insert({
        "medicine_id": req.medicine_id,
        "user_id": user["id"],
        "scheduled_time": req.scheduled_time,
        "scheduled_date": req.scheduled_date,
        "status": "pending",
    }).execute()

    return {"message": "Reminder created!", "reminder": result.data[0] if result.data else {}}


@app.get("/reminders/today")
def get_todays_reminders(authorization: str = Header(...)):
    """Get all reminders for today, joined with medicine name."""
    user = get_user_from_token(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    today = str(date.today())   # "YYYY-MM-DD"

    reminders = (
        db.table("reminders")
        .select("*, medicines(name, dosage)")
        .eq("user_id", user["id"])
        .eq("scheduled_date", today)
        .order("scheduled_time")
        .execute()
    )
    return {"reminders": reminders.data, "date": today}


@app.put("/reminders/{reminder_id}/status")
def update_reminder_status(reminder_id: int, req: StatusUpdate, authorization: str = Header(...)):
    """Mark a reminder as taken or skipped, and log to dose_history."""
    user = get_user_from_token(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if req.status not in ("taken", "skipped"):
        raise HTTPException(status_code=400, detail="Status must be 'taken' or 'skipped'")

    # Update reminder status
    db.table("reminders").update({"status": req.status}).eq("id", reminder_id).execute()

    # Log to dose_history
    now = datetime.now()
    db.table("dose_history").insert({
        "user_id": user["id"],
        "reminder_id": reminder_id,
        "medicine_name": req.medicine_name,
        "taken_date": str(now.date()),
        "taken_time": now.strftime("%H:%M"),
        "status": req.status,
    }).execute()

    return {"message": f"Reminder marked as {req.status}"}


# ── History Route ──────────────────────────────────────────────────────────────
@app.get("/history")
def get_history(authorization: str = Header(...)):
    """Get all dose history for the logged-in user."""
    user = get_user_from_token(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    result = (
        db.table("dose_history")
        .select("*")
        .eq("user_id", user["id"])
        .order("taken_date", desc=True)
        .execute()
    )
    return {"history": result.data}


# ── Dashboard Stats ────────────────────────────────────────────────────────────
@app.get("/dashboard/stats")
def dashboard_stats(authorization: str = Header(...)):
    """Return summary counts for the dashboard."""
    user = get_user_from_token(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    today = str(date.today())

    # Total medicines
    medicines = db.table("medicines").select("id").eq("user_id", user["id"]).execute()
    total_medicines = len(medicines.data)

    # Today's reminders
    todays = (
        db.table("reminders")
        .select("status")
        .eq("user_id", user["id"])
        .eq("scheduled_date", today)
        .execute()
    )
    today_total = len(todays.data)
    taken = sum(1 for r in todays.data if r["status"] == "taken")
    pending = sum(1 for r in todays.data if r["status"] == "pending")

    return {
        "username": user["username"],
        "total_medicines": total_medicines,
        "todays_reminders": today_total,
        "taken_today": taken,
        "pending_today": pending,
    }


# ── Mount Frontend Static Files ───────────────────────────────────────────────
from fastapi.staticfiles import StaticFiles
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")


# ── Run ────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

