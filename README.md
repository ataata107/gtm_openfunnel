# 🚀 GTM Research System

A sophisticated **Go-To-Market (GTM) research system** built with **LangGraph** and **Large Language Models** to automatically discover, analyze, and evaluate companies based on specific research goals.

## 🎯 **What It Does**

This system automatically:
- 🔍 **Discovers companies** relevant to your research goal
- 📊 **Analyzes evidence** from multiple sources (web search, company websites)
- 🧠 **Evaluates quality** using AI-powered assessment
- 🔄 **Refines strategies** based on gaps and quality metrics
- 📈 **Provides insights** with confidence scores and recommendations

## 🏗️ **Architecture**

### **Core Components:**
- **LangGraph Workflow**: Multi-agent orchestration
- **LLM Agents**: Specialized AI agents for different tasks
- **External APIs**: Serper (Google Search), FireCrawl (Web Scraping)
- **Quality Analysis**: Automated research quality assessment
- **Strategy Refinement**: Dynamic query generation and optimization
- **REST API**: FastAPI-based REST endpoints for integration

### **Agent Pipeline:**
```
Query Agent → Company Aggregator → Multi-Source Search → 
Website Scraper → Evaluator → Quality Evaluator → Strategy Refinement
```

## 🚀 **Quick Start**

### **1. Setup Environment**
```bash
# Clone the repository
git clone <your-repo-url>
cd OpenFunnel

# Create virtual environment
python -m venv openfunnel
source openfunnel/bin/activate  # On Windows: openfunnel\Scripts\activate

# Install dependencies
pip install -r gtm-langgraph/requirements.txt
```

### **2. Configure API Keys**
Create a `.env` file in the root directory:
```env
OPENAI_API_KEY=your_openai_api_key
SERPER_API_KEY=your_serper_api_key
FIRECRAWL_API_KEY=your_firecrawl_api_key
```

### **3. Run the System**

#### **Option A: Direct Execution**
```bash
cd gtm-langgraph
python main.py
```

#### **Option B: REST API Server**
```bash
cd gtm-langgraph
python server.py
```

The API server will be available at:
- **API Server**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🌐 **REST API**

### **Quick API Test**
```bash
# Test the API
python test_api_simple.py

# Or use curl
curl -X POST "http://localhost:8000/research/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "research_goal": "Find fintech companies using AI for fraud detection",
    "search_depth": "comprehensive",
    "max_parallel_searches": 20,
    "confidence_threshold": 0.8
  }'
```

### **API Endpoints**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `POST /research/batch` | POST | Start a new research batch |
| `GET /research/{id}` | GET | Get research results |
| `GET /research/{id}/status` | GET | Get research status |
| `GET /research` | GET | List all research sessions |
| `DELETE /research/{id}` | DELETE | Delete research session |
| `GET /health` | GET | Health check |

### **Example Request/Response**

**Request:**
```json
{
    "research_goal": "Find fintech companies using AI for fraud detection",
    "search_depth": "comprehensive",
    "max_parallel_searches": 20,
    "confidence_threshold": 0.8
}
```

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
            }
        }
    ],
    "search_performance": {
        "queries_per_second": 65,
        "cache_hit_rate": 0.34,
        "failed_requests": 12
    }
}
```

For detailed API documentation, see [API_README.md](API_README.md).

## 📊 **Example Output**

The system generates comprehensive research findings:

- **Company Discovery**: 13+ companies found
- **Quality Scores**: 84% coverage and quality
- **Evidence Analysis**: Multiple sources per company
- **Strategy Refinement**: 5 refined strategies with 20+ queries

## 🛠️ **Key Features**

### **🤖 Intelligent Agents**
- **Query Agent**: Generates diverse search strategies
- **Company Aggregator**: Extracts companies from search results
- **Multi-Source Search**: Performs targeted web searches
- **Website Scraper**: Extracts relevant content from company sites
- **Evaluator**: Assesses evidence against research goals
- **Quality Evaluator**: Analyzes research coverage and quality
- **Strategy Refinement**: Generates improved search strategies

### **📈 Performance Optimization**
- **Async Processing**: Parallel API calls and LLM operations
- **Rate Limiting**: Smart handling of API limits
- **Error Recovery**: Graceful handling of failures
- **Memory Management**: Efficient processing of large datasets

### **🎯 Quality Assurance**
- **Coverage Analysis**: Identifies research gaps
- **Quality Metrics**: Scores evidence reliability
- **Gap Identification**: Finds missing information
- **Strategy Refinement**: Improves search effectiveness

### **🌐 REST API Features**
- **Background Processing**: Non-blocking research execution
- **Real-time Status**: Progress monitoring and status updates
- **Session Management**: Research session tracking
- **Performance Metrics**: Comprehensive analytics
- **Interactive Documentation**: Auto-generated API docs

## 📁 **Project Structure**

```
OpenFunnel/
├── gtm-langgraph/
│   ├── agents/           # AI agent implementations
│   ├── graph/           # LangGraph workflow definition
│   ├── utils/           # Utility functions
│   ├── app/             # API endpoints
│   ├── prompts/         # LLM prompts
│   ├── server.py        # API server startup
│   ├── test_api.py      # API test client
│   ├── test_api_simple.py # Simple API test
│   └── API_README.md    # Detailed API documentation
```

## 🧪 **Testing**

### **Test the Core System**
```bash
python main.py
```

### **Test the API**
```bash
# Start the server
python server.py

# In another terminal, test the API
python test_api_simple.py
```

### **Interactive API Testing**
Visit http://localhost:8000/docs for interactive API documentation and testing.

## 📈 **Performance Metrics**

The system achieves impressive performance:

- **Processing Speed**: Sub-30 second response times
- **Parallel Processing**: 50+ companies simultaneously
- **Search Throughput**: 65+ queries per second
- **Quality Scores**: 85%+ confidence thresholds
- **Coverage**: Comprehensive multi-source analysis

## 🔧 **Configuration**

### **Search Depth Options**
- **quick**: Fast search with minimal depth
- **standard**: Balanced search depth and speed
- **comprehensive**: Deep search with maximum coverage

### **Performance Tuning**
- **max_parallel_searches**: Control concurrent operations
- **confidence_threshold**: Set quality requirements
- **max_iterations**: Limit research cycles

## 🚀 **Deployment**

### **Development**
```bash
python server.py
```

### **Production**
```bash
# Use gunicorn for production
gunicorn app.api:app -w 4 -k uvicorn.workers.UvicornWorker

# Or use uvicorn directly
uvicorn app.api:app --host 0.0.0.0 --port 8000
```

## 📚 **Documentation**

- **[API Documentation](API_README.md)**: Complete REST API guide
- **[Agent Documentation](agents/)**: Individual agent implementations
- **[Graph Documentation](graph/)**: LangGraph workflow details

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Built with ❤️ using LangGraph, LangChain, and OpenAI** 
