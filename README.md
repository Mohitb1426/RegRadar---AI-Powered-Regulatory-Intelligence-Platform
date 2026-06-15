# RegRadar - AI-Powered Regulatory Intelligence Platform

**Never miss a regulation again**

RegRadar automatically monitors, processes, and makes searchable all RBI and SEBI circulars using AI. Ask questions in plain English and get answers with exact source citations including page numbers.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18.2-blue.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)

---

## 🚀 Features

- **Automated Scraping**: Daily monitoring of RBI & SEBI websites for new circulars
- **Smart Processing**: PDF parsing, text extraction with page-level tracking
- **AI Summaries**: Claude Sonnet 4.5 generates 300-500 word summaries
- **Semantic Search**: Natural language search using Voyage AI embeddings + Pinecone
- **RAG Q&A**: Ask questions and get AI answers with exact citations (circular name, date, page)
- **Modern UI**: React 18 dashboard with search, chat, and circular browsing
- **REST API**: FastAPI backend with JWT authentication
- **Real-time Streaming**: Server-sent events for responsive AI chat

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     USER BROWSER                             │
│                  (React + Vite Frontend)                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ REST API (JWT Auth)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  FASTAPI BACKEND                             │
│  - /auth/register, /auth/login                              │
│  - /search (vector search)                                  │
│  - /chat (RAG with citations)                               │
│  - /circulars (CRUD)                                        │
└────────────┬────────────┬──────────────┬────────────────────┘
             │            │              │
             ▼            ▼              ▼
    ┌────────────┐  ┌──────────┐  ┌──────────────┐
    │ PostgreSQL │  │ Pinecone │  │ AWS Bedrock  │
    │  (Railway) │  │ (Vectors)│  │ (Claude 4.5) │
    └────────────┘  └──────────┘  └──────────────┘
             ▲            ▲              ▲
             │            │              │
    ┌────────┴────────────┴──────────────┴────────┐
    │         DATA PIPELINE (Offline)              │
    │  Scraper → Download → Parse → Summarize →   │
    │  Chunk → Embed → Index                       │
    └──────────────────────────────────────────────┘
