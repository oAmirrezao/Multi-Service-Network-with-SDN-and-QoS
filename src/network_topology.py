#!/usr/bin/env python3
"""
Multi-Service Network Topology with SDN and QoS
Author: Amirreza Inanloo
Date: 2025-06-05
"""

from mininet.net import Mininet
from mininet.node import OVSSwitch, RemoteController
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel, info, error
import time
import os
import subprocess
from datetime import datetime

class MultiServiceNetwork:
    def __init__(self):
        self.net = None
        self.hosts = {}
        self.switches = {}
        self.links = []
        
    def create_topology(self):
        """Create the multi-service network topology"""
        info('*** Creating Multi-Service Network\n')
        
        # Initialize Mininet with a simple controller
        self.net = Mininet(controller=None, 
                          link=TCLink, 
                          switch=OVSSwitch,
                          autoSetMacs=True,
                          autoStaticArp=True)  # Important for ARP resolution
        
        # Add switches
        info('*** Adding Switches\n')
        self.switches['s1'] = self.net.addSwitch('s1', dpid='0000000000000001')
        self.switches['s2'] = self.net.addSwitch('s2', dpid='0000000000000002')
        self.switches['s3'] = self.net.addSwitch('s3', dpid='0000000000000003')
        
        # Add hosts - all in same subnet for simplicity
        info('*** Adding Hosts\n')
        # Web servers
        self.hosts['h1'] = self.net.addHost('h1', ip='10.0.0.1/24')
        self.hosts['h2'] = self.net.addHost('h2', ip='10.0.0.2/24')
        
        # Video streaming servers
        self.hosts['h3'] = self.net.addHost('h3', ip='10.0.0.3/24')
        self.hosts['h4'] = self.net.addHost('h4', ip='10.0.0.4/24')
        
        # IoT devices
        self.hosts['h5'] = self.net.addHost('h5', ip='10.0.0.5/24')
        self.hosts['h6'] = self.net.addHost('h6', ip='10.0.0.6/24')
        
        # Create links
        info('*** Creating Links\n')
        # Web servers to S1
        self.links.append(self.net.addLink(self.hosts['h1'], self.switches['s1'],
                                          bw=100, delay='1ms', loss=0))
        self.links.append(self.net.addLink(self.hosts['h2'], self.switches['s1'],
                                          bw=100, delay='1ms', loss=0))
        
        # Video servers to S2
        self.links.append(self.net.addLink(self.hosts['h3'], self.switches['s2'],
                                          bw=1000, delay='2ms', loss=0))
        self.links.append(self.net.addLink(self.hosts['h4'], self.switches['s2'],
                                          bw=1000, delay='2ms', loss=0))
        
        # IoT devices to S3
        self.links.append(self.net.addLink(self.hosts['h5'], self.switches['s3'],
                                          bw=100, delay='5ms', loss=0))
        self.links.append(self.net.addLink(self.hosts['h6'], self.switches['s3'],
                                          bw=100, delay='5ms', loss=0))
        
        # Inter-switch links
        self.links.append(self.net.addLink(self.switches['s1'], self.switches['s2'],
                                          bw=1000, delay='1ms', loss=0))
        self.links.append(self.net.addLink(self.switches['s2'], self.switches['s3'],
                                          bw=100, delay='10ms', loss=0.1))
        self.links.append(self.net.addLink(self.switches['s1'], self.switches['s3'],
                                          bw=10, delay='20ms', loss=0.5))
    
    def configure_switches(self):
        """Configure switches for basic L2 forwarding"""
        info('*** Configuring switches\n')
        for switch in self.switches.values():
            # Set switches to operate in standalone mode (L2 learning switch)
            switch.cmd('ovs-vsctl set-fail-mode', switch.name, 'standalone')
            # Enable STP to prevent loops
            switch.cmd('ovs-vsctl set bridge', switch.name, 'stp_enable=true')
    
    def apply_qos_policies(self):
        """Apply QoS policies to the network"""
        info('*** Applying QoS Policies\n')
        
        # QoS for web traffic (High priority)
        for host in ['h1', 'h2']:
            h = self.hosts[host]
            for intf in h.intfList():
                if intf.name != 'lo':
                    # Set high priority queue
                    h.cmd(f'tc qdisc add dev {intf} root handle 1: htb default 30')
                    h.cmd(f'tc class add dev {intf} parent 1: classid 1:1 htb rate 100mbit')
                    h.cmd(f'tc class add dev {intf} parent 1:1 classid 1:10 htb rate 80mbit ceil 100mbit prio 1')
                    
        # QoS for video traffic (Medium priority)
        for host in ['h3', 'h4']:
            h = self.hosts[host]
            for intf in h.intfList():
                if intf.name != 'lo':
                    h.cmd(f'tc qdisc add dev {intf} root handle 1: htb default 30')
                    h.cmd(f'tc class add dev {intf} parent 1: classid 1:1 htb rate 1000mbit')
                    h.cmd(f'tc class add dev {intf} parent 1:1 classid 1:20 htb rate 800mbit ceil 1000mbit prio 2')
        
        # QoS for IoT traffic (Low priority)
        for host in ['h5', 'h6']:
            h = self.hosts[host]
            for intf in h.intfList():
                if intf.name != 'lo':
                    h.cmd(f'tc qdisc add dev {intf} root handle 1: htb default 30')
                    h.cmd(f'tc class add dev {intf} parent 1: classid 1:1 htb rate 100mbit')
                    h.cmd(f'tc class add dev {intf} parent 1:1 classid 1:30 htb rate 50mbit ceil 100mbit prio 3')
    
    def start_network(self, qos_enabled=False, routing='none'):
        """Start the network with specified configuration"""
        self.create_topology()
        
        info('*** Starting network\n')
        self.net.start()
        
        # Configure switches
        self.configure_switches()
        
        # Wait for network initialization and STP convergence
        info('*** Waiting for STP convergence\n')
        time.sleep(5)
        
        if qos_enabled:
            self.apply_qos_policies()
        
        return self.net
    
    def stop_network(self):
        """Stop the network"""
        if self.net:
            info('*** Stopping network\n')
            self.net.stop()

