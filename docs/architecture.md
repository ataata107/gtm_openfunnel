# 🏗️ System Architecture

Comprehensive overview of the GTM Intelligence System architecture, components, and data flow.

## 🎯 **System Overview**

The GTM Intelligence System is a sophisticated **multi-agent research platform** that combines **LangGraph orchestration**, **LLM-powered agents**, **real-time streaming**, and **modern web technologies** to automatically discover and analyze companies based on research goals.

## 🏗️ **High-Level Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React UI      │    │   FastAPI       │    │   LangGraph     │
│   (Frontend)    │◄──►│   (Backend)     │◄──►│   (Orchestration)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Browser       │    │   External      │    │   LLM Agents    │
│   (Playwright)  │    │   APIs          │    │   (OpenAI)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔧 **Core Components**

### **1. Frontend Layer**
- **React Application**: Modern UI with real-time streaming
- **Server-Sent Events**: Live progress updates
- **State Management**: React hooks for UI state
- **Component Library**: Reusable UI components

### **2. API Layer**
- **FastAPI**: High-performance REST API
- **Streaming Endpoints**: Server-Sent Events for real-time updates
- **Request Validation**: Pydantic models for data validation
- **Error Handling**: Comprehensive error management

### **3. Orchestration Layer**
- **LangGraph**: Multi-agent workflow orchestration
- **State Management**: Centralized state handling
- **Agent Coordination**: Inter-agent communication
- **Feedback Loops**: Iterative research refinement

### **4. Agent Layer**
- **Query Agent**: Search strategy generation
- **Company Aggregator**: Company discovery and extraction
- **Multi-Source Search**: Evidence gathering and evaluation
- **News Extractor**: Playwright-based news analysis
- **Quality Evaluator**: Research quality assessment

### **5. External Services**
- **OpenAI API**: LLM-powered intelligence
- **Serper API**: Web search and news search
- **Playwright**: Browser automation for news scraping
- **Caching Layer**: In-memory and Redis caching

## 🔄 **Data Flow**

### **1. Research Initiation**
```
User Input → React UI → FastAPI → LangGraph → Agent Pipeline
```

### **2. Agent Pipeline**
```
Query Agent → Company Aggregator → Multi-Source Search → Quality Evaluator
     ↓              ↓                    ↓                    ↓
Search Strategies → Company Discovery → Evidence Gathering → Quality Assessment
```

### **3. Real-time Streaming**
```
Agent Logs → LangGraph → FastAPI → Server-Sent Events → React UI
```

### **4. Results Processing**
```
Quality Metrics → State Updates → Final Results → JSON Response
```

## 🤖 **Agent Architecture**

### **Query Agent**
```python
# Purpose: Generate diverse search strategies
# Input: Research goal, quality metrics (optional)
# Output: List of search strategies
# Tools: OpenAI GPT-4 with structured output
```

### **Company Aggregator**
```python
# Purpose: Extract companies from multiple sources
# Input: Search strategies, research goal
# Output: List of unique companies
# Tools: Serper API, Playwright, OpenAI GPT-4
```

### **Multi-Source Search**
```python
# Purpose: Gather and evaluate evidence
# Input: Company list, research goal
# Output: Company findings with confidence scores
# Tools: Serper API, OpenAI GPT-4 with bound tools
```

### **News Extractor**
```python
# Purpose: Extract companies from news articles
# Input: Search queries, research goal
# Output: Companies from news sources
# Tools: Serper News API, Playwright browser automation
```

### **Quality Evaluator**
```python
# Purpose: Assess research quality and coverage
# Input: Research results, quality metrics
# Output: Quality analysis and recommendations
# Tools: OpenAI GPT-4 with parallel processing
```

## 📊 **State Management**

### **GTMState Schema**
```python
class GTMState(BaseModel):
    research_goal: str
    search_depth: str
    max_iterations: int
    current_iteration: int
    search_strategies_generated: List[str]
    extracted_companies: List[CompanyMeta]
    company_findings: List[CompanyFinding]
    quality_metrics: Optional[dict]
    max_parallel_searches: int
    confidence_threshold: float
```

### **State Transitions**
1. **Initialization**: Research goal and parameters
2. **Strategy Generation**: Search strategies created
3. **Company Discovery**: Companies extracted from multiple sources
4. **Evidence Gathering**: Evidence collected and evaluated
5. **Quality Assessment**: Research quality analyzed
6. **Iteration Check**: Determine if more iterations needed
7. **Final Results**: Complete research results

