# Backend Configuration Guide

## Overview

This guide explains how to configure and run the AI Execution Agent FastAPI backend server.

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Google Cloud Platform account (for Google Calendar API)
- OpenAI API key or Google Gemini API key

## Installation

### 1. Create Virtual Environment

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `pydantic` - Data validation
- `python-dateutil` - Date parsing
- `google-api-python-client` - Google Calendar API
- `google-auth-httplib2` - Google authentication
- `google-auth-oauthlib` - OAuth2 flow
- `openai` - OpenAI API client (optional)
- `google-generativeai` - Google Gemini API client (optional)
- `hypothesis` - Property-based testing
- `pytest` - Unit testing

## Environment Variables

Create a `.env` file in the `backend/` directory with the following variables:

```env
# LLM Provider Configuration
LLM_PROVIDER=openai  # Options: "openai" or "gemini"

# OpenAI Configuration (if using OpenAI)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4  # or gpt-3.5-turbo

# Google Gemini Configuration (if using Gemini)
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-pro

# Google Calendar API Configuration
GOOGLE_CALENDAR_CREDENTIALS_PATH=credentials.json
GOOGLE_CALENDAR_TOKEN_PATH=token.json

# Server Configuration
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=chrome-extension://*

# Security
HTTPS_ONLY=true
MAX_EMAIL_SIZE_KB=500
RATE_LIMIT_PER_MINUTE=10
```

### Environment Variable Details

#### LLM_PROVIDER
- **Required**: Yes
- **Options**: `openai` or `gemini`
- **Description**: Specifies which LLM provider to use for task extraction and meeting prep generation

#### OPENAI_API_KEY
- **Required**: Yes (if LLM_PROVIDER=openai)
- **Description**: Your OpenAI API key from https://platform.openai.com/api-keys
- **Format**: `sk-...`

#### GEMINI_API_KEY
- **Required**: Yes (if LLM_PROVIDER=gemini)
- **Description**: Your Google Gemini API key from https://makersuite.google.com/app/apikey
- **Format**: String key

#### GOOGLE_CALENDAR_CREDENTIALS_PATH
- **Required**: Yes
- **Description**: Path to Google Calendar API OAuth2 credentials file
- **Default**: `credentials.json`

#### GOOGLE_CALENDAR_TOKEN_PATH
- **Required**: Yes
- **Description**: Path where OAuth2 token will be stored after authentication
- **Default**: `token.json`

## Google Calendar API Setup

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note your project ID

### 2. Enable Google Calendar API

1. In the Google Cloud Console, navigate to "APIs & Services" > "Library"
2. Search for "Google Calendar API"
3. Click "Enable"

### 3. Create OAuth2 Credentials

1. Navigate to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Select "Desktop app" as the application type
4. Name it "AI Execution Agent Backend"
5. Click "Create"
6. Download the credentials JSON file
7. Save it as `credentials.json` in the `backend/` directory

### 4. Configure OAuth Consent Screen

1. Navigate to "APIs & Services" > "OAuth consent screen"
2. Select "External" user type (or "Internal" if using Google Workspace)
3. Fill in required fields:
   - App name: "AI Execution Agent"
   - User support email: Your email
   - Developer contact: Your email
4. Add scopes:
   - `https://www.googleapis.com/auth/calendar.events`
   - `https://www.googleapis.com/auth/calendar.readonly`
5. Add test users (your email address)
6. Save and continue

### 5. First-Time Authentication

The first time you run the backend, it will open a browser window for OAuth2 authentication:

```bash
python -m src.main
```

1. A browser window will open
2. Sign in with your Google account
3. Grant calendar access permissions
4. The token will be saved to `token.json`
5. Subsequent runs will use the saved token

**Note**: The `token.json` file contains sensitive credentials. Never commit it to version control.

## Running the Server

### Development Mode

```bash
# Activate virtual environment first
cd backend
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Run with auto-reload
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
# Run without auto-reload
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using Python Module

```bash
python -m src.main
```

The server will start at `http://localhost:8000`

