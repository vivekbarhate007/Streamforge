#!/bin/bash
# Comprehensive project test script

echo "🔍 StreamForge Project Verification"
echo "===================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASSED=0
FAILED=0

test_check() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $1${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ $1${NC}"
        ((FAILED++))
    fi
}

# 1. Check Docker services
echo "1. Checking Docker Services..."
docker compose ps | grep -q "Up" && test_check "All Docker services running" || test_check "Docker services check"

# 2. Check API health
echo ""
echo "2. Testing API Endpoints..."
curl -s http://localhost:8000/health | grep -q "healthy" && test_check "API health endpoint" || test_check "API health endpoint"

# 3. Test authentication
echo ""
echo "3. Testing Authentication..."
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"admin"}' | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)
[ ! -z "$TOKEN" ] && test_check "Login endpoint works" || test_check "Login endpoint"

# 4. Test protected endpoints
echo ""
echo "4. Testing Protected Endpoints..."
[ ! -z "$TOKEN" ] && curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/metrics/overview | grep -q "total_users" && test_check "Overview endpoint" || test_check "Overview endpoint"
[ ! -z "$TOKEN" ] && curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:8000/metrics/events_timeseries?hours=24" | grep -q "data" && test_check "Events timeseries endpoint" || test_check "Events timeseries endpoint"
[ ! -z "$TOKEN" ] && curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:8000/metrics/revenue_timeseries?days=365" | grep -q "data" && test_check "Revenue timeseries endpoint" || test_check "Revenue timeseries endpoint"
[ ! -z "$TOKEN" ] && curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:8000/metrics/top_products" | grep -q "products" && test_check "Top products endpoint" || test_check "Top products endpoint"
[ ! -z "$TOKEN" ] && curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/quality/latest | grep -q "checkpoint_name" && test_check "Quality endpoint" || test_check "Quality endpoint"
[ ! -z "$TOKEN" ] && curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/health/pipelines | grep -q "pipelines" && test_check "Health/pipelines endpoint" || test_check "Health/pipelines endpoint"

# 5. Check database data
echo ""
echo "5. Checking Database Data..."
EVENTS=$(docker compose exec -T postgres psql -U streamforge -d streamforge -t -c "SELECT COUNT(*) FROM fact_events;" 2>/dev/null | tr -d ' ')
TX=$(docker compose exec -T postgres psql -U streamforge -d streamforge -t -c "SELECT COUNT(*) FROM fact_transactions;" 2>/dev/null | tr -d ' ')
[ "$EVENTS" -gt 0 ] && test_check "Events data exists ($EVENTS events)" || test_check "Events data"
[ "$TX" -gt 0 ] && test_check "Transactions data exists ($TX transactions)" || test_check "Transactions data"

# 6. Check UI accessibility
echo ""
echo "6. Checking UI Accessibility..."
curl -s http://localhost:3000 | grep -q "StreamForge\|Next.js" && test_check "UI is accessible" || test_check "UI accessibility"

# 7. Check required files
echo ""
echo "7. Checking Required Files..."
[ -f "docker-compose.yml" ] && test_check "docker-compose.yml exists" || test_check "docker-compose.yml"
[ -f "Makefile" ] && test_check "Makefile exists" || test_check "Makefile"
[ -f "README.md" ] && test_check "README.md exists" || test_check "README.md"
[ -f ".github/workflows/ci.yml" ] && test_check "CI workflow exists" || test_check "CI workflow"

# Summary
echo ""
echo "===================================="
echo "Summary:"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All checks passed!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  Some checks failed. Review above.${NC}"
    exit 1
fi