def test_connectivity():
    """Test basic connectivity between hosts"""
    print("\n=== Testing Connectivity ===")
    mn = MultiServiceNetwork()
    net = mn.start_network()
    
    # Wait a bit more for network to stabilize
    print("Waiting for network to stabilize...")
    time.sleep(2)
    
    # Test ping between different service types
    print("\nTesting Web Servers (h1 -> h2):")
    h1 = mn.hosts['h1']
    h2 = mn.hosts['h2']
    result = h1.cmd(f'ping -c 4 {h2.IP()}')
    print(result)
    
    print("\nTesting Video Servers (h3 -> h4):")
    h3 = mn.hosts['h3']
    h4 = mn.hosts['h4']
    result = h3.cmd(f'ping -c 4 {h4.IP()}')
    print(result)
    
    print("\nTesting IoT Devices (h5 -> h6):")
    h5 = mn.hosts['h5']
    h6 = mn.hosts['h6']
    result = h5.cmd(f'ping -c 4 {h6.IP()}')
    print(result)
    
    print("\nTesting Cross-Service (h1 -> h3):")
    h1 = mn.hosts['h1']
    h3 = mn.hosts['h3']
    result = h1.cmd(f'ping -c 4 {h3.IP()}')
    print(result)
    
    # Test all pairs
    print("\nTesting all-to-all connectivity:")
    net.pingAll()
    
    # Show switch information
    print("\nSwitch information:")
    for sw_name, switch in mn.switches.items():
        print(f"\n{sw_name}:")
        print(switch.cmd('ovs-vsctl show'))
    
    mn.stop_network()

def run_experiment(qos_enabled=False, routing='none', duration=60):
    """Run network experiment with specified parameters"""
    print(f"\n=== Starting Mininet Topology (QoS: {qos_enabled}, Routing: {routing}) ===")
    
    mn = MultiServiceNetwork()
    net = mn.start_network(qos_enabled=qos_enabled, routing=routing)
    
    print("Waiting for network to initialize...")
    time.sleep(5)
    
    # Start monitoring
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    pcap_dir = "pcaps"
    os.makedirs(pcap_dir, exist_ok=True)
    
    # Start packet capture on switches
    print("Starting packet captures...")
    tcpdump_procs = []
    for sw_name in mn.switches:
        pcap_file = f"{pcap_dir}/{sw_name}_{timestamp}.pcap"
        sw = mn.switches[sw_name]
        proc = sw.popen(['tcpdump', '-i', 'any', '-w', pcap_file], 
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        tcpdump_procs.append(proc)
    
    # Generate traffic
    print(f"Generating traffic for {duration} seconds...")
    
    # Start web traffic (h1 -> h2)
    h1, h2 = mn.hosts['h1'], mn.hosts['h2']
    h2.cmd('iperf -s -p 5001 &')
    h1.cmd(f'iperf -c {h2.IP()} -p 5001 -t {duration} &')
    
    # Start video streaming (h3 -> h4)
    h3, h4 = mn.hosts['h3'], mn.hosts['h4']
    h4.cmd('iperf -s -p 5002 -u &')
    h3.cmd(f'iperf -c {h4.IP()} -p 5002 -u -b 500M -t {duration} &')
    
    # Start IoT traffic (h5 -> h6)
    h5, h6 = mn.hosts['h5'], mn.hosts['h6']
    h6.cmd('iperf -s -p 5003 &')
    h5.cmd(f'iperf -c {h6.IP()} -p 5003 -t {duration} -i 10 &')
    
    # Wait for traffic generation to complete
    print("Traffic generation in progress...")
    time.sleep(duration + 5)
    
    # Stop packet captures
    print("Stopping packet captures...")
    for proc in tcpdump_procs:
        proc.terminate()
    
    # Collect statistics
    print("Collecting statistics...")
    stats_file = f"logs/stats_{timestamp}.txt"
    os.makedirs("logs", exist_ok=True)
    
    with open(stats_file, 'w') as f:
        f.write(f"Network Statistics - {timestamp}\n")
        f.write(f"QoS Enabled: {qos_enabled}\n")
        f.write(f"Routing: {routing}\n")
        f.write("=" * 50 + "\n\n")
        
        # Get interface statistics
        for host_name, host in mn.hosts.items():
            f.write(f"\nHost {host_name} statistics:\n")
            stats = host.cmd('ip -s link show')
            f.write(stats)
            f.write("\n")
    
    # Cleanup
    print("Cleaning up...")
    for host in mn.hosts.values():
        host.cmd('killall iperf 2>/dev/null')
    
    mn.stop_network()
    print("Experiment completed!")

if __name__ == '__main__':
    setLogLevel('info')
    
    # Run simple connectivity test
    test_connectivity()
