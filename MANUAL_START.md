# 🚀 RegRadar - Manual Start Instructions

## ⚡ Easiest Way to Start

### **Method 1: Python Script (Recommended)**

```bash
python run_system.py
```

This automatically:
- Starts backend in new window
- Starts frontend in new window  
- Opens browser to http://localhost:3000

---

### **Method 2: Manual (If script doesn't work)**

Follow these exact steps:

#### **Step 1: Open First Terminal**

```bash
cd "C:\Users\mohit.dj.kumar\Desktop\Set up with Gen AI\Project 2\ComplianceIQ\backend"
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Wait for this message:**
```
INFO: Application startup complete
```

✅ Backend is now running! Keep this window open.

---

#### **Step 2: Open Second Terminal**

```bash
cd "C:\Users\mohit.dj.kumar\Desktop\Set up with Gen AI\Project 2\ComplianceIQ\frontend"
npm run dev
```

**Wait for this message:**
```
VITE ready in XXXms
Local: http://localhost:3000
```

✅ Frontend is now running! Keep this window open.

---

#### **Step 3: Open Browser**

Navigate to: **http://localhost:3000**

You should see the RegRadar login page!

---

## 🐛 If It Still Doesn't Work

### **Issue 1: Backend won't start**

**Check Python path:**
```bash
python --version
# Should show Python 3.11 or higher
```

**Check if dependencies installed:**
```bash
cd backend
pip list | findstr fastapi
# Should show fastapi
```

**Reinstall if needed:**
```bash
cd backend
pip install -r requirements.txt
```

---

### **Issue 2: Frontend won't start**

**Check Node.js:**
```bash
node --version
# Should show v18 or higher

npm --version
# Should show 9 or higher
```

**Check if dependencies installed:**
```bash
cd frontend
dir node_modules | findstr react
# Should show react folder
```

**Reinstall if needed:**
```bash
cd frontend
npm install
```

---

### **Issue 3: Port already in use**

**Find what's using the port:**
```bash
netstat -ano | findstr :8000
netstat -ano | findstr :3000
```

**Kill the process:**
```bash
# Replace <PID> with the number from above
taskkill /PID <PID> /F
```

---

### **Issue 4: Browser shows "Can't reach"**

**Check if servers are actually running:**

Backend test:
```bash
curl http://localhost:8000/health
# Should return JSON with "healthy"
```

Frontend test:
```bash
curl http://localhost:3000
# Should return HTML
```

If curl not available, open URLs in browser directly.

---

## 📝 Step-by-Step Verification

Run these commands one by one:

```bash
# 1. Check you're in the right directory
cd "C:\Users\mohit.dj.kumar\Desktop\Set up with Gen AI\Project 2\ComplianceIQ"
dir
# Should show: backend, frontend, pipeline folders

# 2. Check .env exists
dir .env
# Should show the file

# 3. Check backend dependencies
cd backend
pip show fastapi
# Should show package info

# 4. Check frontend dependencies  
cd ..\frontend
dir node_modules
# Should show many folders

# 5. Try starting backend
cd ..\backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
# Press CTRL+C after you see "Application startup complete"

# 6. Try starting frontend (in new terminal)
cd ..\frontend
npm run dev
# Press CTRL+C after you see "ready in XXXms"
```

---

## ✅ Success Indicators

### **Backend Started Successfully:**
```
INFO: Uvicorn running on http://127.0.0.1:8000
INFO: Application startup complete
[INFO] Starting RegRadar API...
[INFO] Environment: development
[INFO] Database initialized
```

### **Frontend Started Successfully:**
```
VITE v5.1.0  ready in 500ms

➜  Local:   http://localhost:3000/
➜  Network: use --host to expose
```

### **Browser Working:**
- http://localhost:3000 shows login page
- http://localhost:8000/docs shows API documentation
- http://localhost:8000/health returns {"status":"healthy"}

---

## 🎯 Alternative Ports

If ports 8000 or 3000 are taken:

**Backend on different port:**
```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8080
```

**Frontend on different port:**
```bash
# Edit frontend/vite.config.js first
# Change: port: 3000 to port: 3001
cd frontend
npm run dev
```

**Update frontend to use new backend port:**
```bash
# Create frontend/.env
echo VITE_API_URL=http://localhost:8080 > frontend/.env
```

---

## 💡 Pro Tips

1. **Always start backend FIRST**, wait for it to fully start, then start frontend
2. **Keep both terminal windows open** - closing them stops the servers
3. **Check Windows Firewall** - it might block the ports
4. **Use 127.0.0.1** instead of localhost if localhost doesn't work
5. **Try incognito mode** in browser to avoid cache issues

---

## 🆘 Still Not Working?

Try this minimal test:

```bash
# Test if backend can start at all
cd backend
python -c "from app.main import app; print('Backend imports OK!')"

# Test if frontend can build
cd ..\frontend
npm run build
# Should create dist/ folder
```

If these work, the issue is likely with ports or firewall.

---

## 📞 Final Checklist

Before asking for help, verify:

- [ ] Python 3.11+ installed (`python --version`)
- [ ] Node.js 18+ installed (`node --version`)
- [ ] .env file exists in root directory
- [ ] Backend dependencies installed (`cd backend && pip list`)
- [ ] Frontend dependencies installed (`cd frontend && dir node_modules`)
- [ ] No other services using ports 8000 or 3000
- [ ] Windows Firewall allows Python and Node
- [ ] Both terminals stay open (don't close them)
- [ ] Waited 5-10 seconds after starting each server

---

## 🎉 Once It Works

You'll see:
1. Backend terminal showing API logs
2. Frontend terminal showing Vite output
3. Browser at http://localhost:3000 with login page
4. You can register and use the system!

**Test it:**
- Register: test@example.com / test12345
- Search: "capital adequacy"
- See results!

---

## 🔧 Emergency Reset

If everything is broken:

```bash
# 1. Stop all processes
taskkill /F /IM python.exe
taskkill /F /IM node.exe

# 2. Clean install
cd backend
pip install -r requirements.txt --force-reinstall

cd ..\frontend
rmdir /s /q node_modules
npm install

# 3. Try again
python ..\run_system.py
```

---

**Good luck! The system is complete and ready - just needs to start!** 🚀
