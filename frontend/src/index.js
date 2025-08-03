import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './index.css';
import App from './App';
import TestStreaming from './TestStreaming';
import SimpleStreamingTest from './SimpleStreamingTest';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <Router>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/test" element={<TestStreaming />} />
        <Route path="/debug" element={<SimpleStreamingTest />} />
      </Routes>
    </Router>
  </React.StrictMode>
); 