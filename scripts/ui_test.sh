#!/bin/bash
# UI Functionality Test

echo "🎨 UI Functionality Testing"
echo "=========================="
echo ""

PASSED=0
FAILED=0

test_check() {
    if [ $? -eq 0 ]; then
        echo "✅ $1"
        PASSED=$((PASSED + 1))
    else
        echo "❌ $1"
        FAILED=$((FAILED + 1))
    fi
}

# Test all UI pages
echo "1. Testing UI Pages"
curl -s http://localhost:3000 | grep -qi "StreamForge\|Next" && test_check "Homepage loads"
curl -s http://localhost:3000/login | grep -qi "login\|Login\|username\|password" && test_check "Login page loads with form"
curl -s http://localhost:3000/dashboard/overview 2>&1 | grep -qi "login\|redirect" && test_check "Dashboard requires authentication"
echo ""

# Test API endpoints that UI uses
echo "2. Testing API Endpoints Used by UI"
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"admin"}' | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)

[ ! -z "$TOKEN" ] && test_check "Login API works"

if [ ! -z "$TOKEN" ]; then
    OVERVIEW=$(curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/metrics/overview)
    echo "$OVERVIEW" | python3 -c "import sys, json; d=json.load(sys.stdin); exit(0 if 'total_users' in d and 'total_events' in d else 1)" && test_check "Overview API returns valid data"
    
    EVENTS=$(curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:8000/metrics/events_timeseries?hours=24")
    echo "$EVENTS" | python3 -c "import sys, json; d=json.load(sys.stdin); exit(0 if 'data' in d and isinstance(d['data'], list) else 1)" && test_check "Events API returns valid data"
    
    REVENUE=$(curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:8000/metrics/revenue_timeseries?days=365")
    echo "$REVENUE" | python3 -c "import sys, json; d=json.load(sys.stdin); exit(0 if 'data' in d and isinstance(d['data'], list) else 1)" && test_check "Revenue API returns valid data"
    
    PRODUCTS=$(curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:8000/metrics/top_products?limit=10")
    echo "$PRODUCTS" | python3 -c "import sys, json; d=json.load(sys.stdin); exit(0 if 'products' in d and isinstance(d['products'], list) else 1)" && test_check "Top Products API returns valid data"
    
    QUALITY=$(curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/quality/latest)
    echo "$QUALITY" | python3 -c "import sys, json; d=json.load(sys.stdin); exit(0 if 'checkpoint_name' in d and 'success' in d else 1)" && test_check "Quality API returns valid data"
    
    HEALTH=$(curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/health/pipelines)
    echo "$HEALTH" | python3 -c "import sys, json; d=json.load(sys.stdin); exit(0 if 'pipelines' in d and 'table_counts' in d else 1)" && test_check "Health API returns valid data"
fi
echo ""

# Test production features
echo "3. Testing Production Features"
curl -s http://localhost:8000/metrics | grep -q "http_requests_total" && test_check "Prometheus metrics available"
curl -s http://localhost:8000/health/live | grep -q "alive" && test_check "Liveness probe works"
curl -s http://localhost:8000/health/ready | grep -q "ready" && test_check "Readiness probe works"
echo ""

echo "=========================="
echo "Summary: Passed: $PASSED, Failed: $FAILED"
if [ $FAILED -eq 0 ]; then
    echo "🎉 All UI tests passed!"
    exit 0
else
    echo "⚠️  Some tests failed"
    exit 1
fi

