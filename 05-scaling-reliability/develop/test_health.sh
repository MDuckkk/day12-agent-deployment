#!/bin/bash
# Test script for health checks and graceful shutdown

echo "=== Testing Health Checks ==="
echo ""

# Start the app in background
echo "Starting agent..."
python app.py &
APP_PID=$!
echo "Agent PID: $APP_PID"

# Wait for startup
sleep 3

echo ""
echo "--- Test 1: Health check ---"
curl -s http://localhost:8000/health | python -m json.tool

echo ""
echo "--- Test 2: Readiness check ---"
curl -s http://localhost:8000/ready | python -m json.tool

echo ""
echo "--- Test 3: Ask endpoint ---"
curl -s http://localhost:8000/ask -X POST \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello"}' | python -m json.tool

echo ""
echo "--- Test 4: Graceful shutdown ---"
echo "Sending SIGTERM to PID $APP_PID..."
kill -TERM $APP_PID

# Wait for graceful shutdown
wait $APP_PID
echo "✅ Agent shut down gracefully"
