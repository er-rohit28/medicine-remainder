# 💊 MediRemind – Medicine Reminder System

A simple, beginner-friendly Medicine Reminder System built with:
- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python + FastAPI
- **Database**: Supabase (PostgreSQL)

> Built as a 2nd-year Computer Engineering college prototype to demonstrate Python OOP, CRUD, and basic web development.

---

## 📁 Project Structure

```
Medicine Reminder/
│
├── backend/
│   ├── main.py          ← FastAPI app (all API routes)
│   ├── models.py        ← Python OOP classes (Medicine, User, etc.)
│   ├── database.py      ← Supabase connection
│   └── requirements.txt ← Python packages
│
├── frontend/
│   ├── index.html       ← Login / Signup page
│   ├── dashboard.html   ← Dashboard (stats + quick actions)
│   ├── medicines.html   ← Manage medicines (CRUD)
│   ├── add-medicine.html← Add medicine form
│   ├── schedule.html    ← Today's schedule (Taken/Skip)
│   ├── history.html     ← Dose history
│   └── style.css        ← Global stylesheet
│
├── schema.sql           ← Run this in Supabase SQL Editor
├── .env.example         ← Copy to .env with your credentials
├── .gitignore
└── README.md
```

---

## 🚀 Setup Instructions (Step by Step)

### Step 1 – Create Supabase Project

1. Go to [https://supabase.com](https://supabase.com) → Sign up → **New Project**
2. Go to **SQL Editor** → Click **New query**
3. Paste the contents of `schema.sql` → Click **Run**
4. Go to **Settings → API** → Copy:
   - **Project URL** (looks like `https://xxxx.supabase.co`)
   - **Anon public key**

### Step 2 – Configure Environment

```bash
# In the Medicine Reminder folder, create a .env file:
copy .env.example .env
```

Open `.env` and replace the placeholder values:
```
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-public-key-here
```

### Step 3 – Set Up Python Backend

Open a terminal in VS Code (`Ctrl + `` ` ``):

```bash
# Navigate to backend folder
cd backend

# Create a virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### Step 4 – Run the Backend

```bash
# Inside the backend/ folder with venv active:
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

✅ API is live! You can test it at: **http://127.0.0.1:8000/docs**

### Step 5 – Open the Frontend

Simply open `frontend/index.html` in your browser (double-click or use VS Code Live Server).

> **Tip**: Install the **Live Server** extension in VS Code, right-click `index.html` → *Open with Live Server*

---

## 🎯 Demo Flow

```
Login / Sign Up
     ↓
Dashboard (see stats)
     ↓
Add Medicine (fill form → Save)
     ↓
My Medicines (view, edit, delete)
     ↓
Today's Schedule (see reminders)
     ↓
Click "Taken" or "Skip"
     ↓
Dose History (see all records)
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/signup` | Register new user |
| POST | `/login` | Login user |
| POST | `/medicines` | Add medicine |
| GET | `/medicines` | Get all medicines |
| PUT | `/medicines/{id}` | Update medicine |
| DELETE | `/medicines/{id}` | Delete medicine |
| POST | `/reminders` | Create reminder |
| GET | `/reminders/today` | Get today's reminders |
| PUT | `/reminders/{id}/status` | Mark taken/skipped |
| GET | `/history` | Get dose history |
| GET | `/dashboard/stats` | Get dashboard summary |

---

## 🧠 OOP Concepts Used (for Viva)

| Concept | Where Used |
|---------|-----------|
| **Class** | `Medicine`, `User`, `Reminder`, `DoseHistory` in `models.py` |
| **Object** | Each medicine/user entry is an object |
| **Constructor (`__init__`)** | Sets up all attributes |
| **Methods** | `is_active_today()`, `mark_taken()`, `get_info()` |
| **Encapsulation** | Password is hashed; data hidden inside class |

---

## ⏰ Reminder Feature

- When you're on the **Dashboard** or **Schedule** page, the app checks every **60 seconds** if any reminder's time matches the current time
- If it matches and is still **pending**, a **popup notification** appears:
  > *"⏰ Time to take: Vitamin C"*
- No extra services needed — pure JavaScript `setInterval`!

---

## 🛠️ Tech Stack Summary

| Layer | Technology |
|-------|-----------|
| Frontend | HTML5 + CSS3 + Vanilla JS |
| Backend | Python 3.10+ + FastAPI |
| Database | Supabase (PostgreSQL) |
| ORM / DB Client | Supabase Python SDK |
| Server | Uvicorn (ASGI) |

---

## 📝 Notes for Viva

- **Why FastAPI?** — Fast, modern Python web framework with automatic API docs at `/docs`
- **Why Supabase?** — Free PostgreSQL cloud database, no server setup needed
- **Why no JWT?** — Kept simple; token is just the user ID stored in `localStorage`
- **Why no Docker?** — Not needed for a college prototype; just `python main.py`

---

## 🌐 Deploy to the Cloud (Render - Free)

1. Push your code to GitHub:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin <YOUR_GITHUB_REPO_URL>
   git push -u origin main
   ```
2. Log in to [Render.com](https://render.com) → Click **New +** → **Web Service**
3. Select your repository
4. Settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
5. Add Environment Variables:
   - `SUPABASE_URL` = your Supabase URL
   - `SUPABASE_KEY` = your Supabase Anon Key
6. Click **Deploy Web Service** — your app is live!