```

### Data Flow

1. **Scraping**: BeautifulSoup extracts circular links from RBI/SEBI websites
2. **Download**: PDFs saved locally with validation (ensures actual PDF, not HTML)
3. **Parse**: PyMuPDF extracts text page-by-page with character count
4. **Summarize**: Claude Sonnet 4.5 via AWS Bedrock generates 300-500 word summaries
5. **Chunk**: LangChain splits text into 800-char chunks with 100-char overlap
6. **Embed**: Voyage AI voyage-2 creates 1024-dimensional vectors
7. **Index**: Pinecone stores vectors with metadata (title, source, page, date)
8. **Store**: PostgreSQL saves circular metadata and summaries

### RAG Pipeline (User Query)

1. **User asks**: "What are capital adequacy requirements?"
2. **Embed query**: Voyage AI converts question to vector
3. **Search Pinecone**: Find top 10 most similar chunks
4. **Retrieve context**: Get relevant text with page numbers
5. **Generate answer**: Claude Sonnet 4.5 answers using context only
6. **Extract citations**: Parse circular titles, dates, page numbers
7. **Return**: AI answer + citations to frontend

---

## 📁 Project Structure

```
ComplianceIQ/
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── main.py          # FastAPI app entry point
│   │   ├── config.py        # Environment settings (Pydantic)
│   │   ├── database.py      # SQLAlchemy async engine
│   │   ├── auth.py          # JWT + bcrypt utilities
│   │   ├── schemas.py       # Pydantic request/response models
│   │   ├── models/
│   │   │   ├── user.py      # User table (email, password_hash)
│   │   │   └── circular.py  # Circular table (title, date, source, summary)
│   │   ├── routes/
│   │   │   ├── auth.py      # POST /auth/register, /auth/login
│   │   │   ├── search.py    # POST /search (vector search)
│   │   │   ├── chat.py      # POST /chat (RAG Q&A)
│   │   │   └── circulars.py # GET /circulars, GET /circulars/{id}
│   │   └── services/
│   │       └── rag_service.py  # Core RAG logic (embed → search → generate)
│   └── requirements.txt     # Python dependencies
│
├── frontend/                # React frontend
│   ├── src/
│   │   ├── App.jsx         # Main app (auth, search, chat, circulars)
│   │   ├── main.jsx        # React entry point
│   │   ├── index.css       # Tailwind imports
│   │   └── services/
│   │       └── api.js      # Axios client with JWT interceptor
│   ├── package.json        # npm dependencies
│   ├── vite.config.js      # Vite dev server config
│   └── tailwind.config.js  # Tailwind CSS config
│
├── pipeline/               # Data processing pipeline
│   ├── scraper_improved.py     # Web scraping (RBI + SEBI)
│   ├── downloader_robust.py   # PDF download with validation
│   ├── parser.py               # PyMuPDF text extraction
│   ├── summarizer.py           # AWS Bedrock Claude integration
│   ├── chunker.py              # Text chunking + embedding + indexing
│   ├── db.py                   # Database operations
│   └── __init__.py
│
├── run_pipeline_prod.py    # Master pipeline orchestration
├── run_system.py           # Start backend + frontend together
├── START_ALL.bat           # Windows batch script to start servers
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules (excludes .env)
├── requirements.txt        # Root Python dependencies
└── README.md               # This file
```

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Frontend** | React 18.2 | UI framework |
| | Vite 5.1 | Build tool (fast HMR) |
| | Tailwind CSS 3.4 | Styling |
| | Axios 1.6 | HTTP client |
| | React Router 6.22 | Navigation |
| **Backend** | FastAPI | REST API framework |
| | SQLAlchemy 2.0 | ORM (async) |
| | asyncpg | PostgreSQL driver |
| | python-jose | JWT handling |
| | bcrypt 5.0 | Password hashing |
| | Uvicorn | ASGI server |
| **AI/ML** | Claude Sonnet 4.5 | Summarization + Q&A |
| | Voyage AI voyage-2 | Text embeddings (1024-dim) |
| | LangChain | Text chunking |
| **Data** | PostgreSQL | Relational database |
| | Pinecone | Vector database |
| **Pipeline** | PyMuPDF (fitz) | PDF parsing |
| | BeautifulSoup4 | Web scraping |
| | boto3 | AWS SDK |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL database (Railway recommended)
- API Keys:
  - AWS Bedrock (Claude access)
  - Voyage AI (embeddings)
  - Pinecone (vector database)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Mohitb1426/RegRadar---AI-Powered-Regulatory-Intelligence-Platform.git
cd RegRadar---AI-Powered-Regulatory-Intelligence-Platform
```

2. **Set up environment variables**
```bash
# Copy example and fill in your API keys
cp .env.example .env
# Edit .env with your actual credentials
```

3. **Install backend dependencies**
```bash
pip install -r requirements.txt
cd backend
pip install -r requirements.txt
```

4. **Install frontend dependencies**
```bash
cd frontend
npm install
```

5. **Initialize database**
```bash
# Backend startup automatically creates tables
# Or run manually:
cd backend
python -c "from app.database import init_db; import asyncio; asyncio.run(init_db())"
```

6. **Run the pipeline (optional - to index circulars)**
```bash
# Index 10 circulars
python run_pipeline_prod.py 10
```

7. **Start the application**

**Option A: Automatic (Windows)**
```bash
# Double-click START_ALL.bat or run:
START_ALL.bat
```

**Option B: Python script**
```bash
python run_system.py
```

