# 🚀 GTM Intelligence Streaming Guide

This guide explains how to use the real-time streaming functionality to see logs and results as they happen.

## 📡 Streaming Features

### **Real-time Logs**
- See research progress in real-time
- Watch as each agent processes data
- Monitor search strategies being generated
- Track company extraction progress

### **Live Results**
- Get results as soon as they're available
- No need to wait for the entire process to complete
- See quality metrics as they're calculated

## 🔧 How to Use Streaming

### **1. Start the API Server**
```bash
# Activate virtual environment
source openfunnel/bin/activate

# Start the API server
python app/simple_api.py
```

The server will run on `http://localhost:8001`

### **2. Start the React App**
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (if not done already)
npm install

# Start the React app
npm start
```

The React app will run on `http://localhost:3000`

### **3. Use Streaming Mode**

1. **Open the React app** in your browser
2. **Enter your research goal** (e.g., "Find fintech companies using AI for fraud detection")
3. **Select search depth** (quick/standard/comprehensive)
4. **Enable "Use Real-time Streaming Mode"** checkbox
5. **Click "Start Research"**

### **4. Watch Real-time Progress**

You'll see:
- ✅ Connection status
- 📊 Research progress updates
- 🏢 Companies being found
- 📈 Quality metrics
- 🎉 Final results

## 🔄 API Endpoints

### **Streaming Endpoint**
```
POST /research/stream
```

**Request Body:**
```json
{
  "research_goal": "Find fintech companies using AI for fraud detection",
  "search_depth": "quick",
  "max_parallel_searches": 100,
  "confidence_threshold": 0.8,
  "max_iterations": 1
}
```

**Response:** Server-Sent Events (SSE) stream with real-time updates

### **Regular Endpoint**
```
POST /research
```

**Response:** Synchronous JSON response with final results

## 📊 Stream Data Types

### **Status Updates**
```json
{
  "type": "status",
  "message": "Starting research...",
  "timestamp": "2024-01-15T10:30:00"
}
```

### **Results**
```json
{
  "type": "results",
  "data": {
    "research_goal": "...",
    "total_companies": 38,
    "processing_time_ms": 87650,
    "quality_metrics": {...},
    "results": [...]
  }
}
```

### **Completion**
```json
{
  "type": "complete",
  "message": "Research completed successfully",
  "timestamp": "2024-01-15T10:31:30"
}
```

### **Errors**
```json
{
  "type": "error",
  "message": "Research failed: ...",
  "timestamp": "2024-01-15T10:30:15"
}
```

## 🧪 Testing the Streaming

### **Test with Python Script**
```bash
# Run the test script
python test_streaming.py
```

### **Test with curl**
```bash
# Test streaming endpoint
curl -X POST "http://localhost:8001/research/stream" \
  -H "Content-Type: application/json" \
  -d '{"research_goal": "Find fintech companies using AI for fraud detection", "search_depth": "quick"}' \
  --no-buffer
```

### **Test with JavaScript**
```javascript
// In browser console
fetch('http://localhost:8001/research/stream', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    research_goal: "Find fintech companies using AI for fraud detection",
    search_depth: "quick"
  })
})
.then(response => {
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  
  function readStream() {
    return reader.read().then(({done, value}) => {
      if (done) return;
      
      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');
      
      lines.forEach(line => {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6));
            console.log('📡', data);
          } catch (e) {
            console.log('Raw:', line);
          }
        }
      });
      
      return readStream();
    });
  }
  
  return readStream();
});
```

## 🎯 Benefits of Streaming

### **1. Real-time Feedback**
- See progress as it happens
- Know exactly what's happening in each step
- Identify bottlenecks quickly

### **2. Better User Experience**
- No more waiting in silence
- Users can see the system is working
- Can stop long-running processes if needed

### **3. Debugging**
- Easy to see where issues occur
- Real-time error reporting
- Step-by-step progress tracking

### **4. Performance Monitoring**
- Track processing time for each step
- Monitor resource usage
- Identify optimization opportunities

## 🔧 Troubleshooting

### **Connection Issues**
- Make sure API server is running on port 8001
- Check CORS settings if using from different domain
- Verify network connectivity

### **Stream Not Working**
- Check browser console for errors
- Verify EventSource support in browser
- Try the regular endpoint as fallback

### **Performance Issues**
- Reduce `max_parallel_searches` for slower systems
- Use "quick" search depth for faster results
- Monitor memory usage during long runs

## 🚀 Next Steps

1. **Start the API server** and React app
2. **Test with a simple research goal**
3. **Watch the real-time logs**
4. **Try different search depths**
5. **Experiment with different research goals**

The streaming functionality provides a much better user experience by showing real-time progress instead of waiting for the entire process to complete! 