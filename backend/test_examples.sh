#!/bin/bash

# Test examples for the improved Animathic backend
echo "🧪 Testing Animathic Backend - Simplified & Reliable System"
echo "==========================================================="

BASE_URL="http://localhost:8080"

# Test 1: Simple Circle Fade
echo -e "\n📝 Test 1: Simple Circle Fade"
curl -X POST "$BASE_URL/api/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create a blue circle that fades in smoothly", "user_id": "test_user"}' \
  | jq '.job_id' 2>/dev/null || echo "Job submitted (check status endpoint)"

# Test 2: Text Display
echo -e "\n📝 Test 2: Text Display"  
curl -X POST "$BASE_URL/api/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Display the text Hello World clearly without overlap", "user_id": "test_user"}' \
  | jq '.job_id' 2>/dev/null || echo "Job submitted (check status endpoint)"

# Test 3: Multiple Objects
echo -e "\n📝 Test 3: Multiple Objects"
curl -X POST "$BASE_URL/api/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Show a circle and a square positioned apart without overlapping", "user_id": "test_user"}' \
  | jq '.job_id' 2>/dev/null || echo "Job submitted (check status endpoint)"

# Test 4: Function Plot
echo -e "\n📝 Test 4: Function Plot"
curl -X POST "$BASE_URL/api/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Plot a simple sine wave with axes", "user_id": "test_user"}' \
  | jq '.job_id' 2>/dev/null || echo "Job submitted (check status endpoint)"

echo -e "\n✅ Tests submitted! Check the status endpoints above to see results."
echo -e "\n📖 Visit: http://localhost:8080/docs for full API documentation"
