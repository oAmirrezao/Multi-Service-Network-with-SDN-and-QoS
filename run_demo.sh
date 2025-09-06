#!/bin/bash
#
# Demo runner script for Multi-Service Network SDN
# Author: Amirreza Inanloo
# Date: 2025-06-05

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${GREEN}$1${NC}"
}

print_warning() {
    echo -e "${YELLOW}$1${NC}"
}

print_error() {
    echo -e "${RED}$1${NC}"
}

# Check if running with sudo
if [ "$EUID" -ne 0 ]; then 
    print_error "Please run with sudo"
    exit 1
fi

# Banner
echo "=== Multi-Service Network SDN Demo ==="
echo

# Clean up previous instances
print_info "Cleaning up previous instances..."
mn -c > /dev/null 2>&1
killall -9 iperf tcpdump ovs-controller controller 2>/dev/null

# Create necessary directories
mkdir -p logs pcaps results

# Demo menu
echo "Select demo option:"
echo "1) Simple connectivity test"
echo "2) Quick QoS demonstration (30 seconds)"
echo "3) Full experiment suite (5 minutes)"
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        print_info "Running simple connectivity test..."
        python3 -c "
import sys
sys.path.append('src')
from network_topology import test_connectivity
from mininet.log import setLogLevel
setLogLevel('info')
test_connectivity()
"
        ;;
    
    2)
        print_info "Running quick QoS demonstration..."
        python3 run_experiment.py --demo
        ;;
    
    3)
        print_warning "This will run multiple experiments and take approximately 5 minutes."
        read -p "Continue? (y/n): " confirm
        if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
            print_info "Running full experiment suite..."
            python3 run_experiment.py --all --duration 60
        else
            print_info "Cancelled."
            exit 0
        fi
        ;;
    
    *)
        print_error "Invalid choice"
        exit 1
        ;;
esac

# Post-run information
echo
print_info "Demo completed!"
echo "Check the following directories for results:"
echo "  - logs/    : Traffic generation logs"
echo "  - pcaps/   : Packet capture files"
echo "  - results/ : Analysis graphs and reports"

# Cleanup
print_info "Cleaning up..."
mn -c > /dev/null 2>&1
