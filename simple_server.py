#!/usr/bin/env python3
"""
Simple GTM Intelligence API Server

This script starts a simple synchronous FastAPI server for the GTM Intelligence API.
The server provides a single endpoint that directly executes the research workflow.

Usage:
    python simple_server.py

Endpoints:
    POST /research - Start a research (synchronous)
    GET /health - Health check
"""

import uvicorn
from app.simple_api import app

if __name__ == "__main__":
    print("🚀 Starting Simple GTM Intelligence API Server...")
    print("📚 API Documentation: http://localhost:8001/docs")
    print("🔍 Health Check: http://localhost:8001/health")
    print("🌐 Server: http://localhost:8001")
    print("💡 Simple synchronous API - no background processing!")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    ) 