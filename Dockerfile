FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose FastAPI backend and Streamlit frontend ports
EXPOSE 8000
EXPOSE 8501

# Command to run both services
CMD python -m uvicorn api.app:app --host 0.0.0.0 --port 8000 & python -m streamlit run frontend/streamlit_app.py --server.port 8501 --server.address 0.0.0.0
