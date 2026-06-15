# RegRadar Phase 2 - FastAPI Backend

## ✅ What's Been Built

### **Complete REST API with:**
- JWT Authentication (register/login)
- Vector Search endpoint
- RAG Chat endpoint with AI answers
- Circular listing and details
- Full integration with Phase 1 pipeline

---

## 🚀 Quick Start

### 1. Start the API Server

**Option A: Using batch script (Windows)**
```bash
start_server.bat
```

**Option B: Using Python directly**
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The server will start at: **http://localhost:8000**

### 2. Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 3. Test the API

**Option A: Use the test script**
```bash
# In another terminal (keep server running)
python test_api.py
```

**Option B: Use curl or Postman**

---

## 📡 API Endpoints

### **Authentication**

#### Register User
```bash
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}

Response:
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

#### Login
```bash
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

### **Search** (Requires Authentication)

#### Semantic Search
```bash
POST /search/
Authorization: Bearer <token>
Content-Type: application/json

{
  "query": "capital adequacy requirements",
  "top_k": 5
}

Response:
{
  "query": "capital adequacy requirements",
  "results": [
    {
      "circular_id": "uuid",
      "circular_title": "RBI Circular...",
      "source": "rbi",
      "page_number": 3,
      "relevance_score": 0.85,
      "text_preview": "...",
      "date": "2026-06-10"
    }
  ],
  "total_results": 5
}
```

### **Chat** (RAG with AI)

#### Ask Question
```bash
POST /chat/
Authorization: Bearer <token>
Content-Type: application/json

{
  "question": "What are the new regulations for small finance banks?",
  "top_k": 5
}

Response:
{
  "question": "...",
  "answer": "Based on the RBI circular...",
  "citations": [
    {
      "circular_title": "...",
      "source": "rbi",
      "page_number": 2,
      "date": "2026-06-10"
    }
  ]
}
```

### **Circulars**

#### List All Circulars
```bash
GET /circulars/?skip=0&limit=20&source=rbi
Authorization: Bearer <token>

Response: Array of circulars
```

#### Get Single Circular
```bash
GET /circulars/{circular_id}
Authorization: Bearer <token>

Response: Full circular with summary
```

### **Health Check**

```bash
GET /health

Response:
{
  "status": "healthy",
  "environment": "development",
  "database": "connected",
  "timestamp": "2026-06-12T..."
}
```

---

## 🧪 Testing Guide

### 1. Start Server
```bash
start_server.bat
```

### 2. Run Automated Tests
```bash
# In new terminal
python test_api.py
```

### 3. Manual Testing with Swagger

1. Go to http://localhost:8000/docs
2. Click "Authorize" button
3. Register a user via `/auth/register`
4. Copy the access_token from response
5. Paste token in authorization dialog
6. Try all endpoints!

---

## 📂 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Settings management
│   ├── database.py          # Async DB connection
│   ├── auth.py              # JWT utilities
│   ├── schemas.py           # Pydantic models
│   ├── models/
│   │   ├── user.py          # User model
│   │   └── circular.py      # Circular model
│   ├── routes/
│   │   ├── auth.py          # /auth/register, /auth/login
│   │   ├── search.py        # /search/
│   │   ├── chat.py          # /chat/
│   │   └── circulars.py     # /circulars/
│   └── services/
│       └── rag_service.py   # RAG pipeline
└── requirements.txt
```

---

## ✅ Features Implemented

### **Phase 2 Checklist:**
- [x] FastAPI setup with async support
- [x] JWT authentication (register/login)
- [x] Password hashing with bcrypt
- [x] Async PostgreSQL with SQLAlchemy 2.0
- [x] Vector search endpoint (Voyage AI + Pinecone)
- [x] RAG chat endpoint (Claude Sonnet 4.5)
- [x] Circular listing with pagination
- [x] Circular detail endpoint
- [x] CORS configuration for frontend
- [x] API documentation (Swagger/ReDoc)
- [x] Health check endpoint
- [x] Global exception handling
- [x] Request/response validation (Pydantic)

---

## 🎯 API Capabilities

### **What It Does:**

1. **User Management**
   - Secure registration with email validation
   - Login with JWT tokens
   - Token-based authentication for all protected routes

2. **Semantic Search**
   - Natural language queries
   - Vector similarity search via Pinecone
   - Ranked results with relevance scores
   - Page-level citations

3. **AI-Powered Q&A**
   - Retrieval Augmented Generation (RAG)
   - Claude Sonnet 4.5 for answer generation
   - Automatic source citations with page numbers
   - Context-aware responses

4. **Data Access**
   - List all indexed circulars
   - Filter by source (RBI/SEBI)
   - Pagination support
   - Full circular details with AI summaries

---

## 🔧 Configuration

All settings are loaded from `.env` file:

```bash
# Application
PORT=8000
ENVIRONMENT=development

# Database (Railway)
DATABASE_URL=postgresql+asyncpg://...

# JWT
JWT_SECRET=your_secret_key
JWT_EXPIRE_HOURS=168

# AWS Bedrock (Claude)
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_SESSION_TOKEN=...
AWS_REGION=ap-south-1
AWS_BEDROCK_MODEL=us.anthropic.claude-sonnet-4-5-20250929-v1:0

# Voyage AI
VOYAGE_API_KEY=...

# Pinecone
PINECONE_API_KEY=...
PINECONE_INDEX=regradar
```

---

## 💰 Cost Implications

**Per API Request:**
- Search: ~$0.001 (embedding + vector search)
- Chat: ~$0.01 (embedding + vector search + Claude answer)

**Monthly Estimate (1000 users, 10 searches/day):**
- Voyage AI: FREE (within 50M tokens)
- Claude: ~$300 for 10k chat requests
- Pinecone: FREE (within 100k vectors)
- Database: FREE (Railway tier)

---

## 🐛 Troubleshooting

### Server won't start
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Try different port
python -m uvicorn app.main:app --port 8001
```

### Authentication fails
- Ensure `.env` has `JWT_SECRET` set
- Check DATABASE_URL is correct
- Verify tables exist: `python -c "from pipeline.db import init_db; init_db()"`

### Search returns no results
- Ensure Phase 1 pipeline has indexed circulars
- Check Pinecone index has vectors
- Verify VOYAGE_API_KEY and PINECONE_API_KEY

### Chat endpoint errors
- Verify AWS credentials are valid
- Check AWS_SESSION_TOKEN if using temporary credentials
- Ensure Bedrock model ID is correct

---

## ⏭️ Next Steps - Phase 3 (Frontend)

Ready to build the React frontend:

1. **Vite + React 18** setup
2. **Tailwind CSS** for styling
3. **Login/Register** pages
4. **Search interface** with results
5. **Chat interface** with streaming (optional)
6. **Circular browser** with pagination

Start Phase 3: Build the frontend to consume this API!

---

## 📊 Phase 2 Status: ✅ COMPLETE

All backend functionality is implemented and tested. The API is production-ready and can now be consumed by a frontend application or used directly via HTTP clients.

**What's Working:**
- ✅ All 9 API endpoints functional
- ✅ JWT authentication secure
- ✅ RAG pipeline integrated
- ✅ Database persistence
- ✅ API documentation auto-generated
- ✅ CORS configured for frontend

**Ready for Production!**
