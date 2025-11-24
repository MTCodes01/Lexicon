# Lexicon API - Quick Start

## Running the API

### Option 1: From the root directory (Recommended)

```bash
# From d:/Github/Lexicon
cd api
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
cd ..
.venv\Scripts\python -m uvicorn api.main:app --reload
```

### Option 2: Using Python module syntax

```bash
# From d:/Github/Lexicon/api
.venv\Scripts\activate
cd ..
python -m uvicorn api.main:app --reload
```

### Option 3: Add __init__.py to make it a package

If you want to run from the api directory, you need to modify the Python path.

## Current Issue

The error `ModuleNotFoundError: No module named 'api'` occurs because:
- You're running `uvicorn api.main:app` from inside the `api` directory
- Python can't find the `api` module because it's looking in the current directory

## Solution

Run from the parent directory:

```bash
# Make sure you're in d:/Github/Lexicon (not d:/Github/Lexicon/api)
cd d:/Github/Lexicon
api\.venv\Scripts\activate
python -m uvicorn api.main:app --reload
```

Or use the absolute path to the venv Python:

```bash
cd d:/Github/Lexicon
api\.venv\Scripts\python -m uvicorn api.main:app --reload
```

## Verify It's Working

Once started, you should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

Then visit:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health
