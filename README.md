# RegRadar - AI-Powered Regulatory Intelligence Platform

**Never miss a regulation again**

RegRadar automatically monitors, processes, and makes searchable all RBI and SEBI circulars using AI. Ask questions in plain English and get answers with exact source citations including page numbers.

---

## 🚀 What It Does

- **Automated Scraping**: Daily monitoring of RBI & SEBI websites for new circulars
- **Smart Processing**: PDF parsing, text extraction with page tracking
- **AI Summaries**: Claude Sonnet 4 generates concise summaries of each circular
- **Semantic Search**: Voyage AI embeddings + Pinecone vector database
- **Natural Language Queries**: Ask questions like "new KYC rules for banks" and get cited answers
- **Real-time Streaming**: Server-sent events for responsive AI answers

---

## 🏗️ Architecture

```
RBI/SEBI Websites
        ↓
Web Scraper (BeautifulSoup)
        ↓
PDF Download → AWS S3
        ↓
Text Extraction (PyMuPDF with page numbers)
        ↓
Text Chunking (LangChain)
        ↓
Embeddings (Voyage AI voyage-2)
        ↓
Vector Index (Pinecone)
        ↓
Summaries (Claude Sonnet 4 via AWS Bedrock)
        ↓
Metadata Storage (PostgreSQL)
```

---

## 📦 Tech Stack

### Data Pipeline
- **Web Scraping**: BeautifulSoup4 + requests
- **PDF Processing**: PyMuPDF (fitz)
- **Text Chunking**: LangChain RecursiveCharacterTextSplitter
- **Embeddings**: Voyage AI (voyage-2)
- **Vector Database**: Pinecone
- **AI Summarization**: Claude Sonnet 4 via AWS Bedrock
- **Database**: PostgreSQL + SQLAlchemy
- **Storage**: AWS S3
- **Scheduling**: APScheduler

### Backend (Phase 2)
- FastAPI
- JWT Authentication
- SSE Streaming

### Frontend (Phase 3)
- React 18 + Vite
- Tailwind CSS

---

## ⚙️ Setup Instructions

### Prerequisites
- Python 3.11+
- PostgreSQL database
- AWS account (for Bedrock & S3)
- Voyage AI API key (free tier)
- Pinecone account (free tier)

### 1. Clone & Install Dependencies

```bash
cd ComplianceIQ
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Required variables:
```bash
# AWS Bedrock (Claude API)
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=ap-south-1
AWS_BEDROCK_MODEL=anthropic.claude-sonnet-4-20250514-v1:0

# AWS S3
AWS_BUCKET_NAME=regradar-pdfs

# Voyage AI (free tier: 50M tokens/month)
VOYAGE_API_KEY=pa-your_key

# Pinecone (free tier)
PINECONE_API_KEY=your_key
PINECONE_INDEX=regradar

# PostgreSQL
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/regradar

# JWT (for backend - Phase 2)
JWT_SECRET=your_random_secret
JWT_EXPIRE_HOURS=168
```

### 3. Initialize Database

```bash
python pipeline/db.py
```

This creates the required tables:
- `circulars` - Stores circular metadata, summaries, S3 keys
- `users` - User authentication (Phase 2)

### 4. Create AWS S3 Bucket

```bash
aws s3 mb s3://regradar-pdfs --region ap-south-1
```

Or create via AWS Console.

### 5. Create Pinecone Index

The pipeline will auto-create the index on first run, or create manually:
- **Name**: `regradar`
- **Dimension**: 1024 (Voyage-2)
- **Metric**: Cosine
- **Cloud**: AWS
- **Region**: us-east-1

---

## 🎯 Running the Pipeline

### Full Pipeline (50 circulars per source)
```bash
python run_pipeline.py
```

### Test Mode (5 circulars per source)
```bash
python run_pipeline.py test
```

### Custom Limit
```bash
python run_pipeline.py full 100
```

### Pipeline Steps

The pipeline executes 6 steps automatically:

1. **Database Initialization** - Creates tables if needed
2. **Web Scraping** - Discovers new circulars from RBI & SEBI
3. **PDF Download & S3 Upload** - Downloads and stores PDFs
4. **Database Storage** - Saves circular metadata
5. **PDF Text Extraction** - Extracts text with page numbers
6. **AI Summarization** - Generates summaries via Claude
7. **Chunking & Vector Indexing** - Embeds and indexes in Pinecone

---

## 🔍 Testing Queries

### Search Mode (returns matching circulars)
```bash
python pipeline/test_query.py search "KYC guidelines"
```

### Ask Mode (RAG with AI answer + citations)
```bash
python pipeline/test_query.py ask "What are the new KYC rules for banks?"
```

### Interactive Mode
```bash
python pipeline/test_query.py
```

Commands in interactive mode:
- `/search <query>` - Search circulars
- `/ask <question>` - Get AI answer with citations
- `/quit` - Exit

---

## 📊 Cost Estimates

### Per Circular Processing
- Voyage AI embeddings: ~5000 tokens → **FREE** (within 50M/month limit)
- Claude summary: ~2500 tokens → **$0.014**

### Monthly Costs (50 circulars/month)
- Pipeline processing: 50 × $0.014 = **$0.70**
- User searches (3000/month): ~**$27**
- AWS S3: ~**$0.50**
- **Total: ~$28-29/month**

### Free Tier Services
- Vercel (frontend)
- Railway (backend + PostgreSQL)
- Pinecone (vector storage)
- Voyage AI (embeddings)

---

## 📁 Project Structure

```
ComplianceIQ/
├── pipeline/
│   ├── scraper.py          # RBI & SEBI web scraper
│   ├── downloader.py       # PDF download + S3 upload
│   ├── parser.py           # PyMuPDF text extraction
│   ├── chunker.py          # LangChain chunking + Pinecone indexing
│   ├── summarizer.py       # AWS Bedrock Claude summarization
│   ├── db.py               # PostgreSQL operations
│   └── test_query.py       # CLI testing tool
├── backend/                # FastAPI (Phase 2)
│   └── app/
│       ├── main.py
│       ├── models/
│       ├── routes/
│       └── services/
├── frontend/               # React (Phase 3)
│   └── src/
├── data/
│   ├── pdfs/              # Downloaded PDFs
│   │   ├── rbi/
│   │   └── sebi/
│   └── parsed/            # Parsed text
├── run_pipeline.py        # Master orchestration script
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🔧 Development Workflow

