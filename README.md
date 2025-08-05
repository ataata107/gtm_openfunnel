# 🚀 GTM Intelligence System

A sophisticated **Go-To-Market (GTM) research system** with **real-time streaming** and **multi-agent orchestration** to automatically discover, analyze, and evaluate companies based on specific research goals.

## 🎯 **What It Does**

This system automatically:
- 🔍 **Discovers companies** relevant to your research goal using Serper search API
- 📰 **Extracts companies from news articles** using Playwright browser automation
- 📊 **Analyzes evidence** from multiple sources (web search, news sites, company websites)
- 🧠 **Evaluates quality** using AI-powered assessment with confidence scores
- 🔄 **Refines strategies** based on gaps and quality metrics (iterative research)
- 📈 **Provides insights** with confidence scores and recommendations
- ⚡ **Real-time streaming** of agent logs and progress via Server-Sent Events
- 🎨 **Modern React UI** for interactive research with configurable parameters
- 💾 **Smart caching** with in-memory and Redis support for performance optimization

## 🏗️ **Architecture**

### **Core Components:**
- **LangGraph Workflow**: Multi-agent orchestration with feedback loops
- **LLM Agents**: Specialized AI agents for different tasks
- **External APIs**: Serper (Google Search + News), FireCrawl (Web Scraping)
- **Browser Automation**: Playwright for automatic news site browsing
- **Real-time Streaming**: Server-Sent Events for live progress updates
- **React Frontend**: Modern UI with real-time log streaming
- **REST API**: FastAPI with streaming and synchronous endpoints

### **Agent Pipeline:**

![GTM Intelligence Workflow](gtm_graph.png)

```
Query Agent → Company Aggregator (Serper + News) → Multi-Source Search → 
Quality Evaluator → (Feedback Loop with max_iterations)
```

### **Key Features:**
- **🔍 Direct LLM Tool Integration**: Agents use LLM with bound Serper tools for direct extraction
- **📰 Parallel News Extraction**: Playwright-based news scraping runs alongside Serper searches
- **🔄 Iterative Research**: Configurable max_iterations for refinement cycles
- **💾 Smart Caching**: In-memory caching with Redis fallback for performance
- **⚡ Real-time Streaming**: Server-Sent Events for live progress updates

## 🚀 **Quick Start**

### **1. Setup Environment**
```bash
# Clone the repository
git clone https://github.com/ataata107/gtm_openfunnel.git
cd OpenFunnel/gtm-langgraph

# Create virtual environment
python -m venv openfunnel
source openfunnel/bin/activate  # On Windows: openfunnel\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### **2. Configure API Keys**
Create a `.env` file in the root directory:
```env
OPENAI_API_KEY=your_openai_api_key
SERPER_API_KEY=your_serper_api_key
FIRECRAWL_API_KEY=your_firecrawl_api_key
```

### **3. Install Playwright (for news agent)**
```bash
# Install Playwright browser
playwright install chromium
```

### **4. Run the System**

#### **Option A: API Server + React Frontend**
```bash
# Terminal 1: Start API Server
source openfunnel/bin/activate
python -m uvicorn app.simple_api:app --host 0.0.0.0 --port 8001

# Terminal 2: Start React Frontend
cd frontend
npm install
npm start
```

Visit `http://localhost:3000` for the interactive UI!

#### **Option B: Direct Execution**
```bash
python main.py
```

## 🌐 **API Endpoints**

### **Synchronous Research**
```bash
curl -X POST "http://localhost:8001/research" \
  -H "Content-Type: application/json" \
  -d '{
    "research_goal": "Find fintech companies using AI for fraud detection",
    "search_depth": "quick",
    "max_parallel_searches": 100,
    "confidence_threshold": 0.8
  }'
```

### **Real-time Streaming Research**
```bash
curl -X POST "http://localhost:8001/research/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "research_goal": "Find fintech companies using AI for fraud detection",
    "search_depth": "quick",
    "max_iterations": 1
  }'
```

### **Health Check**
```bash
curl http://localhost:8001/health
```

## 🎨 **React Frontend**

### **Features:**
- ✅ **Real-time streaming** of agent logs via Server-Sent Events
- ✅ **Interactive research configuration** with all parameters
- ✅ **Live progress updates** with detailed agent logs
- ✅ **Results visualization** with confidence scores
- ✅ **Search depth controls** (quick/standard/comprehensive)
- ✅ **Max iterations configuration** (1-10 refinement cycles)
- ✅ **Streaming vs Regular mode toggle**
- ✅ **Smart caching** for improved performance

### **Usage:**
1. Navigate to `http://localhost:3000`
2. Enter your research goal
3. Select search depth (quick/standard/comprehensive)
4. Choose streaming mode for real-time logs
5. Click "🚀 Start Research"
6. Watch real-time agent progress!

## 📊 **Example Output**

### **Real-time Streaming Logs:**
```
🚀 Starting GTM Research (Streaming Mode)...
📋 Research Goal: Find fintech companies using AI for fraud detection
🔍 Search Depth: quick
🔄 Max Iterations: 1
⏳ Connecting to API stream...

🔍 QUERY AGENT: Starting search strategy generation...
🎯 QUERY AGENT: Generating 10 focused search strategies
🔍 COMPANY AGGREGATOR: Targeting 10 results per search, 10 companies per query, 50 companies max
📰 NEWS EXTRACTOR: Using quick search depth
🔍 Running Serper and News extraction in parallel...
✅ Research completed!
```

