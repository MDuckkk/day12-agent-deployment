#  Delivery Checklist — Day 12 Lab Submission

> **Student Name:** Bùi Minh Đức 
> **Student ID:** 2A202600005  
> **Date:** 17/04/2026

---

##  Submission Requirements

Submit a **GitHub repository** containing:

### 1. Mission Answers (40 points)

Create a file `MISSION_ANSWERS.md` with your answers to all exercises:

```markdown
# Day 12 Lab - Mission Answers

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found

1. **Không có error handling** — Không có `try/except` quanh LLM call. Nếu service lỗi sẽ trả về HTTP 500 với stack trace thô, lộ thông tin nội bộ cho client.
   ```python
   response = ask(question)
   ```

2. **Nhận `question` qua query parameter thay vì request body** — FastAPI hiểu `question: str` trong hàm POST là query param (`/ask?question=...`). Câu hỏi bị ghi vào URL, server log, browser history — vi phạm bảo mật.
   ```python
   def ask_agent(question: str): 
   ```

3. **Không validate input** — Không kiểm tra `question` có rỗng không, không giới hạn độ dài. Dễ bị abuse, gửi câu hỏi cực dài để tốn token/tiền.

4. **Không có CORS configuration** — Không set CORS middleware, không kiểm soát được domain nào được phép gọi API.

5. **`import os` nhưng không dùng** — Import thừa, cho thấy không có ý định đọc environment variables ở bất kỳ đâu trong file.
    ```python
    import os 
    ```
...

### Exercise 1.3: Comparison table
| Feature | Develop | Production | Why Important? |
|---------|---------|------------|----------------|
| Config | Hardcode trong code | Đọc từ env vars qua `config.py` | Thay đổi config không cần sửa code, bảo mật secrets |
| Secrets | `OPENAI_API_KEY = "sk-..."` | `os.getenv("OPENAI_API_KEY")` | Tránh lộ key khi push code lên GitHub |
| Logging | `print()` + log ra secret | Structured JSON logging, không log secret | Dễ parse, tích hợp log aggregator (Datadog, Loki) |
| Health check | Không có | `/health` (liveness) + `/ready` (readiness) | Platform tự restart khi crash, load balancer biết route traffic |
| Port/Host | `host="localhost"`, `port=8000` cứng | `host="0.0.0.0"`, `port=int(os.getenv("PORT"))` | Chạy được trong container, tương thích Railway/Render |
| Error handling | Không có | HTTPException + try/except | Không lộ stack trace, trả lỗi có nghĩa cho client |
| Input validation | Không có | Kiểm tra rỗng, giới hạn độ dài | Tránh abuse, bảo vệ chi phí LLM |
| CORS | Không config | CORSMiddleware với allowed_origins | Kiểm soát domain được phép gọi API |
| Graceful shutdown | Không có | SIGTERM handler + lifespan context | Hoàn thành request đang xử lý trước khi tắt |
| Reload | `reload=True` luôn | `reload=settings.debug` | Không dùng debug mode trong production |
...

## Part 2: Docker

### Exercise 2.1: Dockerfile questions
1. **Base image là gì?**
   `python:3.11` — đây là full Python distribution (~1 GB), bao gồm toàn bộ Python runtime, pip, và các system tools. Phù hợp cho develop vì dễ debug, nhưng nặng cho production.

2. **Working directory là gì?**
   `/app` — được set bằng lệnh `WORKDIR /app`. Tất cả lệnh sau đó (`COPY`, `RUN`, `CMD`) đều chạy trong thư mục này bên trong container. Nếu thư mục chưa tồn tại, Docker tự tạo.

3. **Tại sao COPY requirements.txt trước?**
   Vì **Docker layer cache**. Mỗi lệnh trong Dockerfile tạo ra một layer. Docker chỉ rebuild layer khi nội dung thay đổi.
   - Nếu copy `requirements.txt` trước → `pip install` chỉ chạy lại khi dependencies thay đổi
   - Nếu copy toàn bộ code trước → mỗi lần sửa code dù 1 dòng, `pip install` cũng chạy lại từ đầu → build chậm hơn nhiều
   ```dockerfile
   COPY requirements.txt .        # layer này ít thay đổi
   RUN pip install -r requirements.txt  # chỉ rebuild khi requirements đổi
   COPY app.py .                  # layer này thay đổi thường xuyên
   ```

4. **CMD vs ENTRYPOINT khác nhau thế nào?**

   | | `CMD` | `ENTRYPOINT` |
   |--|-------|--------------|
   | Mục đích | Lệnh mặc định, **có thể override** khi `docker run` | Lệnh chính, **không bị override** dễ dàng |
   | Override | `docker run image python other.py` → chạy `other.py` | `docker run image python other.py` → `python other.py` chỉ là argument thêm vào |
   | Dùng khi | App có thể chạy nhiều mode khác nhau | Container chỉ có 1 mục đích cố định |
   | Kết hợp | `ENTRYPOINT` = executable, `CMD` = default args | — |

   Ví dụ trong Dockerfile này dùng `CMD ["python", "app.py"]` — phù hợp cho develop vì có thể override để debug:
   ```bash
   docker run agent-develop python -c "import app; print('ok')"
   ```
   Production thường dùng `ENTRYPOINT ["python", "app.py"]` để đảm bảo container luôn chạy đúng service.
...

### Exercise 2.3: Image size comparison
- Develop: 1.66 GB
- Production: 236 GB
- Difference: 85.8 %

## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment
- URL: https://enthusiastic-amazement-production-7900.up.railway.app
- Screenshot: ![alt text](image.png)

## Part 4: API Security

### Exercise 4.1-4.3: Test results

1. 
curl http://localhost:8000/ask -X POST \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello"}'
{"detail":"Missing API key. Include header: X-API-Key: <your-key>"}(.venv) 

curl http://localhost:8000/ask -X POST \
  -H "X-API-Key: secret-key-123" \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello"}'
{"detail":"Invalid API key."}(.venv) 

2. 
MDuck@DESKTOP-R3SUQJN MINGW64 /d/AI_Vin/Lab/assignments/day12_ha-tang-cloud_va_deployment/04-api-gateway/production (main)
$ curl http://localhost:8000/auth/token -X POST \
  -H "Content-Type: application/json" \
  -d '{"username": "student", "password": "demo123"}'
{"access_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdHVkZW50Iiwicm9sZSI6InVzZXIiLCJpYXQiOjE3NzY0MTYyOTQsImV4cCI6MTc3NjQxOTg5NH0.8ANSDAEksWzt97tnLYbT4hKgTbIqQzxORaLB98_gz_4","token_type":"bearer","expires_in_minutes":60,"hint":"Include in header: Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."}(.venv) 
MDuck@DESKTOP-R3SUQJN MINGW64 /d/AI_Vin/Lab/assignments/day12_ha-tang-cloud_va_deployment/04-api-gateway/production (main)
$ TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdHVkZW50Iiwicm9sZSI6InVzZXIiLCJpYXQiOjE3NzY0MTYyOTQsImV4cCI6MTc3NjQxOTg5NH0.8ANSDAEksWzt97tnLYbT4hKgTbIqQzxORaLB98_gz_4"
curl http://localhost:8000/ask -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question": "Explain JWT"}'
{"question":"Explain JWT","answer":"Tôi là AI agent được deploy lên cloud. Câu hỏi của bạn đã được nhận.","usage":{"requests_remaining":9,"budget_remaining_usd":1.9e-05}}(.venv) 

3. 
$ for i in {1..20}; do
  curl http://localhost:8000/ask -X POST \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"question": "Test '$i'"}'
  echo ""
done
{"question":"Test 1","answer":"Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đi nhé.","usage":{"requests_remaining":8,"budget_remaining_usd":3.5e-05}}
{"question":"Test 2","answer":"Tôi là AI agent được deploy lên cloud. Câu hỏi của bạn đã được nhận.","usage":{"requests_remaining":7,"budget_remaining_usd":5.3e-05}}
{"question":"Test 3","answer":"Đây là câu trả lời từ AI agent (mock). Trong production, đây sẽ là response từ OpenAI/Anthropic.","usage":{"requests_remaining":6,"budget_remaining_usd":7.4e-05}}
{"question":"Test 4","answer":"Tôi là AI agent được deploy lên cloud. Câu hỏi của bạn đã được nhận.","usage":{"requests_remaining":5,"budget_remaining_usd":9.3e-05}}
{"question":"Test 5","answer":"Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đi nhé.","usage":{"requests_remaining":4,"budget_remaining_usd":0.000109}}
{"question":"Test 6","answer":"Tôi là AI agent được deploy lên cloud. Câu hỏi của bạn đã được nhận.","usage":{"requests_remaining":3,"budget_remaining_usd":0.000128}}
{"question":"Test 7","answer":"Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đi nhé.","usage":{"requests_remaining":2,"budget_remaining_usd":0.000144}}
{"question":"Test 8","answer":"Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đi nhé.","usage":{"requests_remaining":1,"budget_remaining_usd":0.00016}}
{"question":"Test 9","answer":"Đây là câu trả lời từ AI agent (mock). Trong production, đây sẽ là response từ OpenAI/Anthropic.","usage":{"requests_remaining":0,"budget_remaining_usd":0.000181}}
{"detail":{"error":"Rate limit exceeded","limit":10,"window_seconds":60,"retry_after_seconds":24}}
{"detail":{"error":"Rate limit exceeded","limit":10,"window_seconds":60,"retry_after_seconds":23}}
{"detail":{"error":"Rate limit exceeded","limit":10,"window_seconds":60,"retry_after_seconds":23}}
{"detail":{"error":"Rate limit exceeded","limit":10,"window_seconds":60,"retry_after_seconds":23}}
{"detail":{"error":"Rate limit exceeded","limit":10,"window_seconds":60,"retry_after_seconds":22}}
{"detail":{"error":"Rate limit exceeded","limit":10,"window_seconds":60,"retry_after_seconds":22}}
{"detail":{"error":"Rate limit exceeded","limit":10,"window_seconds":60,"retry_after_seconds":22}}
{"detail":{"error":"Rate limit exceeded","limit":10,"window_seconds":60,"retry_after_seconds":22}}
{"detail":{"error":"Rate limit exceeded","limit":10,"window_seconds":60,"retry_after_seconds":21}}
{"detail":{"error":"Rate limit exceeded","limit":10,"window_seconds":60,"retry_after_seconds":21}}
{"detail":{"error":"Rate limit exceeded","limit":10,"window_seconds":60,"retry_after_seconds":21}}

### Exercise 4.4: Cost guard implementation
**Approach:** Implement hàm `check_budget` dùng Redis để track chi phí theo tháng per user.

**Logic từng bước:**
1. **Key theo tháng** — `budget:user_id:2026-04` → sang tháng 5 key mới tự động, không cần cron job reset
2. **Đọc spending hiện tại** từ Redis (`r.get`), mặc định 0 nếu chưa có
3. **So sánh** `current + estimated_cost > $10` → vượt thì `return False`, block request
4. **Ghi lại** chi phí bằng `incrbyfloat` (atomic, thread-safe)
5. **TTL 32 ngày** để Redis tự dọn key cũ, tránh memory leak

## Part 5: Scaling & Reliability

### Exercise 5.1-5.5: Implementation notes

Implement 2 endpoints trong `05-scaling-reliability/develop/app.py`:

- **`GET /health`** (liveness probe) — trả về `status: ok` kèm uptime, memory usage. Platform dùng để quyết định có restart container không.
- **`GET /ready`** (readiness probe) — trả `503` khi agent đang startup hoặc shutdown. Load balancer dùng để quyết định có route traffic vào instance này không.

| | `/health` | `/ready` |
|--|-----------|----------|
| Fail → | Platform restart container | LB ngừng route traffic |
| Trả 503 khi | Process treo, OOM | Đang khởi động / tắt / Redis mất kết nối |

---

3 cơ chế kết hợp trong `develop/app.py`:

1. **Middleware** đếm số request đang xử lý (`_in_flight_requests`)
2. **Lifespan shutdown** — set `_is_ready = False` (LB ngừng route), chờ tối đa 30s cho requests hoàn thành
3. **SIGTERM handler** — log signal, để uvicorn xử lý shutdown

---

**Vấn đề:** Nếu lưu session trong memory, scale lên nhiều instances thì instance B không đọc được session của instance A.

**Giải pháp (`production/app.py`):** Toàn bộ conversation history lưu vào Redis với TTL 1 giờ. Bất kỳ instance nào cũng đọc/ghi được cùng session. Response trả về `served_by: INSTANCE_ID` để thấy rõ điều này.

Code có fallback in-memory khi Redis không có (dev local), nhưng không scalable cho production.

---

Nginx dùng Docker DNS `agent` tự động resolve đến tất cả replicas và round-robin qua chúng. `proxy_next_upstream error` đảm bảo failover tự động khi 1 instance die — client không thấy lỗi.

```
Client → Nginx :8080 → agent_1 → agent_2 → agent_3 (round-robin)
                              ↕
                            Redis (shared state)
