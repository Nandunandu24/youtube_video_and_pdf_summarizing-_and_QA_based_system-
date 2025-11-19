# scripts/run_api.ps1

# Activate the virtual environment
Write-Host "Activating virtual environment..."
& .\.venv\Scripts\Activate.ps1

# Start FastAPI server using uvicorn
Write-Host "Starting FastAPI development server..."
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