**Option C: Manual (2 terminals)**
```bash
# Terminal 1 - Backend
cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

8. **Open your browser**
```
Frontend: http://localhost:3000
Backend API: http://localhost:8000
API Docs: http://localhost:8000/docs
```

---

## 🔐 Environment Variables

Create a `.env` file in the project root with the following:

```bash
# AWS Bedrock (Claude API)
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_SESSION_TOKEN=your_session_token_if_using_temporary_credentials
AWS_REGION=ap-south-1
AWS_BEDROCK_MODEL=us.anthropic.claude-sonnet-4-5-20250929-v1:0

# AWS S3 (PDF storage - optional)
AWS_BUCKET_NAME=regradar-pdfs

# Voyage AI (embeddings)
VOYAGE_API_KEY=your_voyage_api_key

# Pinecone (vector database)
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX=regradar

# PostgreSQL
DATABASE_URL=postgresql+asyncpg://postgres:password@host:port/database

# JWT Authentication
JWT_SECRET=generate_a_strong_random_secret_key_at_least_32_characters
JWT_EXPIRE_HOURS=168

# Application
PORT=8000
ENVIRONMENT=development
```

---

## 📖 API Documentation

### Authentication

**Register**
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}

Response: {"access_token": "eyJ0eXAi..."}
```

**Login**
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}

Response: {"access_token": "eyJ0eXAi..."}
```

### Search

**Semantic Search**
```http
POST /search
Authorization: Bearer <token>
Content-Type: application/json

{
  "query": "capital adequacy requirements",
  "top_k": 5
}

Response: {
  "results": [
    {
      "circular_title": "Master Direction - Capital Adequacy",
      "source": "RBI",
      "date": "2024-03-15",
      "page_number": 5,
      "score": 0.87,
      "summary": "..."
    }
  ]
}
```

### Chat (RAG Q&A)

**Ask Question**
```http
POST /chat
Authorization: Bearer <token>
Content-Type: application/json

{
  "question": "What are the new KYC rules?"
}

Response: {
  "answer": "Based on RBI circulars, the new KYC rules require...",
  "citations": [
    {
      "circular_title": "Master Direction - KYC Norms",
      "source": "RBI",
      "page_number": 5,
      "date": "2024-03-15"
    }
  ]
}
```

### Circulars

**List All**
```http
GET /circulars?skip=0&limit=20&source=RBI
Authorization: Bearer <token>

Response: {
  "circulars": [...],
  "total": 45
}
```

**Get Single Circular**
```http
GET /circulars/{id}
Authorization: Bearer <token>

Response: {
  "id": "uuid",
  "title": "...",
  "date": "2024-03-15",
  "source": "RBI",
  "summary": "...",
  "indexed": true
}
```

Full interactive API docs: `http://localhost:8000/docs`

---

## 🧪 Testing

### Test Individual Components

```bash
# Test environment setup
python test_setup.py

# Test API endpoints
python test_api.py

# Test all components
python test_components.py
```

### Test the Application

1. **Register a user**
   - Navigate to http://localhost:3000
   - Click "Register"
   - Enter email and password (min 8 chars)

2. **Search for circulars**
   - Go to "Search" tab
   - Enter: "capital adequacy requirements"
   - View results with page numbers

3. **Ask questions**
   - Go to "Chat" tab
   - Ask: "What are the new KYC rules for banks?"
   - See AI answer with citations

4. **Browse circulars**
   - Go to "Circulars" tab
   - Filter by RBI/SEBI
   - View summaries

---

## 🎯 Usage Examples

### Running the Pipeline

```bash
# Index 10 new circulars
python run_pipeline_prod.py 10

# Output:
# [INFO] Phase 1/6: Initializing database...
# [OK] Database initialized
# [INFO] Phase 2/6: Scraping circulars...
# [OK] Found 8 new RBI circulars
# [INFO] Phase 3/6: Downloading PDFs...
# [OK] Downloaded 10/10 PDFs
# [INFO] Phase 4/6: Parsing text...
# [OK] Parsed 10 circulars
# [INFO] Phase 5/6: Generating summaries...
# [OK] Summarized 10 circulars
# [INFO] Phase 6/6: Indexing vectors...
# [OK] Indexed 210 vectors
```