```

---

Chạy `python test_stateless.py` — script gửi 5 câu hỏi liên tiếp trong cùng 1 session:
Dù mỗi request đến instance khác nhau, conversation history vẫn liên tục — xác nhận stateless design hoạt động đúng.

```

---

### 2. Full Source Code - Lab 06 Complete (60 points)

Your final production-ready agent with all files:

```
your-repo/
├── app/
│   ├── main.py              # Main application
│   ├── config.py            # Configuration
│   ├── auth.py              # Authentication
│   ├── rate_limiter.py      # Rate limiting
│   └── cost_guard.py        # Cost protection
├── utils/
│   └── mock_llm.py          # Mock LLM (provided)
├── Dockerfile               # Multi-stage build
├── docker-compose.yml       # Full stack
├── requirements.txt         # Dependencies
├── .env.example             # Environment template
├── .dockerignore            # Docker ignore
├── railway.toml             # Railway config (or render.yaml)
└── README.md                # Setup instructions
```

**Requirements:**
-  All code runs without errors
-  Multi-stage Dockerfile (image < 500 MB)
-  API key authentication
-  Rate limiting (10 req/min)
-  Cost guard ($10/month)
-  Health + readiness checks
-  Graceful shutdown
-  Stateless design (Redis)
-  No hardcoded secrets

