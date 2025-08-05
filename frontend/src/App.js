import React, { useState, useRef } from 'react';
import axios from 'axios';
import TestStreaming from './TestStreaming';
import './App.css';

function App() {
  const [researchGoal, setResearchGoal] = useState('Find fintech companies using AI for fraud detection');
  const [searchDepth, setSearchDepth] = useState('quick');
  const [maxIterations, setMaxIterations] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [logs, setLogs] = useState('');
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');
  const [streamingMode, setStreamingMode] = useState(true);
  const [selectedCompany, setSelectedCompany] = useState(null);
  const [showEvidenceModal, setShowEvidenceModal] = useState(false);
  const eventSourceRef = useRef(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setLogs('');
    setResults(null);
    setError('');

    if (streamingMode) {
      // Use streaming mode with Server-Sent Events
      await startStreamingResearch();
    } else {
      // Use regular synchronous mode
      await startRegularResearch();
    }
  };

  const startStreamingResearch = async () => {
    try {
      // Add initial log
      setLogs(prev => prev + '🚀 Starting GTM Research (Streaming Mode)...\n');
      setLogs(prev => prev + `📋 Research Goal: ${researchGoal}\n`);
      setLogs(prev => prev + `🔍 Search Depth: ${searchDepth}\n`);
      setLogs(prev => prev + `🔄 Max Iterations: ${maxIterations}\n`);
      setLogs(prev => prev + '⏳ Connecting to API stream...\n\n');

      // First, make a POST request to start the research
      const response = await fetch('http://localhost:8001/research/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          research_goal: researchGoal,
          search_depth: searchDepth,
          max_parallel_searches: 100,
          confidence_threshold: 0.8,
          max_iterations: maxIterations
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Get the response as a stream
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = ''; // Buffer for incomplete data

      setLogs(prev => prev + '✅ Connected to API stream\n');
      setLogs(prev => prev + '📡 Receiving real-time updates...\n\n');

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          setLogs(prev => prev + '✅ Stream completed\n');
          break;
        }

        const chunk = decoder.decode(value);
        buffer += chunk; // Add to buffer
        
        // Process complete lines from buffer
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // Keep incomplete line in buffer

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
                   setLogs(prev => prev + '✅ Research completed!\n');
                   setLogs(prev => prev + `📊 Processing Time: ${data.data.processing_time_ms}ms\n`);
                   setLogs(prev => prev + `🏢 Companies Found: ${data.data.total_companies}\n`);
                   setLogs(prev => prev + `🔍 Search Strategies: ${data.data.search_strategies_generated}\n`);
                   setLogs(prev => prev + `🔄 Iterations Used: ${data.data.iterations_used || 1}\n`);
                   setLogs(prev => prev + `📈 Quality Score: ${data.data.quality_metrics.quality_score.toFixed(2)}\n`);
                   setLogs(prev => prev + `📈 Coverage Score: ${data.data.quality_metrics.coverage_score.toFixed(2)}\n`);
                   setLogs(prev => prev + '🎉 Research Completed Successfully!\n\n');
                   
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
              // Check if it's an incomplete JSON (truncated)
              if (parseError.message.includes('Unterminated string') || 
                  parseError.message.includes('Unexpected end of JSON input')) {
                // Don't log this as an error since it's expected with streaming
              } else {
                setLogs(prev => prev + `⚠️ Error parsing stream data: ${parseError.message}\n`);
              }
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

  const startRegularResearch = async () => {
    // Add initial log
    setLogs(prev => prev + '🚀 Starting GTM Research (Regular Mode)...\n');
    setLogs(prev => prev + `📋 Research Goal: ${researchGoal}\n`);
    setLogs(prev => prev + `🔍 Search Depth: ${searchDepth}\n`);
    setLogs(prev => prev + `🔄 Max Iterations: ${maxIterations}\n`);
    setLogs(prev => prev + '⏳ Sending request to API...\n\n');

    try {
      const response = await axios.post('/research', {
        research_goal: researchGoal,
        search_depth: searchDepth,
        max_parallel_searches: 100,
        confidence_threshold: 0.8,
        max_iterations: maxIterations
      });

      // Add success logs
      setLogs(prev => prev + '✅ API Request Successful!\n');
      setLogs(prev => prev + `📊 Processing Time: ${response.data.processing_time_ms}ms\n`);
      setLogs(prev => prev + `🏢 Companies Found: ${response.data.total_companies}\n`);
      setLogs(prev => prev + `🔍 Search Strategies: ${response.data.search_strategies_generated}\n`);
      setLogs(prev => prev + `🔄 Iterations Used: ${response.data.iterations_used || 1}\n`);
      setLogs(prev => prev + `📈 Quality Score: ${response.data.quality_metrics.quality_score.toFixed(2)}\n`);
      setLogs(prev => prev + `📈 Coverage Score: ${response.data.quality_metrics.coverage_score.toFixed(2)}\n`);
      setLogs(prev => prev + '🎉 Research Completed Successfully!\n\n');

      setResults(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
      setLogs(prev => prev + '❌ API Request Failed!\n');
      setLogs(prev => prev + `Error: ${err.response?.data?.detail || err.message}\n`);
    } finally {
      setIsLoading(false);
    }
  };

  const stopResearch = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }
    setIsLoading(false);
    setLogs(prev => prev + '⏹️ Research stopped by user\n');
  };

  const handleCompanyClick = (company) => {
    setSelectedCompany(company);
    setShowEvidenceModal(true);
  };

  const closeEvidenceModal = () => {
    setShowEvidenceModal(false);
    setSelectedCompany(null);
  };

  return (
    <div className="container">
                    <div className="card">
                <h1>🔍 GTM Intelligence Research</h1>
                <p>Research fintech companies with AI-powered analysis</p>
                <div style={{ marginTop: '10px' }}>
                  <button 
                    onClick={() => window.location.href = '/test'}
                    style={{
                      padding: '8px 16px',
                      fontSize: '14px',
                      backgroundColor: '#28a745',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      marginRight: '10px'
                    }}
                  >
                    🧪 Test Streaming
                  </button>
                  <button 
                    onClick={() => window.location.href = '/debug'}
                    style={{
                      padding: '8px 16px',
                      fontSize: '14px',
                      backgroundColor: '#dc3545',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer'
                    }}
                  >
                    🔍 Debug Streaming
                  </button>
                </div>
              </div>

      <div className="card">
        <h2>📝 Research Configuration</h2>
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '16px' }}>
            <label htmlFor="researchGoal">Research Goal:</label>
            <input
              id="researchGoal"
              type="text"
              className="input"
              value={researchGoal}
              onChange={(e) => setResearchGoal(e.target.value)}
              placeholder="Enter your research goal..."
              disabled={isLoading}
            />
          </div>

          <div style={{ marginBottom: '16px' }}>
            <label htmlFor="searchDepth">Search Depth:</label>
            <select
              id="searchDepth"
              className="select"
              value={searchDepth}
              onChange={(e) => setSearchDepth(e.target.value)}
              disabled={isLoading}
            >
              <option value="quick">Quick (5 strategies, ~50 companies)</option>
              <option value="standard">Standard (10 strategies, ~100 companies)</option>
              <option value="comprehensive">Comprehensive (15 strategies, ~200 companies)</option>
            </select>
          </div>

          <div style={{ marginBottom: '16px' }}>
            <label htmlFor="maxIterations">Max Iterations:</label>
            <input
              id="maxIterations"
              type="number"
              className="input"
              value={maxIterations}
              onChange={(e) => setMaxIterations(parseInt(e.target.value) || 1)}
              min="1"
              max="10"
              disabled={isLoading}
              style={{ width: '100px' }}
            />
            <small style={{ display: 'block', marginTop: '4px', color: '#666' }}>
              Number of research iterations (1-10). Higher values allow for more comprehensive analysis.
            </small>
          </div>

          <div style={{ marginBottom: '16px' }}>
            <label>
              <input
                type="checkbox"
                checked={streamingMode}
                onChange={(e) => setStreamingMode(e.target.checked)}
                disabled={isLoading}
              />
              {' '}Use Real-time Streaming Mode
            </label>
            <small style={{ display: 'block', marginTop: '4px', color: '#666' }}>
              {streamingMode ? '🟢 Real-time logs and progress updates' : '⚡ Regular synchronous mode'}
            </small>
          </div>

          <div style={{ display: 'flex', gap: '12px' }}>
            <button 
              type="submit" 
              className="btn" 
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <span className="loading"></span>
                  {streamingMode ? 'Streaming...' : 'Researching...'}
                </>
              ) : (
                '🚀 Start Research'
              )}
            </button>

            {isLoading && streamingMode && (
              <button 
                type="button" 
                className="btn" 
                onClick={stopResearch}
                style={{ background: 'linear-gradient(135deg, #dc3545 0%, #c82333 100%)' }}
              >
                ⏹️ Stop
              </button>
            )}
          </div>
        </form>
      </div>

      {logs && (
        <div className="card">
          <h2>📋 Research Logs {streamingMode && isLoading && <span className="status loading">Live</span>}</h2>
          <div className="logs">{logs}</div>
        </div>
      )}

      {error && (
        <div className="card">
          <h2>❌ Error</h2>
          <div className="status error">{error}</div>
        </div>
      )}

      {results && (
        <div className="card">
          <h2>📊 Research Results</h2>
          
          <div style={{ marginBottom: '20px' }}>
            <div className="status success">
              ✅ Research Completed Successfully
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' }}>
            <div>
              <h3>📈 Quality Metrics</h3>
              <p><strong>Quality Score:</strong> {results.quality_metrics.quality_score.toFixed(2)}/1.0</p>
              <p><strong>Coverage Score:</strong> {results.quality_metrics.coverage_score.toFixed(2)}/1.0</p>
            </div>
            <div>
              <h3>📊 Performance</h3>
              <p><strong>Processing Time:</strong> {results.processing_time_ms}ms</p>
              <p><strong>Companies Found:</strong> {results.total_companies}</p>
              <p><strong>Search Strategies:</strong> {results.search_strategies_generated}</p>
            </div>
          </div>

          <div>
            <h3>🏢 Companies Found ({results.results.length})</h3>
            <div className="results">
              {results.results.map((company, index) => (
                <div 
                  key={index} 
                  className="company-item"
                  onClick={() => handleCompanyClick(company)}
                  style={{ cursor: 'pointer', transition: 'all 0.2s ease' }}
                  onMouseEnter={(e) => e.target.style.transform = 'scale(1.02)'}
                  onMouseLeave={(e) => e.target.style.transform = 'scale(1)'}
                >
                  <h4>🏢 {company.domain}</h4>
                  <p><strong>Confidence:</strong> {company.confidence_score.toFixed(2)}</p>
                  <p><strong>Evidence Sources:</strong> {company.evidence_sources}</p>
                  <p><strong>Signals Found:</strong> {company.signals_found}</p>
                  <p><strong>Goal Achieved:</strong> {company.findings.goal_achieved ? '✅ Yes' : '❌ No'}</p>
                  {company.findings.technologies && (
                    <p><strong>Technologies:</strong> {company.findings.technologies.join(', ')}</p>
                  )}
                  <small style={{ color: '#666', fontStyle: 'italic' }}>Click to view evidence snippets</small>
                </div>
              ))}
            </div>
          </div>

          {results.quality_metrics.missing_aspects && results.quality_metrics.missing_aspects.length > 0 && (
            <div style={{ marginTop: '20px' }}>
              <h3>🔍 Missing Aspects</h3>
              <ul>
                {results.quality_metrics.missing_aspects.map((aspect, index) => (
                  <li key={index}>{aspect}</li>
                ))}
              </ul>
            </div>
          )}

          {results.quality_metrics.recommendations && results.quality_metrics.recommendations.length > 0 && (
            <div style={{ marginTop: '20px' }}>
              <h3>💡 Recommendations</h3>
              <ul>
                {results.quality_metrics.recommendations.map((rec, index) => (
                  <li key={index}>{rec}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Evidence Modal */}
      {showEvidenceModal && selectedCompany && (
        <div 
          className="evidence-modal"
          onClick={closeEvidenceModal}
        >
          <div 
            className="evidence-modal-content"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              className="modal-close-btn"
              onClick={closeEvidenceModal}
            >
              ×
            </button>
            
            <h2>🔍 Evidence for {selectedCompany.domain}</h2>
            
            <div style={{ marginBottom: '20px' }}>
              <p><strong>Confidence Score:</strong> {selectedCompany.confidence_score.toFixed(2)}</p>
              <p><strong>Evidence Sources:</strong> {selectedCompany.evidence_sources}</p>
              <p><strong>Signals Found:</strong> {selectedCompany.signals_found}</p>
              <p><strong>Goal Achieved:</strong> {selectedCompany.findings.goal_achieved ? '✅ Yes' : '❌ No'}</p>
              {selectedCompany.findings.technologies && (
                <p><strong>Technologies:</strong> {selectedCompany.findings.technologies.join(', ')}</p>
              )}
            </div>

            <div>
              <h3>📄 Evidence Snippets</h3>
              {console.log('Selected Company Findings:', selectedCompany.findings)}
              {selectedCompany.findings.evidences && selectedCompany.findings.evidences.length > 0 ? (
                <div style={{ maxHeight: '400px', overflow: 'auto' }}>
                  {selectedCompany.findings.evidences.map((evidence, index) => (
                    <div 
                      key={index} 
                      className="evidence-snippet"
                    >
                      <p style={{ margin: 0 }}>
                        {evidence}
                      </p>
                    </div>
                  ))}
                </div>
              ) : (
                <div>
                  <p style={{ color: '#666', fontStyle: 'italic' }}>
                    No evidence snippets available for this company.
                  </p>
                  <details style={{ marginTop: '10px', fontSize: '12px', color: '#888' }}>
                    <summary>Debug: Show findings structure</summary>
                    <pre style={{ backgroundColor: '#f5f5f5', padding: '10px', borderRadius: '4px', overflow: 'auto' }}>
                      {JSON.stringify(selectedCompany.findings, null, 2)}
                    </pre>
                  </details>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App; 