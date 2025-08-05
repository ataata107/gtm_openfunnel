# 🚀 Quick Start Guide

Get the GTM Intelligence System up and running in **5 minutes**!

## 📋 **Prerequisites**

- Python 3.8+
- Node.js 16+
- Git

## ⚡ **5-Minute Setup**

### **1. Clone & Setup (1 minute)**
```bash
git clone https://github.com/your-repo/gtm-langgraph.git
cd gtm-langgraph

# Create virtual environment
python -m venv openfunnel
source openfunnel/bin/activate  # On Windows: openfunnel\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### **2. Configure API Keys (1 minute)**
Create `.env` file in the root directory:
```env
OPENAI_API_KEY=your_openai_api_key
SERPER_API_KEY=your_serper_api_key
```

### **3. Install Playwright (1 minute)**
```bash
playwright install chromium
```

### **4. Start the System (2 minutes)**
```bash
# Terminal 1: Start API Server
source openfunnel/bin/activate
python -m uvicorn app.simple_api:app --host 0.0.0.0 --port 8001

# Terminal 2: Start React Frontend
cd frontend
npm install
npm start
```

### **5. Start Research!**
1. Open `http://localhost:3000`
2. Enter research goal: "Find fintech companies using AI for fraud detection"
3. Select search depth: "Quick"
4. Set max iterations: 1
5. Click "🚀 Start Research"
6. Watch real-time progress!

## 🎯 **Your First Research**

### **Example Research Goal**
```
Find companies using AI for customer service automation
```

### **Expected Results**
- **Companies Found**: 50-100 companies
- **Processing Time**: 30-60 seconds
- **Quality Score**: 0.75+ (out of 1.0)
- **Real-time Logs**: Live agent progress

### **Sample Output**
```
🚀 Starting GTM Research (Streaming Mode)...
📋 Research Goal: Find companies using AI for customer service automation
🔍 Search Depth: quick
🔄 Max Iterations: 1
⏳ Connecting to API stream...

🔍 QUERY AGENT: Starting search strategy generation...
🎯 QUERY AGENT: Generating 10 focused search strategies
🔍 COMPANY AGGREGATOR: Targeting 10 results per search, 10 companies per query, 50 companies max
📰 NEWS EXTRACTOR: Using quick search depth
🔍 Running Serper and News extraction in parallel...
✅ Research completed!
📊 Processing Time: 45230ms
🏢 Companies Found: 67
🔍 Search Strategies: 10
🔄 Iterations Used: 1
📈 Quality Score: 0.82
📈 Coverage Score: 0.78
```

## 🔧 **Configuration Options**

### **Search Depth**
- **Quick**: 5 strategies, ~50 companies (fastest)
- **Standard**: 10 strategies, ~100 companies (balanced)
- **Comprehensive**: 15 strategies, ~200 companies (thorough)

### **Max Iterations**
- **1**: Single research pass (default)
- **2-5**: Multiple refinement cycles
- **6-10**: Deep iterative analysis

### **Streaming Mode**
- **✅ Enabled**: Real-time logs and progress
- **❌ Disabled**: Synchronous mode (faster results)

## 🚨 **Troubleshooting**

### **Common Issues**

**API Key Errors**
```bash
# Check your .env file
cat .env
# Should contain: OPENAI_API_KEY=sk-... and SERPER_API_KEY=...
```

**Port Already in Use**
```bash
# Kill existing process
lsof -i :8001
kill -9 <PID>
```

**Playwright Issues**
```bash
# Reinstall Playwright
playwright install chromium
```

**Frontend Build Errors**
```bash
# Clear npm cache
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

## 📚 **Next Steps**

1. **Read the [Architecture Guide](architecture.md)** to understand the system
2. **Explore [API Documentation](api/rest-api.md)** for programmatic access
3. **Try [Advanced Examples](examples/research-examples.md)** for complex research
4. **Check [Performance Guide](performance/guide.md)** for optimization tips

## 🆘 **Need Help?**

- **Documentation**: [Full Documentation Index](README.md)
- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Examples**: [Research Examples](examples/research-examples.md)

---

**🎉 Congratulations!** You're now ready to conduct sophisticated GTM research with AI-powered multi-agent analysis! 