## ⚡ **Performance Architecture**

### **Parallel Processing**
- **Async Operations**: All I/O operations are asynchronous
- **Concurrent Agents**: Multiple agents run in parallel
- **Parallel Searches**: Multiple search queries executed simultaneously
- **Browser Pooling**: Playwright browser instances are reused

### **Caching Strategy**
- **In-Memory Cache**: Fast access to frequently used data
- **Redis Fallback**: Persistent caching for production
- **Cache Keys**: MD5-hashed keys for consistency
- **TTL Management**: Automatic cache expiration

### **Streaming Optimization**
- **Server-Sent Events**: Efficient real-time communication
- **JSON Buffering**: Proper handling of chunked JSON
- **Error Recovery**: Graceful handling of stream interruptions
- **Memory Management**: Efficient processing of large datasets

## 🔒 **Security & Reliability**

### **API Security**
- **Input Validation**: Pydantic models for request validation
- **Rate Limiting**: Protection against abuse
- **Error Handling**: Comprehensive error management
- **Logging**: Detailed audit trails

### **Data Privacy**
- **No Data Storage**: Results are not persisted
- **Temporary Caching**: Cache expires automatically
- **Secure API Keys**: Environment variable management
- **HTTPS Support**: Secure communication

### **Fault Tolerance**
- **Graceful Degradation**: System continues with partial failures
- **Retry Logic**: Automatic retry for transient failures
- **Fallback Mechanisms**: Alternative approaches when primary fails
- **Error Recovery**: Comprehensive error handling

## 🚀 **Deployment Architecture**

### **Development Environment**
```
┌─────────────────┐    ┌─────────────────┐
│   React Dev     │    │   FastAPI Dev   │
│   (localhost:3000)│    │   (localhost:8001)│
└─────────────────┘    └─────────────────┘
```

### **Production Environment**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx         │    │   Gunicorn      │    │   Redis Cache   │
│   (Load Balancer)│    │   (WSGI Server) │    │   (Optional)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│   React Build   │    │   FastAPI App   │
│   (Static Files)│    │   (Python)      │
└─────────────────┘    └─────────────────┘
```

## 📈 **Scalability Considerations**

### **Horizontal Scaling**
- **Stateless Design**: No server-side state
- **Load Balancing**: Multiple API instances
- **Caching Layer**: Redis for shared state
- **Async Processing**: Non-blocking operations

### **Vertical Scaling**
- **Memory Optimization**: Efficient data structures
- **CPU Optimization**: Parallel processing
- **I/O Optimization**: Async operations
- **Resource Management**: Proper cleanup

## 🔧 **Configuration Management**

### **Environment Variables**
```env
OPENAI_API_KEY=your_openai_api_key
SERPER_API_KEY=your_serper_api_key
FIRECRAWL_API_KEY=your_firecrawl_api_key
REDIS_URL=redis://localhost:6379  # Optional
```

### **Search Depth Configurations**
```python
SEARCH_DEPTH_CONFIGS = {
    "quick": {"strategies": 5, "companies": 50},
    "standard": {"strategies": 10, "companies": 100},
    "comprehensive": {"strategies": 15, "companies": 200}
}
```

### **Performance Tuning**
```python
MAX_PARALLEL_SEARCHES = 100
CONFIDENCE_THRESHOLD = 0.8
MAX_ITERATIONS = 1
CACHE_TTL = 7200  # 2 hours
```

## 📚 **Technology Stack**

### **Backend**
- **Python 3.8+**: Core runtime
- **FastAPI**: High-performance web framework
- **LangGraph**: Multi-agent orchestration
- **LangChain**: LLM integration
- **Pydantic**: Data validation
- **Uvicorn**: ASGI server

### **Frontend**
- **React 18**: Modern UI framework
- **JavaScript ES6+**: Client-side logic
- **CSS3**: Styling and animations
- **Server-Sent Events**: Real-time streaming

### **AI/ML**
- **OpenAI GPT-4**: Large language model
- **Serper API**: Web search and news
- **Playwright**: Browser automation

### **Infrastructure**
- **Redis**: Caching (optional)
- **Nginx**: Load balancing (production)
- **Docker**: Containerization (optional)

---

**📖 Next**: [Agent Pipeline](agent-pipeline.md) for detailed workflow information 