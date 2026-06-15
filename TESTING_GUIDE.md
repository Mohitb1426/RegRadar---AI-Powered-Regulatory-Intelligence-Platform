# RegRadar Testing Guide

## 🧪 Phase 1 Testing Checklist

Before running the full pipeline, test each component individually.

---

## Step 1: Configure API Keys

Edit `.env` file with your credentials. I see you already have **Voyage AI key** configured! ✅

Still need:
- [ ] AWS_ACCESS_KEY_ID
- [ ] AWS_SECRET_ACCESS_KEY  
- [ ] PINECONE_API_KEY
- [ ] DATABASE_URL

### Quick Setup Links:
- **Pinecone** (free): https://www.pinecone.io/ → Sign up → Copy API key
- **PostgreSQL**: Use local or Railway → https://railway.app/

---

## Step 2: Run Setup Test

This tests all components without scraping:

```bash
python test_setup.py
```

Expected output:
```
====================
PASS Environment Variables
PASS Database  
PASS AWS Bedrock (Claude)
PASS Voyage AI (Embeddings)  
PASS Pinecone (Vector DB)
PASS AWS S3 (Storage)
PASS PDF Processing
====================
Total: 7/7 tests passed
```

---

## Step 3: Test Individual Components

### 3.1 Database
```bash
python pipeline/db.py
```
✅ Expected: "Database tables created successfully!"

### 3.2 AWS Bedrock (Claude Sonnet 4)
```bash
python pipeline/summarizer.py
```
✅ Expected: Test summary generated

### 3.3 Voyage AI Embeddings
```bash
python pipeline/chunker.py
```
✅ Expected: "Embedding dimension: 1024"

### 3.4 Web Scraper (dry run)
```bash
python pipeline/scraper.py
```
✅ Expected: Lists found circulars (without downloading)

---

## Step 4: Run Test Pipeline

Process 5 circulars end-to-end:

```bash
python run_pipeline.py test
```

This will:
1. ✓ Scrape 5 circulars from RBI & SEBI
2. ✓ Download PDFs to S3
3. ✓ Extract text with page numbers
4. ✓ Generate AI summaries
5. ✓ Create embeddings
6. ✓ Index in Pinecone
7. ✓ Store in PostgreSQL

**Duration**: ~5-10 minutes  
**Cost**: ~$0.10-$0.15

---

## Step 5: Test Queries

### Search for relevant circulars:
```bash
python pipeline/test_query.py search "KYC guidelines"
```

### Ask questions (RAG):
```bash
python pipeline/test_query.py ask "What are the new compliance requirements?"
```

### Interactive mode:
```bash
python pipeline/test_query.py
```

Commands:
- `/search <query>` - Vector search
- `/ask <question>` - RAG answer with citations
- `/quit` - Exit

---

## Step 6: Verify Data

### Check PostgreSQL:
```bash
python -c "from pipeline.db import get_all_circulars; circulars = get_all_circulars(); print(f'Total circulars: {len(circulars)}')"
```

### Check Pinecone vectors:
```bash
python -c "from pipeline.chunker import VectorStore; vs = VectorStore(); stats = vs.index.describe_index_stats(); print(f'Total vectors: {stats.total_vector_count}')"
```

---

## 🐛 Troubleshooting

### Error: "AWS credentials not configured"
- Check `.env` has `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`
- Verify keys are valid: `aws sts get-caller-identity`

### Error: "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### Error: "Database connection failed"
- For local PostgreSQL: `createdb regradar`
- For Railway: Copy DATABASE_URL from dashboard

### Error: "Pinecone index not found"
- Index is auto-created on first run
- Wait 60 seconds after creation before querying

### Error: "S3 bucket not found"
```bash
aws s3 mb s3://regradar-pdfs --region ap-south-1
```

### Web scraper finds no circulars
- This is normal if websites are unreachable
- You can skip to testing with sample data

---

## ✅ Success Criteria

Phase 1 is ready when:
- [x] All dependencies installed
- [ ] All 7 setup tests pass
- [ ] Test pipeline completes successfully
- [ ] At least 1 circular indexed
- [ ] Query returns relevant results with citations
- [ ] Citations include page numbers

---

## 📊 What to Expect

### Test Pipeline Stats:
```
Circulars discovered:  10
PDFs downloaded:       8-10
PDFs parsed:           8-10
Circulars summarized:  8-10
Circulars indexed:     8-10
```

### Query Results:
```
Query: "KYC guidelines"
Found: 5 relevant chunks
Result 1 (Relevance: 0.852)
Circular: RBI Master Direction on KYC Norms
Source: RBI
Page: 5
```

### RAG Answer:
```
Question: "What are the new KYC requirements?"
Answer: Based on RBI circular dated 2024-01-15...
Sources:
1. RBI Master Direction on KYC - Page 5
2. SEBI Circular on Customer Verification - Page 3
```

---

## ⏭️ After Testing

If all tests pass:
1. Run full pipeline: `python run_pipeline.py`
2. Proceed to Phase 2: FastAPI Backend
3. Start building authentication and API endpoints

---

## 💡 Tips

- Test with small batches first (5 circulars)
- Monitor AWS costs in Bedrock dashboard
- Check Pinecone free tier limits (100k vectors = ~5000 circulars)
- Keep `.env` secure - never commit to git (already in .gitignore)

---

**Ready to test?** Start with: `python test_setup.py` 🚀
