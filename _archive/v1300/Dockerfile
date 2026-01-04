# YEDAN AGI - Docker Configuration
# For deploying agi_coordinator (Fast Brain) to Cloud Run

FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy AGI modules
COPY agi_*.py .
COPY yedan_*.py .
COPY .env.example .env

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "print('YEDAN AGI: ALIVE')" || exit 1

# Run coordinator
ENV PYTHONUNBUFFERED=1
CMD ["python", "agi_coordinator.py", "--once"]