---

### 3. Service Domain Link

Create a file `DEPLOYMENT.md` with your deployed service information:

```markdown
# Deployment Information

## Public URL
https://your-agent.railway.app

## Platform
Railway / Render / Cloud Run

## Test Commands

### Health Check
```bash
curl https://your-agent.railway.app/health
# Expected: {"status": "ok"}
```

### API Test (with authentication)
```bash
curl -X POST https://your-agent.railway.app/ask \
  -H "X-API-Key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "question": "Hello"}'
```

## Environment Variables Set
- PORT
- REDIS_URL
- AGENT_API_KEY
- LOG_LEVEL

## Screenshots
- [Deployment dashboard](screenshots/dashboard.png)
- [Service running](screenshots/running.png)
- [Test results](screenshots/test.png)
```

##  Pre-Submission Checklist

- [ ] Repository is public (or instructor has access)
- [ ] `MISSION_ANSWERS.md` completed with all exercises
- [ ] `DEPLOYMENT.md` has working public URL
- [ ] All source code in `app/` directory
- [ ] `README.md` has clear setup instructions
- [ ] No `.env` file committed (only `.env.example`)
- [ ] No hardcoded secrets in code
- [ ] Public URL is accessible and working
- [ ] Screenshots included in `screenshots/` folder
- [ ] Repository has clear commit history

---

##  Self-Test

Before submitting, verify your deployment:

```bash
# 1. Health check
curl https://your-app.railway.app/health

# 2. Authentication required
curl https://your-app.railway.app/ask
# Should return 401

# 3. With API key works
curl -H "X-API-Key: YOUR_KEY" https://your-app.railway.app/ask \
  -X POST -d '{"user_id":"test","question":"Hello"}'
# Should return 200

# 4. Rate limiting
for i in {1..15}; do 
  curl -H "X-API-Key: YOUR_KEY" https://your-app.railway.app/ask \
    -X POST -d '{"user_id":"test","question":"test"}'; 
done
# Should eventually return 429
```

---

##  Submission

**Submit your GitHub repository URL:**

```
https://github.com/your-username/day12-agent-deployment
```

**Deadline:** 17/4/2026

---

##  Quick Tips

1.  Test your public URL from a different device
2.  Make sure repository is public or instructor has access
3.  Include screenshots of working deployment
4.  Write clear commit messages
5.  Test all commands in DEPLOYMENT.md work
6.  No secrets in code or commit history

---

##  Need Help?

- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Review [CODE_LAB.md](CODE_LAB.md)
- Ask in office hours
- Post in discussion forum

---

**Good luck! **
