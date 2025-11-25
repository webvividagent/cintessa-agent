#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
echo "╔══════════════════════════════════════╗"
echo "║         🚀 Cintessa Agent           ║"
echo "║      AI-Powered Coding IDE          ║"
echo "╚══════════════════════════════════════╝"
echo -e "${NC}"

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo -e "${RED}❌ Error: Please run this script from the cintessa_agent directory${NC}"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Creating virtual environment...${NC}"
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Failed to create virtual environment${NC}"
        exit 1
    fi
fi

# Activate virtual environment
echo -e "${YELLOW}🔧 Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip and install requirements
echo -e "${YELLOW}📦 Installing/updating dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to install dependencies${NC}"
    exit 1
fi

# Check if Ollama is running
echo -e "${YELLOW}🤖 Checking Ollama connection...${NC}"
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo -e "${YELLOW}⚠️  Ollama not running or not accessible${NC}"
    echo -e "${YELLOW}   Make sure to start Ollama: ollama serve${NC}"
fi

echo -e "${GREEN}"
echo "✅ Ready to launch!"
echo "🌐 The app will open at: ${CYAN}http://localhost:8501${GREEN}"
echo "🛑 Press ${RED}Ctrl+C${GREEN} to stop the server"
echo -e "${NC}"
echo ""

# Launch the Streamlit app
streamlit run main.py
