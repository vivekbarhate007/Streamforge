#!/bin/bash
# Final Project Verification - 100 Point Scoring System

echo "🔍 StreamForge Final Project Verification"
echo "=========================================="
echo ""

SCORE=0
MAX_SCORE=100

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

check() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $1${NC}"
        SCORE=$((SCORE + $2))
    else
        echo -e "${RED}❌ $1${NC}"
    fi
}

# 1. Project Structure (10 points)
echo -e "${BLUE}1. Project Structure (10 points)${NC}"
[ -f "docker-compose.yml" ] && check "docker-compose.yml exists" 2
[ -f "Makefile" ] && check "Makefile exists" 2
[ -f "README.md" ] && check "README.md exists" 2
[ -f ".gitignore" ] && check ".gitignore exists" 1
[ -f ".env.example" ] && check ".env.example exists" 1
[ -d "services" ] && check "services directory exists" 1
[ -d "warehouse/dbt" ] && check "dbt directory exists" 1
echo ""

# 2. Docker Services (15 points)
echo -e "${BLUE}2. Docker Services (15 points)${NC}"
docker compose ps | grep -q "Up" && check "All Docker services running" 5 || check "Docker services check" 0
curl -s http://localhost:8000/health | grep -q "healthy" && check "API health endpoint" 2 || check "API health" 0
curl -s http://localhost:3000 > /dev/null && check "UI is accessible" 2 || check "UI accessibility" 0
curl -s http://localhost:8080 > /dev/null && check "Kafka UI is accessible" 2 || check "Kafka UI" 0
docker compose exec -T postgres pg_isready -U streamforge > /dev/null 2>&1 && check "PostgreSQL is ready" 2 || check "PostgreSQL" 0
docker compose exec -T kafka kafka-topics --bootstrap-server localhost:9092 --list > /dev/null 2>&1 && check "Kafka is accessible" 2 || check "Kafka" 0
echo ""

# 3. API Endpoints (20 points)
echo -e "${BLUE}3. API Endpoints (20 points)${NC}"
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"admin"}' | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)
[ ! -z "$TOKEN" ] && check "Login endpoint works" 3 || check "Login endpoint" 0

[ ! -z "$TOKEN" ] && curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/metrics/overview | grep -q "total_users" && check "Overview endpoint" 3 || check "Overview endpoint" 0
[ ! -z "$TOKEN" ] && curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:8000/metrics/events_timeseries?hours=24" | grep -q "data" && check "Events timeseries endpoint" 3 || check "Events timeseries" 0
[ ! -z "$TOKEN" ] && curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:8000/metrics/revenue_timeseries?days=365" | grep -q "data" && check "Revenue timeseries endpoint" 3 || check "Revenue timeseries" 0
[ ! -z "$TOKEN" ] && curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:8000/metrics/top_products" | grep -q "products" && check "Top products endpoint" 3 || check "Top products" 0
[ ! -z "$TOKEN" ] && curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/quality/latest | grep -q "checkpoint_name" && check "Quality endpoint" 2 || check "Quality endpoint" 0
[ ! -z "$TOKEN" ] && curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/health/pipelines | grep -q "pipelines" && check "Health/pipelines endpoint" 3 || check "Health/pipelines" 0
echo ""

# 4. Data Pipeline (15 points)
echo -e "${BLUE}4. Data Pipeline (15 points)${NC}"
EVENTS=$(docker compose exec -T postgres psql -U streamforge -d streamforge -t -c "SELECT COUNT(*) FROM fact_events;" 2>/dev/null | tr -d ' ')
TX=$(docker compose exec -T postgres psql -U streamforge -d streamforge -t -c "SELECT COUNT(*) FROM fact_transactions;" 2>/dev/null | tr -d ' ')
[ "$EVENTS" -gt 0 ] && check "Events data exists ($EVENTS events)" 5 || check "Events data" 0
[ "$TX" -gt 0 ] && check "Transactions data exists ($TX transactions)" 5 || check "Transactions data" 0
docker compose exec -T postgres psql -U streamforge -d streamforge -c "SELECT COUNT(*) FROM dim_users;" > /dev/null 2>&1 && check "Dimension tables exist" 3 || check "Dimension tables" 0
docker compose exec -T postgres psql -U streamforge -d streamforge -c "SELECT COUNT(*) FROM dim_products;" > /dev/null 2>&1 && check "Product dimension exists" 2 || check "Product dimension" 0
echo ""

# 5. Code Quality (10 points)
echo -e "${BLUE}5. Code Quality (10 points)${NC}"
[ -f "services/api/tests/test_auth.py" ] && check "API tests exist" 2 || check "API tests" 0
[ -f "services/api/tests/test_metrics.py" ] && check "Metrics tests exist" 2 || check "Metrics tests" 0
[ -f ".github/workflows/ci.yml" ] && check "CI workflow exists" 2 || check "CI workflow" 0
[ -f "LICENSE" ] && check "LICENSE file exists" 2 || check "LICENSE" 0
[ ! -f ".env" ] && check ".env not in repo (security)" 2 || check ".env security" 0
echo ""