### Phase 1: Data Pipeline (Week 1) ✅
- [x] Web scraping (RBI + SEBI)
- [x] PDF download & S3 storage
- [x] Text extraction with page tracking
- [x] LangChain chunking
- [x] Voyage AI embeddings
- [x] Pinecone vector indexing
- [x] Claude Sonnet 4 summarization
- [x] PostgreSQL metadata storage
- [x] CLI testing tool

### Phase 2: Backend API (Week 2)
- [ ] FastAPI setup
- [ ] JWT authentication
- [ ] POST /auth/register, /login
- [ ] POST /search (vector search)
- [ ] POST /chat (RAG with SSE streaming)
- [ ] GET /circulars (list all)
- [ ] GET /circulars/{id} (detail)

### Phase 3: React Frontend (Week 3)
- [ ] Vite + React + Tailwind setup
- [ ] Login page
- [ ] Search interface
- [ ] Streaming chat component
- [ ] Circular detail page
- [ ] Result cards with citations

### Phase 4: Deployment (Week 4)
- [ ] Deploy backend to Railway
- [ ] Deploy frontend to Vercel
- [ ] Set up APScheduler for daily runs
- [ ] Production environment variables
- [ ] End-to-end testing

---

## 🐛 Troubleshooting

### Database Connection Error
```bash
# Verify DATABASE_URL in .env
# Ensure PostgreSQL is running
# Test connection:
python -c "from pipeline.db import init_db; init_db()"
```

### AWS Bedrock Access Denied
```bash
# Verify AWS credentials
aws sts get-caller-identity

# Ensure Bedrock model access is enabled in AWS Console
# Region must be ap-south-1 (Mumbai)
```

### Pinecone Connection Error
```bash
# Verify PINECONE_API_KEY
# Check index name matches PINECONE_INDEX in .env
```

### Voyage AI Rate Limit
```bash
# Free tier: 50M tokens/month
# Monitor usage at https://dash.voyageai.com
```

---

## 📝 Next Steps

1. **Run Test Pipeline**: `python run_pipeline.py test`
2. **Test Queries**: `python pipeline/test_query.py`
3. **Verify Results**: Check PostgreSQL and Pinecone for indexed data
4. **Schedule Daily Runs**: Set up APScheduler (Phase 4)
5. **Build Backend API**: Start Phase 2 implementation
6. **Build Frontend**: Start Phase 3 implementation

---

## 🤝 Contributing

This is a personal project for learning and portfolio purposes. Feedback and suggestions are welcome!

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🔗 Links

- **RBI Circulars**: https://www.rbi.org.in
- **SEBI Circulars**: https://www.sebi.gov.in
- **AWS Bedrock**: https://aws.amazon.com/bedrock/
- **Voyage AI**: https://www.voyageai.com/
- **Pinecone**: https://www.pinecone.io/

---

**Built with Claude Code and AWS Bedrock Claude Sonnet 4**
