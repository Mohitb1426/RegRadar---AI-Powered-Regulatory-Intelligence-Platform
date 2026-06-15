# RegRadar Quick Setup Guide

## 🚀 Quick Start (5 minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Copy the example file
cp .env.example .env

# Edit .env with your actual credentials
# Required: AWS keys, Voyage AI key, Pinecone key, PostgreSQL URL
```

### 3. Initialize Database
```bash
python pipeline/db.py
```

### 4. Run Test Pipeline
```bash
python run_pipeline.py test
```

This will:
- ✓ Scrape 5 circulars from RBI and SEBI
- ✓ Download PDFs to AWS S3
- ✓ Extract text with page numbers
- ✓ Generate AI summaries via Claude Sonnet 4
- ✓ Create embeddings and index in Pinecone
- ✓ Store metadata in PostgreSQL

### 5. Test Queries
```bash
# Interactive mode
python pipeline/test_query.py

# Or directly
python pipeline/test_query.py ask "What are the new KYC guidelines?"
```

---

## 🔑 Getting API Keys

### AWS Bedrock (Claude API)
1. AWS Console → IAM → Create User
2. Attach policy: `AmazonBedrockFullAccess`
3. Create access keys
4. Enable Claude Sonnet 4 in Bedrock console (ap-south-1 region)

### Voyage AI (Free Tier)
1. Visit: https://www.voyageai.com/
2. Sign up (free)
3. Dashboard → API Keys
4. Copy key (starts with `pa-`)

### Pinecone (Free Tier)
1. Visit: https://www.pinecone.io/
2. Sign up (free tier: 1 index, 100k vectors)
3. Create API key
4. Note: Index will be auto-created on first run

### PostgreSQL
**Option 1: Railway (Free)**
1. https://railway.app/
2. New Project → Add PostgreSQL
3. Copy DATABASE_URL

**Option 2: Local PostgreSQL**
```bash
# Install PostgreSQL
# Create database
createdb regradar

# Connection string format:
# postgresql+asyncpg://user:password@localhost:5432/regradar
```

### AWS S3
```bash
# Using AWS CLI
aws s3 mb s3://regradar-pdfs --region ap-south-1

# Or via AWS Console:
# S3 → Create Bucket → Name: regradar-pdfs → Region: ap-south-1
```

---

## 📊 Verify Setup

### Check Database Connection
```bash
python -c "from pipeline.db import init_db; init_db()"
# Expected: "Database tables created successfully!"
```

### Check AWS Bedrock
```bash
python pipeline/summarizer.py
# Expected: Test summary generated
```

### Check Voyage AI
```bash
python pipeline/chunker.py
# Expected: "Embedding dimension: 1024"
```

### Check Pinecone
```bash
python -c "from pipeline.chunker import VectorStore; vs = VectorStore(); print('Connected!')"
# Expected: "Connected to index: regradar"
```

---

## ⚡ Common Issues

### "ModuleNotFoundError: No module named 'fitz'"
```bash
pip install PyMuPDF
```

### "AWS credentials not configured"
Check `.env` file has:
```
AWS_ACCESS_KEY_ID=AKIAXXXXXXXX
AWS_SECRET_ACCESS_KEY=xxxxxxxx
```

### "Pinecone index not found"
The index is auto-created on first run. Wait ~60 seconds after creation before querying.

### "Database connection failed"
Check DATABASE_URL format:
```
postgresql+asyncpg://user:pass@host:5432/dbname
```

### "S3 bucket not found"
Create bucket first:
```bash
aws s3 mb s3://regradar-pdfs --region ap-south-1
```

---

## 🎯 Next Steps After Setup

1. **Run Full Pipeline** (50 circulars)
   ```bash
   python run_pipeline.py
   ```

2. **Schedule Daily Runs** (coming in Phase 4)
   ```bash
   # APScheduler will run pipeline automatically
   ```

3. **Build Backend API** (Phase 2)
   - FastAPI with authentication
   - Search and chat endpoints
   - SSE streaming

4. **Build Frontend** (Phase 3)
   - React app with Tailwind
   - Search interface
   - Streaming chat

---

## 📞 Need Help?

Check the main [README.md](README.md) for detailed documentation.

For issues:
1. Verify all environment variables are set
2. Check logs for specific error messages
3. Test each component individually (db.py, summarizer.py, etc.)

---

**Ready to start?** Run `python run_pipeline.py test` 🚀
