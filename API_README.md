# GTM Intelligence API

A comprehensive REST API for the GTM Intelligence system that processes large datasets with intelligent search query generation and parallel processing.

## 🚀 Quick Start

### 1. Start the API Server

```bash
# Start the FastAPI server
python server.py
```

The server will be available at:
- **API Server**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### 2. Test the API

```bash
# Run the test client
python test_api.py
```

## 📋 API Endpoints

### POST /research/batch
Start a new research batch with intelligent query generation and parallel processing.

**Request Body:**
```json
{
    "research_goal": "Find fintech companies using AI for fraud detection",
    "search_depth": "comprehensive",
    "max_parallel_searches": 20,
    "confidence_threshold": 0.8,
    "max_iterations": 3
}
```

**Response:**
```json
{
    "research_id": "uuid",
    "status": "queued",
    "total_companies": 0,
    "search_strategies_generated": 0,
    "total_searches_executed": 0,
    "processing_time_ms": 0,
    "company_domains": [],
    "results": [],
    "search_performance": {},
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
}
```

### GET /research/{research_id}
Get complete research results by ID.

**Response:**
```json
{
    "research_id": "uuid",
    "status": "completed",
    "total_companies": 150,
    "search_strategies_generated": 12,
    "total_searches_executed": 1847,
    "processing_time_ms": 28450,
    "company_domains": ["stripe.com", "square.com"],
    "results": [
        {
            "domain": "stripe.com",
            "confidence_score": 0.92,
            "evidence_sources": 15,
            "findings": {
                "ai_fraud_detection": true,
                "technologies": ["TensorFlow", "scikit-learn"],
                "evidence": [...],
                "signals_found": 8
            },
            "signals_found": 8
        }
    ],
    "search_performance": {
        "queries_per_second": 65,
        "cache_hit_rate": 0.34,
        "failed_requests": 12
    },
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
}
```

### GET /research/{research_id}/status
Get research status and progress.

**Response:**
```json
{
    "research_id": "uuid",
    "status": "processing",
    "progress": 50.0,
    "current_step": "Executing research workflow",
    "estimated_completion": null
}
```

### GET /research
List all research sessions.

**Response:**
```json
{
    "sessions": [
        {
            "research_id": "uuid",
            "status": "completed",
            "research_goal": "Find fintech companies using AI for fraud detection",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00"
        }
    ]
}
```

### DELETE /research/{research_id}
Delete a research session.

**Response:**
```json
{
    "message": "Research session deleted successfully"
}
```

### GET /health
Health check endpoint.

**Response:**
```json
{
    "status": "healthy",
    "timestamp": "2024-01-01T00:00:00",
    "active_sessions": 5
}
```

## 🔧 Configuration

### Request Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `research_goal` | string | required | High-level goal of the research |
| `search_depth` | string | "standard" | "quick" \| "standard" \| "comprehensive" |
| `max_parallel_searches` | integer | 20 | Number of parallel search executions |
| `confidence_threshold` | float | 0.8 | Minimum acceptable confidence (0.0-1.0) |
| `max_iterations` | integer | 3 | Maximum research iterations |

### Search Depth Options

- **quick**: Fast search with minimal depth
- **standard**: Balanced search depth and speed
- **comprehensive**: Deep search with maximum coverage

## 🏗️ Architecture

### System Components

1. **FastAPI Application** (`app/api.py`)
   - REST API endpoints
   - Background task processing
   - Session management

2. **GTM Intelligence Engine**
   - Query generation and strategy refinement
   - Multi-source parallel search
   - Quality evaluation and feedback loops

3. **State Management**
   - In-memory session storage
   - Progress tracking
   - Result aggregation

### Data Flow

```
Client Request → FastAPI → Background Task → GTM Graph → Results → Session Storage
```

## 🚀 Usage Examples

### Python Client

```python
import requests
import time

# Start research
response = requests.post("http://localhost:8000/research/batch", json={
    "research_goal": "Find B2B SaaS companies with 50-200 employees raising Series A in 2024",
    "search_depth": "comprehensive",
    "max_parallel_searches": 20,
    "confidence_threshold": 0.8
})

research_id = response.json()["research_id"]

# Monitor progress
while True:
    status_response = requests.get(f"http://localhost:8000/research/{research_id}/status")
    status = status_response.json()
    
    print(f"Status: {status['status']} | Progress: {status['progress']}%")
    
    if status['status'] in ['completed', 'failed']:
        break
    
    time.sleep(10)

# Get results
results_response = requests.get(f"http://localhost:8000/research/{research_id}")
results = results_response.json()

print(f"Found {results['total_companies']} companies")
for result in results['results']:
    print(f"- {result['domain']}: {result['confidence_score']}")
```

### cURL Examples

```bash
# Start research
curl -X POST "http://localhost:8000/research/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "research_goal": "Find fintech companies using AI for fraud detection",
    "search_depth": "comprehensive",
    "max_parallel_searches": 20,
    "confidence_threshold": 0.8
  }'

# Get status
curl "http://localhost:8000/research/{research_id}/status"

# Get results
curl "http://localhost:8000/research/{research_id}"
```

## 📊 Performance Metrics

The API tracks comprehensive performance metrics:

- **Processing Time**: Total execution time in milliseconds
- **Queries per Second**: Search throughput
- **Cache Hit Rate**: Caching effectiveness
- **Failed Requests**: Error rate tracking
- **Total Searches**: Number of searches executed
- **Evidence Sources**: Number of data sources per company

## 🔍 Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

### Session Monitoring
```bash
curl http://localhost:8000/research
```

## 🛠️ Development

### Running in Development Mode

```bash
# Start with auto-reload
python server.py

# Or use uvicorn directly
uvicorn app.api:app --reload --host 0.0.0.0 --port 8000
```

### Testing

```bash
# Run the test client
python test_api.py

# Or test individual endpoints
curl http://localhost:8000/health
```

## 📝 Error Handling

The API includes comprehensive error handling:

- **404**: Research session not found
- **422**: Invalid request parameters
- **500**: Internal server errors

All errors include descriptive messages and appropriate HTTP status codes.

## 🔐 Security Considerations

- CORS enabled for cross-origin requests
- Input validation with Pydantic models
- Background task isolation
- Session-based request handling

## 📈 Scaling Considerations

For production deployment:

1. **Database Storage**: Replace in-memory storage with Redis/PostgreSQL
2. **Load Balancing**: Use multiple API instances
3. **Caching**: Implement Redis caching for results
4. **Monitoring**: Add Prometheus/Grafana metrics
5. **Authentication**: Add API key authentication

## 🎯 Next Steps

1. **Additional Data Sources**: News APIs, job boards, LinkedIn
2. **Real-time Updates**: WebSocket/SSE for live progress
3. **Advanced Caching**: Redis-based result caching
4. **Distributed Processing**: Multi-node processing support
5. **Authentication**: API key management
6. **Rate Limiting**: Request throttling
7. **Analytics**: Usage analytics and reporting

---

For more information, see the main [README.md](README.md) for the complete GTM Intelligence system documentation. 