# Grok Mirror API

## Overview
This is a FastAPI-based proxy service that acts as a mirror for the Grok API (https://grok.ylsagi.com). It provides a REST API endpoint that allows external applications like Dify to interact with Grok's AI capabilities.

**Current Status:** Running successfully on Replit
**Version:** 3.3.0
**Port:** 5000

## Recent Changes
- **2024-11-17**: Imported from GitHub and configured for Replit environment
  - Changed default port from 8000 to 5000 (Replit standard)
  - Set up workflow to run the FastAPI application
  - Configured host binding to 0.0.0.0 for web access
  - Added Python .gitignore

## Project Architecture

### Technology Stack
- **Framework:** FastAPI 0.104.1
- **Server:** Uvicorn 0.24.0
- **HTTP Client:** requests 2.31.0
- **Data Validation:** Pydantic 2.5.2
- **Language:** Python 3.11

### File Structure
```
.
├── main.py              # Main FastAPI application
├── requirements.txt     # Python dependencies
├── Dockerfile          # Container configuration (for other platforms)
├── README.md           # Basic project info
├── .gitignore          # Git ignore rules
└── replit.md           # This file
```

### API Endpoints
1. **GET /** - Root endpoint, returns API status and version
2. **GET /health** - Health check endpoint
3. **POST /api/chat** - Main chat endpoint that proxies requests to Grok

### How It Works
1. Receives chat requests via `/api/chat` endpoint
2. Transforms the request into Grok's expected format
3. Forwards request to Grok mirror site (https://grok.ylsagi.com)
4. Parses streaming response from Grok
5. Returns formatted response to client

### Authentication
The application uses pre-configured authentication headers (Cookie, User-Agent, etc.) stored in the `HEADERS` constant in `main.py`. These headers were obtained from browser developer tools (F12) and may need periodic updates if the session expires.

## Configuration

### Environment Variables
- `PORT` - Server port (default: 5000)

### Key Settings in main.py
- `GROK_BASE_URL` - The Grok mirror website URL
- `HEADERS` - Authentication and browser headers for Grok API requests

## Running the Application




