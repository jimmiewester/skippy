#!/bin/bash

# Install Python dependencies if needed
if [ ! -d "venv" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv venv
fi

echo "📦 Installing Python dependencies..."
source venv/bin/activate
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please update .env file with your AWS credentials and other settings"
fi

echo ""
echo "🎉 Setup complete! You can now run:"
echo ""
echo "  # Start the FastAPI server:"
echo "  source venv/bin/activate"
echo "  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "  # Start the Celery worker (in another terminal):"
echo "  source venv/bin/activate"
echo "  celery -A app.workers.celery_app worker --loglevel=info"
echo ""
echo "  # Start the Celery beat scheduler (optional, in another terminal):"
echo "  source venv/bin/activate"
echo "  celery -A app.workers.celery_app beat --loglevel=info"
echo ""
echo "📖 API documentation will be available at: http://localhost:8000/docs"
echo "🔍 Redis Commander UI: http://localhost:8081"
