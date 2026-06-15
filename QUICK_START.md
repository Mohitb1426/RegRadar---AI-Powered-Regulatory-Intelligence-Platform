# ⚡ RegRadar - Quick Start Guide

## 🚀 Start Everything (Easy Mode)

```bash
# Double-click this file:
START_ALL.bat
```

**OR manually in 2 terminals:**

### Terminal 1 - Backend:
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

### Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
```

---

## 🌐 Access Points

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 🎯 First Time Setup

```bash
# 1. Install dependencies (one time only)
pip install -r requirements.txt
cd frontend && npm install && cd ..

# 2. Add some data
python run_pipeline_prod.py 10

# 3. Start servers (see above)

# 4. Open browser to http://localhost:3000
```

---

## 🧪 Quick Test

1. **Register**: test@example.com / test12345
2. **Search**: "capital adequacy"
3. **Chat**: "What are the new regulations?"
4. **Browse**: Click "Circulars" tab

---

## 🛠️ Troubleshooting One-Liners

```bash
# Check backend is running
curl http://localhost:8000/health

# Check how many circulars indexed
python -c "from pipeline.db import get_all_circulars; print(len(get_all_circulars()))"

# Add more data
python run_pipeline_prod.py 10

# Test all components
python test_components.py

# Test API
python test_api.py
```

---

## 📁 Project Structure

```
ComplianceIQ/
├── backend/          # FastAPI backend
├── frontend/         # React frontend
├── pipeline/         # Data processing
├── START_ALL.bat     # Start everything
├── .env              # Configuration (create from .env.example)
└── HOW_TO_RUN.md     # Detailed guide
```

---

## 💡 Common Commands

```bash
# Start backend only
cd backend && python -m uvicorn app.main:app --reload

# Start frontend only
cd frontend && npm run dev

# Run pipeline (add data)
python run_pipeline_prod.py 10

# Test search (CLI)
python -c "from pipeline.test_query import answer_question; answer_question('test')"

# Check database
python pipeline/db.py
```

---

## ✅ Success Indicators

Backend ready:
```
INFO: Application startup complete
```

Frontend ready:
```
VITE ready in XXXms
Local: http://localhost:3000
```

System working:
- Can register/login
- Search returns results
- Chat gives AI answers
- Circulars list shows data

---

## 🎉 That's It!

You now have a complete AI regulatory intelligence platform running locally.

**Next Steps:**
1. Add more circulars (run pipeline with 50+)
2. Test all features
3. Deploy to production (Railway + Vercel)

**Full documentation:** See `HOW_TO_RUN.md` and `PROJECT_COMPLETE.md`
