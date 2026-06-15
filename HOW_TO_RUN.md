# 🚀 How to Run RegRadar - Complete Guide

## ✅ Prerequisites Check

Before starting, ensure you have:
- [x] Python 3.11+ installed
- [x] Node.js 18+ installed
- [x] `.env` file configured in root directory
- [x] Backend dependencies installed (`pip install -r requirements.txt`)
- [x] Frontend dependencies installed (`cd frontend && npm install`)
- [x] PostgreSQL database accessible (Railway)
- [x] All API keys configured in `.env`

---

## 🎯 Quick Start (Recommended)

### **Option 1: Use Startup Script**

```bash
# Double-click this file:
START_ALL.bat

# Or run from command line:
START_ALL.bat
```

This will:
1. Check for .env file
2. Start backend in one window
3. Start frontend in another window
4. Open browser automatically

---

## 🛠️ Manual Start (Step by Step)

### **Step 1: Start Backend**

Open **Terminal 1** (Command Prompt or PowerShell):

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Will watch for changes in these directories
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
[INFO] Starting RegRadar API...
[INFO] Environment: development
[INFO] Database initialized
INFO:     Application startup complete.
```

✅ **Backend is ready when you see:** `Application startup complete`

Test it: Open http://localhost:8000/health in browser

---

### **Step 2: Start Frontend**

Open **Terminal 2** (new window):

```bash
cd frontend
npm run dev
```

**Expected output:**
```
  VITE v5.1.0  ready in 500 ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

✅ **Frontend is ready when you see:** `ready in XXX ms`

---

### **Step 3: Open Application**

Open your browser and navigate to:
**http://localhost:3000**

You should see the RegRadar login page!

---

## 🧪 Testing the System

### **1. Check Backend is Running**

Open in browser: http://localhost:8000/health

Should return:
```json
{
  "status": "healthy",
  "environment": "development",
  "database": "connected",
  "timestamp": "..."
}
```

### **2. Check API Documentation**

Open: http://localhost:8000/docs

Should see interactive Swagger UI

### **3. Test Frontend**

Open: http://localhost:3000

Should see login page with:
- RegRadar logo
- Email and password fields
- Login button
- Register link

---

## 🎮 Using the Application

### **Step 1: Register Account**

1. Click "Register" link
2. Enter email: `test@example.com`
3. Enter password: `test12345` (minimum 8 chars)
4. Click "Register"
5. Should automatically log you in

### **Step 2: Search Circulars**

1. Go to "Search" tab (default)
2. Enter query: `capital adequacy requirements`
3. Click "Search"
4. See results with:
   - Circular titles
   - Relevance scores
   - Page numbers
   - Source (RBI/SEBI)

### **Step 3: Ask Questions (Chat)**

1. Click "Chat" tab
2. Enter question: `What are the new regulations for small finance banks?`
3. Click "Ask"
4. Wait 2-3 seconds for AI response
5. See:
   - Detailed answer from Claude
   - Source citations with page numbers

### **Step 4: Browse Circulars**

1. Click "Circulars" tab
2. See list of all indexed circulars
3. Filter by source (RBI/SEBI)
4. View dates and titles

---

## 🐛 Troubleshooting

### **Backend won't start**

**Error: "DATABASE_URL not found"**
```bash
# Solution: Check .env file exists in root directory
# Copy from .env.example if needed
cp .env.example .env
# Edit .env with your credentials
```

**Error: "ModuleNotFoundError"**
```bash
# Solution: Install backend dependencies
cd backend
pip install -r requirements.txt
```

**Error: "Port 8000 already in use"**
```bash
# Solution: Find and kill the process
netstat -ano | findstr :8000
# Or use different port
python -m uvicorn app.main:app --port 8001
```

---

### **Frontend won't start**

**Error: "Cannot find module"**
```bash
# Solution: Install dependencies
cd frontend
npm install
```

**Error: "Port 3000 already in use"**
```bash
# Solution: Kill existing process or use different port
# Edit vite.config.js and change port to 3001
```

**Error: "Failed to fetch"**
```bash
# Solution: Check backend is running
# Verify VITE_API_URL in .env points to http://localhost:8000
```

---

### **Login/Register fails**

**Error: "Network Error"**
- Check backend is running: http://localhost:8000/health
- Check CORS settings in backend/app/main.py
- Verify API URL in frontend

**Error: "Email already registered"**
- Use different email or login with existing credentials

---

### **Search/Chat returns no results**

**Cause: No circulars indexed**

Solution: Run the pipeline to add data
```bash
# In Terminal 3
python run_pipeline_prod.py 10
```

This will:
- Scrape 10 circulars from RBI/SEBI
- Process and index them
- Make them searchable

---

## 📊 System Status Check

Run this to verify everything is working:

```bash
# Test backend health
curl http://localhost:8000/health

# Test database connection
python -c "from pipeline.db import get_all_circulars; print(f'{len(get_all_circulars())} circulars in database')"

# Test Pinecone vectors
python -c "from pipeline.chunker import VectorStore; vs = VectorStore(); stats = vs.index.describe_index_stats(); print(f'{stats.total_vector_count} vectors indexed')"

# Test frontend (should open in browser)
start http://localhost:3000
```

---

## 🔧 Advanced Options

### **Run with Custom Port**

Backend:
```bash
python -m uvicorn app.main:app --port 8080
```

Frontend:
```bash
# Edit vite.config.js first, then:
npm run dev
```

### **Run in Production Mode**

Backend:
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Frontend:
```bash
npm run build
npm run preview
```

### **Add More Data**

```bash
# Add 50 circulars
python run_pipeline_prod.py 50

# Takes about 15-20 minutes
# Cost: ~$0.70
```

---

## 📝 Stopping the System

### **Method 1: Close Windows**
- Close backend terminal window
- Close frontend terminal window

### **Method 2: CTRL+C**
- In backend terminal: Press CTRL+C
- In frontend terminal: Press CTRL+C

### **Method 3: Kill Processes**
```bash
# Find processes
netstat -ano | findstr :8000
netstat -ano | findstr :3000

# Kill by PID
taskkill /PID <pid> /F
```

---

## ✅ Success Checklist

Your system is working correctly if:

- [ ] Backend starts without errors
- [ ] http://localhost:8000/health returns healthy
- [ ] http://localhost:8000/docs shows API documentation
- [ ] Frontend starts without errors
- [ ] http://localhost:3000 shows login page
- [ ] Can register a new user
- [ ] Can login with credentials
- [ ] Can see dashboard with 3 tabs
- [ ] Search returns results (if circulars indexed)
- [ ] Chat returns AI answers (if circulars indexed)
- [ ] Circulars tab shows list

---

## 🎉 You're All Set!

Your complete RegRadar system is now running:

- ✅ Backend API serving requests
- ✅ Frontend UI responsive
- ✅ Database connected
- ✅ AI services active
- ✅ Vector search working

**Enjoy your AI-powered regulatory intelligence platform!**

---

## 💡 Pro Tips

1. **Keep both terminals open** - closing them stops the servers
2. **Use different browsers** for testing multiple users
3. **Check console logs** if something doesn't work
4. **Run pipeline first** to have data to search
5. **Use API docs** at /docs to test endpoints directly

---

## 📞 Need Help?

- Check backend logs in Terminal 1
- Check frontend console (F12 in browser)
- Verify .env file has all required keys
- Ensure all dependencies are installed
- Try restarting both servers

**If stuck, run:** `python test_components.py` to verify all services
