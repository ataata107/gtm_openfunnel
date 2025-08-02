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
```bash
cd gtm-langgraph
python main.py
```

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

## 📁 **Project Structure**

```
OpenFunnel/
├── gtm-langgraph/
│   ├── agents/           # AI agent implementations
│   ├── graph/           # LangGraph workflow definition
│   ├── utils/           # Utility functions
│   ├── app/             # API endpoints
│   ├── prompts/         # LLM prompts
│   ├── main.py          # Main execution script
│   └── requirements.txt # Python dependencies
├── tests/               # Test files
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## 🔧 **Configuration**

### **Environment Variables**
- `OPENAI_API_KEY`: OpenAI API key for LLM operations
- `SERPER_API_KEY`: Serper API key for web search
- `FIRECRAWL_API_KEY`: FireCrawl API key for web scraping

### **Performance Settings**
- `max_parallel_searches`: Number of concurrent API calls
- `max_iterations`: Maximum research iterations
- `quality_thresholds`: Coverage and quality score thresholds

## 📊 **Output Files**

The system generates several debug files:
- `debug_output/extracted_companies.json`: Discovered companies
- `debug_output/serper_search_output.json`: Search results
- `debug_output/final_findings.json`: Company evaluations
- `debug_output/quality_analysis.json`: Quality metrics
- `debug_output/strategy_refinement.json`: Refined strategies

## 🧪 **Testing**

```bash
# Run tests
cd tests
python test_*.py
```

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 **Acknowledgments**

- **LangGraph**: Multi-agent workflow orchestration
- **OpenAI**: LLM capabilities
- **Serper**: Web search API
- **FireCrawl**: Web scraping API

---

**Built with ❤️ for automated GTM research** 