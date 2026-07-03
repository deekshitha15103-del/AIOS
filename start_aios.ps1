cd C:\Users\deeks\AIOS

$env:HF_HUB_OFFLINE="1"
$env:TRANSFORMERS_OFFLINE="1"

Start-Process powershell -ArgumentList "-NoExit", "-Command", ".\venv\Scripts\activate; python -m uvicorn backend.main:app --reload"

Start-Process powershell -ArgumentList "-NoExit", "-Command", ".\venv\Scripts\activate; streamlit run frontend/app.py"