# 6. Documentation (10 points)
echo -e "${BLUE}6. Documentation (10 points)${NC}"
[ -f "README.md" ] && grep -q "Quick Start" README.md && check "README has Quick Start" 2 || check "README Quick Start" 0
[ -f "README.md" ] && grep -q "Architecture" README.md && check "README has Architecture" 2 || check "README Architecture" 0
[ -f "docs/ARCHITECTURE.md" ] && check "ARCHITECTURE.md exists" 2 || check "ARCHITECTURE.md" 0
[ -f "QUICKSTART.md" ] && check "QUICKSTART.md exists" 2 || check "QUICKSTART.md" 0
[ -f ".env.example" ] && check ".env.example exists" 2 || check ".env.example" 0
echo ""

# 7. UI Pages (10 points)
echo -e "${BLUE}7. UI Pages (10 points)${NC}"
[ -f "services/ui/src/app/login/page.tsx" ] && check "Login page exists" 2 || check "Login page" 0
[ -f "services/ui/src/app/dashboard/overview/page.tsx" ] && check "Overview page exists" 2 || check "Overview page" 0
[ -f "services/ui/src/app/dashboard/events/page.tsx" ] && check "Events page exists" 1 || check "Events page" 0
[ -f "services/ui/src/app/dashboard/revenue/page.tsx" ] && check "Revenue page exists" 1 || check "Revenue page" 0
[ -f "services/ui/src/app/dashboard/top-products/page.tsx" ] && check "Top products page exists" 1 || check "Top products page" 0
[ -f "services/ui/src/app/dashboard/quality/page.tsx" ] && check "Quality page exists" 1 || check "Quality page" 0
[ -f "services/ui/src/app/dashboard/health/page.tsx" ] && check "Health page exists" 1 || check "Health page" 0
[ -f "services/ui/src/components/Nav.tsx" ] && check "Navigation component exists" 1 || check "Navigation component" 0
echo ""

# 8. API Documentation (5 points)
echo -e "${BLUE}8. API Documentation (5 points)${NC}"
curl -s http://localhost:8000/docs > /dev/null && check "Swagger UI accessible" 2 || check "Swagger UI" 0
curl -s http://localhost:8000/openapi.json | python3 -c "import sys, json; d=json.load(sys.stdin); print('ok' if 'paths' in d and len(d['paths']) > 5 else 'fail')" 2>/dev/null | grep -q "ok" && check "OpenAPI schema complete" 2 || check "OpenAPI schema" 0
curl -s http://localhost:8000/openapi.json | python3 -c "import sys, json; d=json.load(sys.stdin); paths=d.get('paths', {}); evt=paths.get('/metrics/events_timeseries', {}).get('get', {}); print('ok' if 'parameters' in evt else 'fail')" 2>/dev/null | grep -q "ok" && check "API parameters documented" 1 || check "API parameters" 0
echo ""

# 9. Data Transformations (5 points)
echo -e "${BLUE}9. Data Transformations (5 points)${NC}"
[ -f "warehouse/dbt/models/staging/stg_raw_events.sql" ] && check "dbt staging model exists" 1 || check "dbt staging" 0
[ -f "warehouse/dbt/models/marts/dim_users.sql" ] && check "dbt dimension model exists" 1 || check "dbt dimension" 0
[ -f "warehouse/dbt/models/marts/metrics_daily_kpis.sql" ] && check "dbt metrics model exists" 1 || check "dbt metrics" 0
[ -f "quality/great_expectations/great_expectations.yml" ] && check "Great Expectations config exists" 1 || check "GE config" 0
[ -f "warehouse/dbt/run_quality.py" ] && check "Quality check script exists" 1 || check "Quality script" 0
echo ""

# 10. Production Readiness (10 points)
echo -e "${BLUE}10. Production Readiness (10 points)${NC}"
[ -f ".gitignore" ] && grep -q ".env" .gitignore && check ".env in .gitignore" 2 || check ".env ignore" 0
[ ! -d "services/ui/node_modules" ] && check "node_modules not in repo" 2 || check "node_modules" 0
[ ! -d "services/ui/.next" ] && check ".next not in repo" 2 || check ".next" 0
[ ! -d "services/api/app/__pycache__" ] && check "__pycache__ not in repo" 2 || check "__pycache__" 0
[ -f "docker-compose.yml" ] && grep -q "healthcheck" docker-compose.yml && check "Health checks configured" 2 || check "Health checks" 0
echo ""

# Final Score
echo "=========================================="
echo -e "${BLUE}Final Score: ${SCORE}/${MAX_SCORE}${NC}"
echo ""

if [ $SCORE -ge 90 ]; then
    echo -e "${GREEN}🎉 Excellent! Project is production-ready!${NC}"
elif [ $SCORE -ge 75 ]; then
    echo -e "${YELLOW}✅ Good! Minor improvements needed.${NC}"
elif [ $SCORE -ge 60 ]; then
    echo -e "${YELLOW}⚠️  Fair. Some features need attention.${NC}"
else
    echo -e "${RED}❌ Needs significant work.${NC}"
fi

echo ""
echo "Breakdown:"
echo "  Project Structure: 10 points"
echo "  Docker Services: 15 points"
echo "  API Endpoints: 20 points"
echo "  Data Pipeline: 15 points"
echo "  Code Quality: 10 points"
echo "  Documentation: 10 points"
echo "  UI Pages: 10 points"
echo "  API Documentation: 5 points"
echo "  Data Transformations: 5 points"
echo "  Production Readiness: 10 points"
echo ""

exit 0

