# 🌐 REST API Reference

Complete documentation for the GTM Intelligence System REST API endpoints.

## 📋 **Base URL**
```
http://localhost:8001
```

## 🔍 **Endpoints Overview**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/research` | Synchronous research |
| `POST` | `/research/stream` | Streaming research |

## 🏥 **Health Check**

### **GET /health**
Check if the API server is running.

**Request:**
```bash
curl http://localhost:8001/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-12-19T10:30:00Z",
  "version": "1.0.0"
}
```

## 🔬 **Synchronous Research**

### **POST /research**
Perform research synchronously and return results when complete.

**Request:**
```bash
curl -X POST "http://localhost:8001/research" \
  -H "Content-Type: application/json" \
  -d '{
    "research_goal": "Find fintech companies using AI for fraud detection",
    "search_depth": "quick",
    "max_parallel_searches": 100,
    "confidence_threshold": 0.8,
    "max_iterations": 1
  }'
```

**Request Body:**
```json
{
  "research_goal": "string (required)",
  "search_depth": "quick|standard|comprehensive (default: quick)",
  "max_parallel_searches": "number (default: 100)",
  "confidence_threshold": "number 0.0-1.0 (default: 0.8)",
  "max_iterations": "number 1-10 (default: 1)"
}
```

**Response:**
```json
{
  "research_goal": "Find fintech companies using AI for fraud detection",
  "search_depth": "quick",
  "total_companies": 67,
  "search_strategies_generated": 10,
  "total_searches_executed": 45,
  "iterations_used": 1,
  "processing_time_ms": 45230,
  "quality_metrics": {
    "quality_score": 0.82,
    "coverage_score": 0.78,
    "missing_aspects": ["international companies"],
    "coverage_gaps": ["enterprise solutions"],
    "evidence_issues": ["outdated information"],
    "recommendations": ["focus on recent news"]
  },
  "results": [
    {
      "domain": "stripe.com",
      "confidence_score": 0.92,
      "evidence_sources": 5,
      "signals_found": 8,
      "findings": {
        "goal_achieved": true,
        "technologies": ["AI", "Machine Learning", "Fraud Detection"],
        "evidences": [
          "Stripe uses AI-powered fraud detection systems",
          "Machine learning algorithms analyze transaction patterns"
        ],
        "confidence_level": "High",
        "research_goal": "Find fintech companies using AI for fraud detection"
      }
    }
  ]
}
```

## ⚡ **Streaming Research**

### **POST /research/stream**
Perform research with real-time streaming updates.

**Request:**
```bash
curl -X POST "http://localhost:8001/research/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "research_goal": "Find fintech companies using AI for fraud detection",
    "search_depth": "quick",
    "max_parallel_searches": 100,
    "confidence_threshold": 0.8,
    "max_iterations": 1
  }'
```

**Request Body:** Same as synchronous research

**Response (Server-Sent Events):**
```
data: {"type": "status", "message": "Starting research..."}

data: {"type": "log", "message": "🔍 QUERY AGENT: Starting search strategy generation..."}

data: {"type": "log", "message": "🎯 QUERY AGENT: Generating 10 focused search strategies"}

data: {"type": "log", "message": "🔍 COMPANY AGGREGATOR: Targeting 10 results per search, 10 companies per query, 50 companies max"}

data: {"type": "log", "message": "📰 NEWS EXTRACTOR: Using quick search depth"}

data: {"type": "log", "message": "🔍 Running Serper and News extraction in parallel..."}

data: {"type": "results", "data": {"research_goal": "Find fintech companies using AI for fraud detection", "search_depth": "quick", "total_companies": 67, "search_strategies_generated": 10, "total_searches_executed": 45, "iterations_used": 1, "processing_time_ms": 45230, "quality_metrics": {"quality_score": 0.82, "coverage_score": 0.78}, "results": [...]}}

data: {"type": "complete", "message": "Research completed successfully"}
```

## 📊 **Response Schema**

