import React, { useState } from 'react';

function SimpleStreamingTest() {
  const [logs, setLogs] = useState('');
  const [debugInfo, setDebugInfo] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const addLog = (message) => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => prev + `[${timestamp}] ${message}\n`);
  };

  const addDebug = (message) => {
    const timestamp = new Date().toLocaleTimeString();
    setDebugInfo(prev => prev + `[${timestamp}] ${message}\n`);
  };

  const startTest = async () => {
    try {
      setIsLoading(true);
      setLogs('');
      setDebugInfo('');
      
      addLog('🧪 Starting streaming test...');
      addDebug('Making fetch request to test API...');

      const response = await fetch('http://localhost:8002/test/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      addDebug(`Response status: ${response.status}`);
      addDebug(`Response headers: ${JSON.stringify(Object.fromEntries(response.headers.entries()))}`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      addLog('✅ Connected to API');
      addDebug('Starting to read response body...');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      let chunkCount = 0;
      let lineCount = 0;

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          addDebug('Stream completed (done = true)');
          break;
        }

        chunkCount++;
        addDebug(`Received chunk #${chunkCount}, size: ${value.length} bytes`);

        const chunk = decoder.decode(value);
        addDebug(`Decoded chunk: "${chunk.replace(/\n/g, '\\n')}"`);

        const lines = chunk.split('\n');
        addDebug(`Split into ${lines.length} lines`);

        for (const line of lines) {
          lineCount++;
          addDebug(`Processing line #${lineCount}: "${line}"`);
          
          if (line.startsWith('data: ')) {
            try {
              const jsonStr = line.slice(6);
              addDebug(`Parsing JSON: "${jsonStr}"`);
              
              const data = JSON.parse(jsonStr);
              addDebug(`Parsed data type: ${data.type}`);
              
              switch (data.type) {
                case 'status':
                  addLog(`📊 Status: ${data.message}`);
                  break;
                
                case 'log':
                  addLog(`📝 Log: ${data.message}`);
                  break;
                
                case 'results':
                  addLog(`✅ Results received`);
                  addLog(`   Companies: ${data.data.companies_found}`);
                  addLog(`   Strategies: ${data.data.strategies_used}`);
                  break;
                
                case 'complete':
                  addLog(`✅ Complete: ${data.message}`);
                  break;
                
                case 'error':
                  addLog(`❌ Error: ${data.message}`);
                  break;
                
                default:
                  addLog(`📡 Unknown type: ${data.type}`);
              }
            } catch (parseError) {
              addLog(`⚠️ JSON parse error: ${parseError.message}`);
              addDebug(`Failed to parse: "${line}"`);
            }
          } else if (line.trim()) {
            addDebug(`Non-data line: "${line}"`);
          }
        }
      }

      addLog('🎉 Test completed!');

    } catch (err) {
      addLog(`❌ Error: ${err.message}`);
      addDebug(`Exception: ${err.stack}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>🔍 Streaming Debug Test</h1>
      <p>This will show exactly what's happening with the streaming.</p>
      
      <button 
        onClick={startTest}
        disabled={isLoading}
        style={{
          padding: '10px 20px',
          fontSize: '16px',
          backgroundColor: isLoading ? '#ccc' : '#007bff',
          color: 'white',
          border: 'none',
          borderRadius: '5px',
          cursor: isLoading ? 'not-allowed' : 'pointer',
          marginBottom: '20px'
        }}
      >
        {isLoading ? '🔄 Testing...' : '🚀 Start Debug Test'}
      </button>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        <div>
          <h2>📋 Application Logs</h2>
          <pre style={{
            backgroundColor: '#f8f9fa',
            padding: '15px',
            borderRadius: '5px',
            border: '1px solid #dee2e6',
            maxHeight: '400px',
            overflow: 'auto',
            whiteSpace: 'pre-wrap',
            fontFamily: 'monospace',
            fontSize: '12px'
          }}>
            {logs || 'No logs yet...'}
          </pre>
        </div>

        <div>
          <h2>🔧 Debug Information</h2>
          <pre style={{
            backgroundColor: '#fff3cd',
            padding: '15px',
            borderRadius: '5px',
            border: '1px solid #ffeaa7',
            maxHeight: '400px',
            overflow: 'auto',
            whiteSpace: 'pre-wrap',
            fontFamily: 'monospace',
            fontSize: '12px'
          }}>
            {debugInfo || 'No debug info yet...'}
          </pre>
        </div>
      </div>
    </div>
  );
}

export default SimpleStreamingTest; 