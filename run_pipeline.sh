#!/bin/bash
# Helper script to run the AI Song Pipeline with automatic service management

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SPLEETER_SERVICE_DIR="$SCRIPT_DIR/spleeter_service"
SPLEETER_SERVICE_URL="http://localhost:5001"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=================================="
echo "AI Song Pipeline Launcher"
echo "=================================="

# Function to check if Spleeter service is running
check_spleeter_service() {
    curl -s -f "$SPLEETER_SERVICE_URL/health" > /dev/null 2>&1
    return $?
}

# Check if Spleeter service is running
echo -e "\n${YELLOW}Checking Spleeter service...${NC}"
if check_spleeter_service; then
    echo -e "${GREEN}✓ Spleeter service is running${NC}"
else
    echo -e "${RED}✗ Spleeter service is not running${NC}"
    echo -e "${YELLOW}Starting Spleeter service...${NC}"
    
    # Start service in background
    cd "$SPLEETER_SERVICE_DIR"
    if [ -f "start.sh" ]; then
        ./start.sh > /tmp/spleeter_service.log 2>&1 &
        SPLEETER_PID=$!
        echo "Service PID: $SPLEETER_PID"
        
        # Wait for service to start (max 30 seconds)
        echo "Waiting for service to start..."
        for i in {1..30}; do
            sleep 1
            if check_spleeter_service; then
                echo -e "${GREEN}✓ Spleeter service started successfully${NC}"
                break
            fi
            if [ $i -eq 30 ]; then
                echo -e "${RED}✗ Failed to start Spleeter service${NC}"
                echo "Check logs at /tmp/spleeter_service.log"
                exit 1
            fi
        done
    else
        echo -e "${RED}✗ start.sh not found in spleeter_service directory${NC}"
        echo "Please set up the Spleeter service first. See README.md"
        exit 1
    fi
    cd "$SCRIPT_DIR"
fi

# Run the main pipeline with all provided arguments
echo -e "\n${YELLOW}Starting main pipeline...${NC}"
echo "==================================\n"

python pipeline.py "$@"
PIPELINE_EXIT_CODE=$?

echo -e "\n=================================="
if [ $PIPELINE_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ Pipeline completed successfully${NC}"
else
    echo -e "${RED}✗ Pipeline failed with exit code $PIPELINE_EXIT_CODE${NC}"
fi
echo "==================================\n"

# Note: We don't stop the Spleeter service as it can be reused for subsequent runs
echo -e "${YELLOW}Note: Spleeter service is still running at $SPLEETER_SERVICE_URL${NC}"
echo "You can stop it manually if needed."

exit $PIPELINE_EXIT_CODE
