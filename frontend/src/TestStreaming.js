import React, { useState } from 'react';

function TestStreaming() {
  const [logs, setLogs] = useState('');
  const [results, setResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const startTestStreaming = async () => {
    try {
      setIsLoading(true);
      setLogs('');
      setResults(null);
      setError('');

      setLogs(prev => prev + '🧪 Starting Test Streaming...\n');
      setLogs(prev => prev + '⏳ Connecting to test API...\n\n');

      const response = await fetch('http://localhost:8002/test/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      setLogs(prev => prev + '✅ Connected to test API\n');
      setLogs(prev => prev + '📡 Receiving test logs...\n\n');

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          setLogs(prev => prev + '✅ Stream completed\n');
          break;
        }

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              switch (data.type) {
                case 'status':
                  setLogs(prev => prev + `📊 ${data.message}\n`);
                  break;
                
                case 'log':
                  setLogs(prev => prev + `${data.message}\n`);
                  break;
                
                case 'results':
                  setLogs(prev => prev + '✅ Test completed!\n');
                  setLogs(prev => prev + `📊 Companies Found: ${data.data.companies_found}\n`);
                  setLogs(prev => prev + `🔍 Strategies Used: ${data.data.strategies_used}\n`);
                  setLogs(prev => prev + '🎉 Test Completed Successfully!\n\n');
                  
                  setResults(data.data);
                  break;
                
                case 'complete':
                  setLogs(prev => prev + `✅ ${data.message}\n`);
                  break;
                
                case 'error':
                  setError(data.message);
                  setLogs(prev => prev + `❌ ${data.message}\n`);
                  break;
                
                default:
                  setLogs(prev => prev + `📡 ${JSON.stringify(data)}\n`);
              }
            } catch (parseError) {
              setLogs(prev => prev + `⚠️ Error parsing stream data: ${parseError.message}\n`);
            }
          }
        }
      }

    } catch (err) {
      setError(err.message);
      setLogs(prev => prev + `❌ Failed to start streaming: ${err.message}\n`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>🧪 Test Streaming API</h1>
      <p>This tests the streaming functionality with simulated agent work.</p>
      
      <button 
        onClick={startTestStreaming}
        disabled={isLoading}
        style={{
          padding: '10px 20px',
          fontSize: '16px',
          backgroundColor: isLoading ? '#ccc' : '#007bff',
          color: 'white',
          border: 'none',
          borderRadius: '5px',
          cursor: isLoading ? 'not-allowed' : 'pointer'
        }}
      >
        {isLoading ? '🔄 Testing...' : '🚀 Start Test Streaming'}
      </button>

      {logs && (
        <div style={{ marginTop: '20px' }}>
          <h2>📋 Test Logs {isLoading && <span style={{color: 'green'}}>Live</span>}</h2>
          <pre style={{
            backgroundColor: '#f8f9fa',
            padding: '15px',
            borderRadius: '5px',
            border: '1px solid #dee2e6',
            maxHeight: '400px',
            overflow: 'auto',
            whiteSpace: 'pre-wrap',
            fontFamily: 'monospace',
            fontSize: '14px'
          }}>
            {logs}
          </pre>
        </div>
      )}

      {error && (
        <div style={{ marginTop: '20px' }}>
          <h2>❌ Error</h2>
          <div style={{ color: 'red', padding: '10px', backgroundColor: '#f8d7da', borderRadius: '5px' }}>
            {error}
          </div>
        </div>
      )}

      {results && (
        <div style={{ marginTop: '20px' }}>
          <h2>📊 Test Results</h2>
          <div style={{ padding: '15px', backgroundColor: '#d4edda', borderRadius: '5px', border: '1px solid #c3e6cb' }}>
            <p><strong>Status:</strong> {results.status}</p>
            <p><strong>Companies Found:</strong> {results.companies_found}</p>
            <p><strong>Strategies Used:</strong> {results.strategies_used}</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default TestStreaming; 