### **Final Results:**
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

## 🛠️ **Key Features**

### **🤖 Intelligent Agents**
- **Query Agent**: Generates diverse search strategies with quality feedback integration
- **Company Aggregator**: Extracts companies from Serper search + Playwright news scraping
- **Multi-Source Search**: Performs targeted web searches with direct LLM tool integration
- **News Extractor**: Uses Playwright to automatically browse news sites and extract companies
- **Quality Evaluator**: Analyzes research coverage and quality with detailed metrics

### **⚡ Real-time Streaming**
- **Live Agent Logs**: See agent progress in real-time
- **Server-Sent Events**: Efficient streaming protocol
- **React Integration**: Modern UI with live updates
- **Progress Tracking**: Real-time status updates

### **📈 Performance Optimization**
- **Async Processing**: Parallel API calls and LLM operations
- **Browser Automation**: Playwright for automatic news site browsing
- **Smart Caching**: In-memory caching with Redis fallback
- **Rate Limiting**: Smart handling of API limits
- **Error Recovery**: Graceful handling of failures
- **Memory Management**: Efficient processing of large datasets
- **Streaming Optimization**: Server-Sent Events for real-time updates

### **🎯 Quality Assurance**
- **Coverage Analysis**: Identifies research gaps
- **Quality Metrics**: Scores evidence reliability
- **Gap Identification**: Finds missing information
- **Strategy Refinement**: Improves search effectiveness

## 📁 **Project Structure**

```
gtm-langgraph/
├── agents/              # AI agent implementations
│   ├── query_agent.py
│   ├── company_aggregator_agent.py
│   ├── multi_source_search_agent.py
│   ├── news_search_agent.py      # Serper news API integration
│   ├── news_extractor_agent.py   # Playwright browser automation
│   ├── website_scraper_agent.py
│   ├── evaluator_agent.py
│   └── quality_evaluator_agent.py
├── graph/              # LangGraph workflow
│   ├── gtm_graph.py
│   └── state.py
├── app/                # API endpoints
│   └── simple_api.py   # FastAPI with streaming
├── frontend/           # React application
│   ├── src/
│   │   ├── App.js
│   │   └── components/
│   └── package.json
├── utils/              # Utility functions
├── tests/              # Test files
├── prompts/            # LLM prompts
├── main.py            # Direct execution
└── requirements.txt    # Dependencies
```

## 🧪 **Testing**

### **Test the Core System**
```bash
python main.py
```

### **Test the API**
```bash
# Start the server
python app/simple_api.py

# Test with curl
curl -X POST "http://localhost:8001/research" \
  -H "Content-Type: application/json" \
  -d '{"research_goal": "Find AI companies", "search_depth": "quick"}'
```

### **Test the React Frontend**
```bash
cd frontend
npm start
# Visit http://localhost:3000
```

## 📈 **Performance Metrics**

- **Processing Speed**: Sub-30 second response times
- **Parallel Processing**: 50+ companies simultaneously
- **Search Throughput**: 65+ queries per second
- **Quality Scores**: 85%+ confidence thresholds
- **Real-time Streaming**: Live agent progress updates

## 🔧 **Configuration**

### **Search Depth Options**
- **quick**: Fast search with minimal depth (~50 companies)
- **standard**: Balanced search depth and speed (~100 companies)
- **comprehensive**: Deep search with maximum coverage (~200 companies)

### **API Parameters**
- **max_parallel_searches**: Control concurrent operations (default: 100)
- **confidence_threshold**: Set quality requirements (default: 0.8)
- **max_iterations**: Limit research cycles (default: 1, range: 1-10)
- **search_depth**: Control research depth (quick/standard/comprehensive)

## 🚀 **Deployment**

### **Development**
```bash
# API Server
python app/simple_api.py

# React Frontend
cd frontend && npm start
```

### **Production**
```bash
# API Server
uvicorn app.simple_api:app --host 0.0.0.0 --port 8001

# React Frontend
cd frontend && npm run build
```

## 📚 **Documentation**

- **[📖 Documentation Index](docs/README.md)**: Complete documentation guide
- **[🚀 Quick Start Guide](docs/quick-start.md)**: Get started in 5 minutes
- **[🌐 API Reference](docs/api/rest-api.md)**: Complete REST API documentation
- **[🏗️ Architecture Guide](docs/architecture.md)**: System design and workflow

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests to the `tests/` folder
5. Submit a pull request

## 📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Built with ❤️ using LangGraph, LangChain, OpenAI, FastAPI, React, and Playwright**

## 🆕 **Recent Updates**

### **v1.0.0 (Aug 2025)**
- ✅ **Max Iterations Parameter**: Configurable research refinement cycles (1-10)
- ✅ **Enhanced Caching**: In-memory caching with Redis fallback
- ✅ **Parallel News Extraction**: Playwright-based news scraping alongside Serper searches
- ✅ **Direct LLM Tool Integration**: Agents use bound Serper tools for direct extraction
- ✅ **Improved Streaming**: Server-Sent Events with proper JSON buffering
- ✅ **Comprehensive Documentation**: Complete docs structure with examples
- ✅ **Performance Optimization**: Reduced LLM invocation times and memory usage 