### Verify Server is Running

Open your browser and navigate to:
- API docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health` (if implemented)

## Testing

### Run All Tests

```bash
# Activate virtual environment
cd backend
venv\Scripts\activate  # Windows

# Run all tests
pytest
```

### Run Unit Tests Only

```bash
pytest tests/ -k "not property"
```

### Run Property-Based Tests Only

```bash
pytest tests/ -k "property"
```

### Run Specific Test File

```bash
pytest tests/test_api.py
```

### Run with Coverage

```bash
pytest --cov=src --cov-report=html
```

Coverage report will be generated in `htmlcov/index.html`

### Run with Verbose Output

```bash
pytest -v
```

## API Endpoints

### POST /run-agent

Processes email content and returns extracted tasks with calendar scheduling.

**Request Body**:
```json
{
  "email_content": {
    "subject": "Project deadline update",
    "body": "Please complete the report by tomorrow",
    "sender": "manager@example.com",
    "timestamp": "2024-02-20T10:00:00Z",
    "thread_messages": [],
    "forwarded_messages": []
  },
  "user_timezone": "America/New_York",
  "calendar_id": "primary"
}
```

**Response**:
```json
{
  "tasks": [...],
  "stats": {
    "tasks_extracted": 1,
    "calendar_blocks_created": 1,
    "scheduling_conflicts": 0,
    "manual_review_items": 0
  },
  "logs": [...],
  "errors": []
}
```

## Troubleshooting

### Issue: "Module not found" errors

**Solution**: Ensure virtual environment is activated and dependencies are installed:
```bash
venv\Scripts\activate
pip install -r requirements.txt
```

### Issue: Google Calendar authentication fails

**Solution**: 
1. Delete `token.json` if it exists
2. Verify `credentials.json` is valid
3. Ensure OAuth consent screen is configured
4. Check that your email is added as a test user
5. Run the server again to re-authenticate

### Issue: LLM API errors

**Solution**:
1. Verify API key is correct in `.env`
2. Check API key has sufficient credits/quota
3. Verify network connectivity
4. Check API provider status page

### Issue: CORS errors from Chrome Extension

**Solution**:
1. Verify `CORS_ORIGINS` includes `chrome-extension://*`
2. Restart the FastAPI server after changing CORS settings
3. Check browser console for specific CORS error details

### Issue: Rate limiting errors

**Solution**:
1. Adjust `RATE_LIMIT_PER_MINUTE` in `.env`
2. Implement exponential backoff in extension
3. Consider upgrading API plan for higher limits

## Security Best Practices

1. **Never commit sensitive files**:
   - Add `.env`, `credentials.json`, `token.json` to `.gitignore`

2. **Use HTTPS in production**:
   - Set `HTTPS_ONLY=true`
   - Use a reverse proxy (nginx, Caddy) with SSL certificates

3. **Rotate API keys regularly**:
   - Update OpenAI/Gemini API keys periodically
   - Revoke old keys after rotation

4. **Limit CORS origins**:
   - In production, specify exact extension ID instead of wildcard
   - Example: `CORS_ORIGINS=chrome-extension://your-extension-id`

5. **Monitor API usage**:
   - Track LLM API costs
   - Set up billing alerts
   - Monitor rate limits

## Deployment

### Local Development
Follow the "Running the Server" section above.

### Cloud Deployment (Example: Heroku)

1. Create `Procfile`:
```
web: uvicorn src.main:app --host 0.0.0.0 --port $PORT
```

2. Set environment variables in Heroku dashboard

3. Deploy:
```bash
git push heroku main
```

### Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t ai-agent-backend .
docker run -p 8000:8000 --env-file .env ai-agent-backend
```

## Support

For issues or questions:
1. Check this configuration guide
2. Review error logs in console output
3. Consult FastAPI documentation: https://fastapi.tiangolo.com/
4. Check Google Calendar API docs: https://developers.google.com/calendar/api
