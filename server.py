#!/usr/bin/env python3
"""
GTM Intelligence API Server

This script starts the FastAPI server for the GTM Intelligence API.
The server provides REST endpoints for research requests and responses.

Usage:
    python server.py

Endpoints:
    POST /research/batch - Start a new research batch
    GET /research/{research_id} - Get research results
    GET /research/{research_id}/status - Get research status
    GET /research - List all research sessions
    DELETE /research/{research_id} - Delete research session
    GET /health - Health check
    GET /docs - Interactive API documentation
"""

import uvicorn

if __name__ == "__main__":
    print("🚀 Starting GTM Intelligence API Server...")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("🌐 Server: http://localhost:8000")
    
    uvicorn.run(
        "app.api:app",  # Use import string format
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    ) 