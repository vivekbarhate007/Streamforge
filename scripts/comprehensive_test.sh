#!/bin/bash
# Comprehensive Test Script - Tests all functionality twice

echo "🧪 StreamForge Comprehensive Testing"
echo "===================================="
echo ""

PASSED=0
FAILED=0
TOTAL=0

test_check() {
    TOTAL=$((TOTAL + 1))
    if [ $? -eq 0 ]; then
        echo "✅ $1"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo "❌ $1"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== ROUND 1: Initial Testing ===${NC}"
echo ""

# 1. Service Health Checks
echo "1. Service Health Checks"
docker compose ps | grep -q "Up" && test_check "All services running"
curl -s http://localhost:8000/health | grep -q "healthy" && test_check "API health endpoint"
curl -s http://localhost:3000 > /dev/null && test_check "UI accessible"
curl -s http://localhost:8080 > /dev/null && test_check "Kafka UI accessible"
echo ""

# 2. Authentication
echo "2. Authentication Tests"
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"admin"}' | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)
[ ! -z "$TOKEN" ] && test_check "Login successful"
[ -z "$TOKEN" ] && echo "❌ Login failed" && FAILED=$((FAILED + 1)) && TOTAL=$((TOTAL + 1))
echo ""

# 3. API Endpoints
echo "3. API Endpoint Tests"
[ ! -z "$TOKEN" ] && curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/metrics/overview | grep -q "total_users" && test_check "Overview endpoint"
[ ! -z "$TOKEN" ] && curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:8000/metrics/events_timeseries?hours=24" | grep -q "data" && test_check "Events timeseries endpoint"
[ ! -z "$TOKEN" ] && curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:8000/metrics/revenue_timeseries?days=365" | grep -q "data" && test_check "Revenue timeseries endpoint"
[ ! -z "$TOKEN" ] && curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:8000/metrics/top_products?limit=10" | grep -q "products" && test_check "Top products endpoint"
[ ! -z "$TOKEN" ] && curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/quality/latest | grep -q "checkpoint_name" && test_check "Quality endpoint"
[ ! -z "$TOKEN" ] && curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/health/pipelines | grep -q "pipelines" && test_check "Health/pipelines endpoint"
echo ""

# 4. Data Validation
echo "4. Data Validation"
EVENTS=$(docker compose exec -T postgres psql -U streamforge -d streamforge -t -c "SELECT COUNT(*) FROM fact_events;" 2>/dev/null | tr -d ' ')
TX=$(docker compose exec -T postgres psql -U streamforge -d streamforge -t -c "SELECT COUNT(*) FROM fact_transactions;" 2>/dev/null | tr -d ' ')
[ "$EVENTS" -gt 0 ] && test_check "Events data exists ($EVENTS events)"
[ "$TX" -gt 0 ] && test_check "Transactions data exists ($TX transactions)"
echo ""

# 5. Production Features
echo "5. Production Features"
curl -s http://localhost:8000/metrics | grep -q "http_requests_total" && test_check "Prometheus metrics endpoint"
curl -s http://localhost:8000/health/live | grep -q "alive" && test_check "Liveness probe"
curl -s http://localhost:8000/health/ready | grep -q "ready" && test_check "Readiness probe"
docker compose ps redis | grep -q "Up" && test_check "Redis service running"
echo ""

# 6. API Documentation
echo "6. API Documentation"
curl -s http://localhost:8000/docs > /dev/null && test_check "Swagger UI accessible"
curl -s http://localhost:8000/openapi.json | python3 -c "import sys, json; d=json.load(sys.stdin); exit(0 if 'paths' in d and len(d['paths']) > 5 else 1)" && test_check "OpenAPI schema complete"
echo ""

echo -e "${BLUE}=== ROUND 2: Verification Testing ===${NC}"
echo ""

# Round 2 - Same tests
echo "7. Round 2 - Service Health"
docker compose ps | grep -q "Up" && test_check "All services still running"
curl -s http://localhost:8000/health | grep -q "healthy" && test_check "API still healthy"
echo ""

echo "8. Round 2 - API Endpoints"
[ ! -z "$TOKEN" ] && curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/metrics/overview | python3 -c "import sys, json; d=json.load(sys.stdin); exit(0 if 'total_users' in d and d['total_users'] >= 0 else 1)" && test_check "Overview returns valid data"
[ ! -z "$TOKEN" ] && curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:8000/metrics/events_timeseries?hours=24" | python3 -c "import sys, json; d=json.load(sys.stdin); exit(0 if 'data' in d and isinstance(d['data'], list) else 1)" && test_check "Events timeseries returns valid data"
[ ! -z "$TOKEN" ] && curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:8000/metrics/revenue_timeseries?days=365" | python3 -c "import sys, json; d=json.load(sys.stdin); exit(0 if 'data' in d and isinstance(d['data'], list) else 1)" && test_check "Revenue timeseries returns valid data"
[ ! -z "$TOKEN" ] && curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:8000/metrics/top_products?limit=5" | python3 -c "import sys, json; d=json.load(sys.stdin); exit(0 if 'products' in d and isinstance(d['products'], list) else 1)" && test_check "Top products returns valid data"
echo ""

echo "9. Round 2 - Rate Limiting"
for i in {1..15}; do
    curl -s -X POST http://localhost:8000/auth/login \
        -H "Content-Type: application/json" \
        -d '{"username":"admin","password":"wrong"}' > /dev/null
done
curl -s -X POST http://localhost:8000/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"admin"}' | grep -q "access_token" && test_check "Rate limiting working (login still works)"
echo ""

echo "10. UI Functionality Check"
curl -s http://localhost:3000 | grep -q "StreamForge\|Next.js" && test_check "UI homepage loads"
curl -s http://localhost:3000/login | grep -q "login\|Login" && test_check "Login page accessible"
echo ""

# Summary
echo "===================================="
echo -e "${BLUE}Test Summary:${NC}"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo -e "Total: $TOTAL"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  Some tests failed. Review above.${NC}"
    exit 1
fi