### Using the API

```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/auth/login",
    json={"email": "user@example.com", "password": "password123"}
)
token = response.json()["access_token"]

# Search
response = requests.post(
    "http://localhost:8000/search",
    headers={"Authorization": f"Bearer {token}"},
    json={"query": "KYC requirements", "top_k": 5}
)
results = response.json()["results"]

# Ask question
response = requests.post(
    "http://localhost:8000/chat",
    headers={"Authorization": f"Bearer {token}"},
    json={"question": "What are capital requirements for banks?"}
)
answer = response.json()["answer"]
citations = response.json()["citations"]
```

---

## 💰 Cost Estimates

| Service | Usage | Cost |
|---------|-------|------|
| **Voyage AI** | Embeddings | FREE (50M tokens/month) |
| **Pinecone** | Vector storage | FREE (100k vectors) |
| **PostgreSQL** | Database | FREE (Railway free tier) |
| **Claude Sonnet 4.5** | Summarization + Q&A | ~$0.003/1k input, $0.015/1k output |

**Example costs:**
- 1 circular summary: ~$0.01
- 1 user question: ~$0.02
- 100 circulars indexed: ~$1.00
- 1000 user queries: ~$20.00

---

## 🐛 Troubleshooting

### Backend won't start

```bash
# Check Python version
python --version  # Should be 3.11+

# Reinstall dependencies
cd backend
pip install -r requirements.txt --force-reinstall

# Check .env file exists
ls ../.env

# Test imports
python -c "from app.main import app; print('OK')"
```

### Frontend won't start

```bash
# Check Node.js version
node --version  # Should be 18+

# Reinstall dependencies
cd frontend
rm -rf node_modules
npm install

# Check for port conflicts
netstat -ano | findstr :3000
```

### Database connection error

- Verify DATABASE_URL in .env
- Check if PostgreSQL is accessible
- For Railway: Use external connection URL, not internal
- Add `?ssl=False` if SSL issues: `postgresql+asyncpg://...?ssl=False`

### API keys not working

- Check .env file is in project root (not in backend/)
- Ensure no quotes around values in .env
- Verify keys are not expired (especially AWS session tokens)
- Test each service individually with test_setup.py

### Search returns no results

- Run pipeline first: `python run_pipeline_prod.py 10`
- Check Pinecone has vectors: Login to Pinecone dashboard
- Verify Voyage AI key is valid
- Check backend logs for errors

---

## 🚢 Deployment

### Deploy Backend (Railway)

1. Create Railway project
2. Add PostgreSQL service
3. Deploy backend:
   ```bash
   railway link
   railway up
   ```
4. Set environment variables in Railway dashboard
5. Note the public URL

### Deploy Frontend (Vercel)

1. Build frontend:
   ```bash
   cd frontend
   npm run build
   ```
2. Deploy to Vercel:
   ```bash
   vercel --prod
   ```
3. Set environment variable:
   ```
   VITE_API_URL=https://your-railway-backend.up.railway.app
   ```

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **Claude Sonnet 4.5** by Anthropic for AI capabilities
- **Voyage AI** for semantic embeddings
- **Pinecone** for vector database
- **FastAPI** for modern Python web framework
- **React** and **Vite** for frontend
- **Railway** for PostgreSQL hosting

---

## 📧 Contact

**Mohit Kumar**  
GitHub: [@Mohitb1426](https://github.com/Mohitb1426)  
Repository: [RegRadar](https://github.com/Mohitb1426/RegRadar---AI-Powered-Regulatory-Intelligence-Platform)

---

## 🔗 Links

- **Live Demo**: Coming soon
- **API Documentation**: `http://localhost:8000/docs` (when running locally)
- **GitHub Issues**: [Report bugs](https://github.com/Mohitb1426/RegRadar---AI-Powered-Regulatory-Intelligence-Platform/issues)

---

**Built with ❤️ for better regulatory compliance**
