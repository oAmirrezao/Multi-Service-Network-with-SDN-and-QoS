#!/bin/bash
#
# Debug and setup verification script
# Author: Amirreza Inanloo
# Date: 2025-06-05

echo "=== Multi-Service Network SDN Setup Verification ==="
echo

# Check if running with sudo
if [ "$EUID" -ne 0 ]; then 
    echo "ERROR: Please run with sudo"
    exit 1
fi

echo "1. Checking Mininet installation..."
if command -v mn &> /dev/null; then
    echo "   ✓ Mininet is installed"
    mn --version
else
    echo "   ✗ Mininet is NOT installed"
    echo "   Run: sudo apt-get install mininet"
fi

echo
echo "2. Checking Open vSwitch..."
if command -v ovs-vsctl &> /dev/null; then
    echo "   ✓ Open vSwitch is installed"
    ovs-vsctl --version | head -1
else
    echo "   ✗ Open vSwitch is NOT installed"
    echo "   Run: sudo apt-get install openvswitch-switch"
fi

echo
echo "3. Checking Python packages..."
for pkg in mininet matplotlib numpy pandas scapy; do
    if python3 -c "import $pkg" &> /dev/null; then
        echo "   ✓ $pkg is installed"
    else
        echo "   ✗ $pkg is NOT installed"
        echo "   Run: sudo pip3 install $pkg"
    fi
done

echo
echo "4. Checking network tools..."
for tool in tcpdump iperf; do
    if command -v $tool &> /dev/null; then
        echo "   ✓ $tool is installed"
    else
        echo "   ✗ $tool is NOT installed"
        echo "   Run: sudo apt-get install $tool"
    fi
done

echo
echo "5. Checking project structure..."
for dir in src logs pcaps results; do
    if [ -d "$dir" ]; then
        echo "   ✓ Directory $dir exists"
    else
        echo "   ! Creating directory $dir"
        mkdir -p $dir
    fi
done

echo
echo "6. Testing basic Mininet functionality..."
python3 -c "
from mininet.net import Mininet
from mininet.node import OVSSwitch
from mininet.link import TCLink
from mininet.log import setLogLevel
setLogLevel('error')
net = Mininet(controller=None, switch=OVSSwitch, link=TCLink)
h1 = net.addHost('h1')
h2 = net.addHost('h2')
s1 = net.addSwitch('s1', failMode='standalone')
net.addLink(h1, s1)
net.addLink(h2, s1)
net.start()
result = net.pingPair()
net.stop()
if result == 0.0:
    print('   ✓ Mininet test successful')
else:
    print('   ✗ Mininet test failed')
"

echo
echo "=== Setup verification complete ==="
