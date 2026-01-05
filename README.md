# 🔍 FastAPI API Monitoring Service

![FastAPI](https://img.shields.io/badge/FastAPI-0.128.0-009688?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-D71F00?style=for-the-badge&logo=sqlalchemy)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

> **Simple yet powerful API monitoring service** untuk mengecek uptime, response time, dan health status dari website atau API apapun.

Perfect untuk **junior backend developers** yang mau belajar:
- ✅ REST API development dengan FastAPI
- ✅ Async programming di Python
- ✅ Database dengan SQLAlchemy ORM
- ✅ HTTP monitoring & observability dasar

---

## 🌟 Features

### Core Features
- 🎯 **URL Monitoring** - Monitor HTTP/HTTPS endpoints
- ⚡ **Response Time Tracking** - Measure response time dalam milliseconds
- 💚 **Health Status** - Auto-detect healthy/unhealthy services
- 📊 **Pagination** - Efficient data retrieval dengan pagination
- 🔄 **Async Operations** - Fully async dengan httpx
- 📝 **Auto Documentation** - Swagger UI & ReDoc built-in

### Tech Stack
- **Framework:** FastAPI 0.128.0
- **Server:** Uvicorn (ASGI)
- **Database:** SQLite + SQLAlchemy ORM
- **HTTP Client:** httpx (async)
- **Validation:** Pydantic v2

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)

### Installation

1. **Clone repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/fastapi-api-monitor.git
   cd fastapi-api-monitor
   ```

2. **Create virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # Windows
   .\venv\Scripts\Activate.ps1
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

5. **Access the API**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc
   - API: http://localhost:8000

---

## 📖 API Documentation

### Base URL
```
http://localhost:8000/api/v1
```

### Endpoints

#### 1. Monitor URL
Monitor sebuah URL dan simpan hasilnya.

**Endpoint:** `POST /monitor`

**Request Body:**
```json
{
  "url": "https://www.google.com"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "url": "https://www.google.com",
  "status_code": 200,
  "response_time_ms": 145.32,
  "is_healthy": true,
  "error_message": null,
  "created_at": "2026-01-05T10:30:45.123456"
}
```

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/monitor" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.google.com"}'
```

---

#### 2. Get All Results (Paginated)
Retrieve semua monitoring results dengan pagination.

**Endpoint:** `GET /results`

**Query Parameters:**
- `page` (optional): Halaman yang mau diambil (default: 1)
- `page_size` (optional): Jumlah items per halaman (default: 10, max: 100)

**Response:** `200 OK`
```json
{
  "total": 25,
  "page": 1,
  "page_size": 10,
  "total_pages": 3,
  "results": [
    {
      "id": 25,
      "url": "https://www.github.com",
      "status_code": 200,
      "response_time_ms": 89.45,
      "is_healthy": true,
      "error_message": null,
      "created_at": "2026-01-05T12:00:00.000000"
    }
  ]
}
```

**cURL Example:**
```bash
# Default pagination
curl "http://localhost:8000/api/v1/results"

# Custom pagination
curl "http://localhost:8000/api/v1/results?page=2&page_size=5"
```

---

#### 3. Get Result by ID
Retrieve detail monitoring result berdasarkan ID.

**Endpoint:** `GET /results/{id}`

**Path Parameters:**
- `id`: ID monitoring result

**Response:** `200 OK`
```json
{
  "id": 1,
  "url": "https://www.google.com",
  "status_code": 200,
  "response_time_ms": 145.32,
  "is_healthy": true,
  "error_message": null,
  "created_at": "2026-01-05T10:30:45.123456"
}
```

**Error Response:** `404 Not Found`
```json
{
  "detail": "Monitoring result with ID 999 not found"
}
```

**cURL Example:**
```bash
curl "http://localhost:8000/api/v1/results/1"
```

---

## 🏗️ Project Structure

```
fastapi-api-monitor/
│
├── app/
│   ├── __init__.py
│   ├── main.py                 # Entry point & FastAPI app
│   ├── database.py             # Database configuration
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── monitoring.py       # SQLAlchemy models
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── monitoring.py       # Pydantic schemas
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   └── monitor_service.py  # Business logic
│   │
│   └── routers/
│       ├── __init__.py
│       └── monitoring.py       # API endpoints
│
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🧠 How It Works

### 1. **Async HTTP Monitoring**
Menggunakan `httpx.AsyncClient` untuk non-blocking HTTP requests:
```python
async with httpx.AsyncClient(timeout=10.0) as client:
    start_time = time.perf_counter()
    response = await client.get(url)
    end_time = time.perf_counter()
    response_time_ms = (end_time - start_time) * 1000
```

### 2. **Health Status Logic**
```python
def is_healthy(status_code: Optional[int]) -> bool:
    if status_code is None:
        return False
    return 200 <= status_code < 400  # 2xx & 3xx = healthy
```

### 3. **Pagination Implementation**
```python
offset = (page - 1) * page_size
results = db.query(Model).limit(page_size).offset(offset).all()
total_pages = math.ceil(total / page_size)
```

---

## 📊 Database Schema

**Table:** `monitoring_results`

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer | Primary key (auto-increment) |
| `url` | String | URL yang dimonitor |
| `status_code` | Integer | HTTP status code (200, 404, etc) |
| `response_time_ms` | Float | Response time dalam milliseconds |
| `is_healthy` | Boolean | Health status (True/False) |
| `error_message` | String | Error message (nullable) |
| `created_at` | DateTime | Timestamp (auto-generated) |

---

## 🔥 Use Cases

### 1. **Monitor Multiple Services**
```python
services = [
    "https://api.github.com",
    "https://api.stripe.com",
    "https://jsonplaceholder.typicode.com"
]

for url in services:
    response = requests.post(
        "http://localhost:8000/api/v1/monitor",
        json={"url": url}
    )
    print(response.json())
```

### 2. **Calculate Uptime Percentage**
```python
results = requests.get("http://localhost:8000/api/v1/results?page_size=100").json()
healthy_count = sum(1 for r in results["results"] if r["is_healthy"])
uptime = (healthy_count / results["total"]) * 100
print(f"Uptime: {uptime:.2f}%")
```

### 3. **Monitor Average Response Time**
```python
results = requests.get("http://localhost:8000/api/v1/results").json()["results"]
avg_response = sum(r["response_time_ms"] for r in results if r["response_time_ms"]) / len(results)
print(f"Average response time: {avg_response:.2f}ms")
```

---

## 🛠️ Development

### Run Tests (Coming Soon)
```bash
pytest tests/ -v
```

### Code Formatting
```bash
black app/
isort app/
```

### Type Checking
```bash
mypy app/
```

---

## 🚧 Roadmap

- [ ] Scheduled monitoring (cron jobs)
- [ ] Webhook notifications (Slack, Discord)
- [ ] Historical charts & graphs
- [ ] Multi-region monitoring
- [ ] SSL certificate expiry check
- [ ] API authentication (API keys)
- [ ] Docker support
- [ ] PostgreSQL support
- [ ] Email alerts
- [ ] Dashboard UI

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Your Name**
- GitHub: [@Yogiexc](https://github.com/Yogiexc)

---

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Amazing web framework
- [httpx](https://www.python-httpx.org/) - Modern HTTP client
- [SQLAlchemy](https://www.sqlalchemy.org/) - Powerful ORM
- [Pydantic](https://docs.pydantic.dev/) - Data validation

---

## 📸 Screenshots

### Swagger UI
![Swagger UI](screenshot/image.png
)


---

**⭐ If you find this project helpful, please give it a star!**