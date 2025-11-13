#!/bin/bash

# Setup verification script
echo "========================================"
echo "gRPC Pipeline Project Setup Verification"
echo "========================================"
echo ""

# Check Docker
echo "1. Checking Docker..."
if command -v docker &> /dev/null; then
    docker --version
    echo "   ✓ Docker is installed"
else
    echo "   ✗ Docker is NOT installed"
    echo "   Please install Docker from https://www.docker.com/"
    exit 1
fi
echo ""

# Check Docker Compose
echo "2. Checking Docker Compose..."
if command -v docker-compose &> /dev/null; then
    docker-compose --version
    echo "   ✓ Docker Compose is installed"
else
    echo "   ✗ Docker Compose is NOT installed"
    echo "   Please install Docker Compose"
    exit 1
fi
echo ""

# Check if Docker daemon is running
echo "3. Checking Docker daemon..."
if docker info &> /dev/null; then
    echo "   ✓ Docker daemon is running"
else
    echo "   ✗ Docker daemon is NOT running"
    echo "   Please start Docker"
    exit 1
fi
echo ""

# Check project structure
echo "4. Checking project structure..."
required_dirs=(
    "proto"
    "service1-input"
    "service2-preprocess"
    "service3-analysis"
    "service4-report"
    "client"
)

all_present=true
for dir in "${required_dirs[@]}"; do
    if [ -d "$dir" ]; then
        echo "   ✓ $dir/ exists"
    else
        echo "   ✗ $dir/ is missing"
        all_present=false
    fi
done

if [ "$all_present" = false ]; then
    echo ""
    echo "   Some directories are missing!"
    exit 1
fi
echo ""

# Check required files
echo "5. Checking required files..."
required_files=(
    "proto/pipeline.proto"
    "docker-compose.yml"
    "Makefile"
    "README.md"
)

all_present=true
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✓ $file exists"
    else
        echo "   ✗ $file is missing"
        all_present=false
    fi
done

if [ "$all_present" = false ]; then
    echo ""
    echo "   Some files are missing!"
    exit 1
fi
echo ""

echo "========================================"
echo "✓ All checks passed!"
echo "========================================"
echo ""
echo "You are ready to run the project!"
echo ""
echo "Next steps:"
echo "  1. Build the project:  make build"
echo "  2. Start services:     make up"
echo "  3. Run test:           make test"
echo "  4. View logs:          make logs"
echo ""
echo "For more information, see README.md"
echo ""