### **Research Response**
```json
{
  "research_goal": "string",
  "search_depth": "string",
  "total_companies": "number",
  "search_strategies_generated": "number",
  "total_searches_executed": "number",
  "iterations_used": "number",
  "processing_time_ms": "number",
  "quality_metrics": {
    "quality_score": "number (0.0-1.0)",
    "coverage_score": "number (0.0-1.0)",
    "missing_aspects": ["string"],
    "coverage_gaps": ["string"],
    "evidence_issues": ["string"],
    "recommendations": ["string"]
  },
  "results": [
    {
      "domain": "string",
      "confidence_score": "number (0.0-1.0)",
      "evidence_sources": "number",
      "signals_found": "number",
      "findings": {
        "goal_achieved": "boolean",
        "technologies": ["string"],
        "evidences": ["string"],
        "confidence_level": "High|Medium|Low",
        "research_goal": "string"
      }
    }
  ]
}
```

### **Streaming Event Types**
- `status`: Status updates
- `log`: Agent log messages
- `results`: Final research results
- `complete`: Research completion
- `error`: Error messages

## ⚙️ **Parameters**

### **research_goal** (required)
- **Type**: string
- **Description**: The research objective to investigate
- **Example**: "Find fintech companies using AI for fraud detection"

### **search_depth** (optional)
- **Type**: string
- **Default**: "quick"
- **Options**: "quick", "standard", "comprehensive"
- **Description**: Controls the depth and breadth of research

| Depth | Strategies | Companies | Time |
|-------|------------|-----------|------|
| quick | 5 | ~50 | 30s |
| standard | 10 | ~100 | 60s |
| comprehensive | 15 | ~200 | 120s |

### **max_parallel_searches** (optional)
- **Type**: number
- **Default**: 100
- **Range**: 1-200
- **Description**: Maximum concurrent API calls

### **confidence_threshold** (optional)
- **Type**: number
- **Default**: 0.8
- **Range**: 0.0-1.0
- **Description**: Minimum confidence score for results

### **max_iterations** (optional)
- **Type**: number
- **Default**: 1
- **Range**: 1-10
- **Description**: Number of research refinement cycles

## 🚨 **Error Handling**

### **HTTP Status Codes**
- `200 OK`: Successful research
- `400 Bad Request`: Invalid parameters
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

### **Error Response Format**
```json
{
  "detail": "Error description",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-12-19T10:30:00Z"
}
```

### **Common Error Codes**
- `INVALID_RESEARCH_GOAL`: Empty or invalid research goal
- `INVALID_SEARCH_DEPTH`: Invalid search depth value
- `API_KEY_MISSING`: Required API key not configured
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `RESEARCH_FAILED`: Research execution failed

## 📈 **Rate Limiting**

- **Requests per minute**: 60
- **Concurrent requests**: 10
- **Request timeout**: 300 seconds

## 🔧 **Examples**

### **Quick Research**
```bash
curl -X POST "http://localhost:8001/research" \
  -H "Content-Type: application/json" \
  -d '{
    "research_goal": "Find AI companies in healthcare",
    "search_depth": "quick"
  }'
```

### **Comprehensive Research**
```bash
curl -X POST "http://localhost:8001/research" \
  -H "Content-Type: application/json" \
  -d '{
    "research_goal": "Find companies using blockchain for supply chain",
    "search_depth": "comprehensive",
    "max_iterations": 3,
    "confidence_threshold": 0.9
  }'
```

### **Streaming Research with JavaScript**
```javascript
const response = await fetch('http://localhost:8001/research/stream', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    research_goal: 'Find fintech companies using AI for fraud detection',
    search_depth: 'standard',
    max_iterations: 2
  })
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  const chunk = decoder.decode(value);
  const lines = chunk.split('\n');
  
  for (const line of lines) {
    if (line.startsWith('data: ')) {
      const data = JSON.parse(line.slice(6));
      console.log(data);
    }
  }
}
```

## 📚 **SDK Examples**

### **Python**
```python
import requests

response = requests.post('http://localhost:8001/research', json={
    'research_goal': 'Find AI companies in fintech',
    'search_depth': 'standard',
    'max_iterations': 2
})

results = response.json()
print(f"Found {results['total_companies']} companies")
```

### **JavaScript/Node.js**
```javascript
const axios = require('axios');

const response = await axios.post('http://localhost:8001/research', {
    research_goal: 'Find AI companies in fintech',
    search_depth: 'standard',
    max_iterations: 2
});

console.log(`Found ${response.data.total_companies} companies`);
```

---

**📖 Next**: [Streaming API Guide](streaming-api.md) for real-time updates 