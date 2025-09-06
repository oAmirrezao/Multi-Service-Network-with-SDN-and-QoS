#!/usr/bin/env python3
"""
Traffic Analyzer for Multi-Service Network
Author: Network Specialist
Date: 2025-09-05
"""

import os
import sys
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import subprocess
import json
from collections import defaultdict

class TrafficAnalyzer:
    def __init__(self, pcap_dir="pcaps", results_dir="results"):
        self.pcap_dir = pcap_dir
        self.results_dir = results_dir
        os.makedirs(self.results_dir, exist_ok=True)
        
    def analyze_pcap(self, pcap_file):
        """Analyze a single pcap file using tcpdump"""
        print(f"Analyzing {pcap_file}...")
        
        # Get basic packet statistics
        cmd = f"tcpdump -r {pcap_file} -nn 2>/dev/null | wc -l"
        result = subprocess.check_output(cmd, shell=True)
        total_packets = int(result.strip())
        
        # Get protocol distribution
        protocols = defaultdict(int)
        
        # Count TCP packets
        cmd = f"tcpdump -r {pcap_file} -nn tcp 2>/dev/null | wc -l"
        result = subprocess.check_output(cmd, shell=True)
        protocols['TCP'] = int(result.strip())
        
        # Count UDP packets
        cmd = f"tcpdump -r {pcap_file} -nn udp 2>/dev/null | wc -l"
        result = subprocess.check_output(cmd, shell=True)
        protocols['UDP'] = int(result.strip())
        
        # Count ICMP packets
        cmd = f"tcpdump -r {pcap_file} -nn icmp 2>/dev/null | wc -l"
        result = subprocess.check_output(cmd, shell=True)
        protocols['ICMP'] = int(result.strip())
        
        # Other packets
        protocols['Other'] = total_packets - sum(protocols.values())
        
        # Get traffic by host
        host_traffic = defaultdict(lambda: {'sent': 0, 'received': 0})
        
        # Parse source IPs
        cmd = f"tcpdump -r {pcap_file} -nn 2>/dev/null | awk '{{print $3}}' | grep -oE '[0-9]+\\.[0-9]+\\.[0-9]+\\.[0-9]+' | sort | uniq -c"
        try:
            result = subprocess.check_output(cmd, shell=True, text=True)
            for line in result.strip().split('\n'):
                if line:
                    parts = line.strip().split()
                    if len(parts) == 2:
                        count = int(parts[0])
                        ip = parts[1]
                        if ip.startswith('10.0.'):
                            host_traffic[ip]['sent'] = count
        except subprocess.CalledProcessError:
            pass
        
        return {
            'total_packets': total_packets,
            'protocols': dict(protocols),
            'host_traffic': dict(host_traffic),
            'filename': os.path.basename(pcap_file)
        }
    
    def analyze_all_pcaps(self):
        """Analyze all pcap files in the directory"""
        results = []
        
        pcap_files = [f for f in os.listdir(self.pcap_dir) if f.endswith('.pcap')]
        
        if not pcap_files:
            print("No pcap files found!")
            return []
        
        for pcap_file in pcap_files:
            full_path = os.path.join(self.pcap_dir, pcap_file)
            try:
                result = self.analyze_pcap(full_path)
                results.append(result)
            except Exception as e:
                print(f"Error analyzing {pcap_file}: {e}")
        
        return results
    
    def generate_protocol_chart(self, results):
        """Generate protocol distribution chart"""
        # Aggregate protocol data
        total_protocols = defaultdict(int)
        
        for result in results:
            for protocol, count in result['protocols'].items():
                total_protocols[protocol] += count
        
        if not total_protocols:
            print("No protocol data to plot")
            return
        
        # Create pie chart
        plt.figure(figsize=(10, 8))
        plt.pie(total_protocols.values(), labels=total_protocols.keys(), 
                autopct='%1.1f%%', startangle=90)
        plt.title('Protocol Distribution Across All Switches')
        plt.savefig(os.path.join(self.results_dir, 'protocol_distribution.png'))
        plt.close()
        
        print(f"Protocol distribution chart saved to {self.results_dir}/protocol_distribution.png")
    
    def generate_traffic_by_switch(self, results):
        """Generate traffic volume by switch"""
        switch_data = {}
        
        for result in results:
            # Extract switch name from filename (e.g., s1_timestamp.pcap -> s1)
            switch_name = result['filename'].split('_')[0]
            switch_data[switch_name] = result['total_packets']
        
        if not switch_data:
            print("No switch data to plot")
            return
        
        # Create bar chart
        plt.figure(figsize=(10, 6))
        switches = list(switch_data.keys())
        packets = list(switch_data.values())
        
        plt.bar(switches, packets, color=['blue', 'green', 'red'])
        plt.xlabel('Switch')
        plt.ylabel('Total Packets')
        plt.title('Traffic Volume by Switch')
        plt.grid(axis='y', alpha=0.3)
        
        plt.savefig(os.path.join(self.results_dir, 'traffic_by_switch.png'))
        plt.close()
        
        print(f"Traffic by switch chart saved to {self.results_dir}/traffic_by_switch.png")
    
    def generate_host_traffic_matrix(self, results):
        """Generate host traffic matrix"""
        # Aggregate host traffic
        host_data = defaultdict(lambda: {'sent': 0, 'received': 0})
        
        for result in results:
            for host, traffic in result['host_traffic'].items():
                host_data[host]['sent'] += traffic['sent']
                host_data[host]['received'] += traffic['received']
        
        if not host_data:
            print("No host traffic data available")
            return
        
        # Create DataFrame
        hosts = sorted(host_data.keys())
        sent_data = [host_data[h]['sent'] for h in hosts]
        received_data = [host_data[h]['received'] for h in hosts]
        
        # Create stacked bar chart
        plt.figure(figsize=(12, 6))
        x = np.arange(len(hosts))
        width = 0.35
        
        plt.bar(x - width/2, sent_data, width, label='Sent', color='skyblue')
        plt.bar(x + width/2, received_data, width, label='Received', color='lightcoral')
        
        plt.xlabel('Host IP')
        plt.ylabel('Packet Count')
        plt.title('Traffic by Host')
        plt.xticks(x, hosts, rotation=45)
        plt.legend()
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        
        plt.savefig(os.path.join(self.results_dir, 'host_traffic.png'))
        plt.close()
        
        print(f"Host traffic chart saved to {self.results_dir}/host_traffic.png")
    
    def generate_report(self, results):
        """Generate analysis report"""
        report_file = os.path.join(self.results_dir, 'analysis_report.txt')
        
        with open(report_file, 'w') as f:
            f.write("Multi-Service Network Traffic Analysis Report\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Summary statistics
            total_packets = sum(r['total_packets'] for r in results)
            f.write(f"Total packets captured: {total_packets}\n")
            f.write(f"Number of capture files: {len(results)}\n\n")
            
            # Per-switch statistics
            f.write("Per-Switch Statistics:\n")
            f.write("-" * 30 + "\n")
            
            for result in results:
                switch_name = result['filename'].split('_')[0]
                f.write(f"\n{switch_name}:\n")
                f.write(f"  Total packets: {result['total_packets']}\n")
                f.write(f"  Protocol breakdown:\n")
                for protocol, count in result['protocols'].items():
                    percentage = (count / result['total_packets'] * 100) if result['total_packets'] > 0 else 0
                    f.write(f"    {protocol}: {count} ({percentage:.1f}%)\n")
            
            # Service type analysis (based on host IPs)
            f.write("\n\nService Type Analysis:\n")
            f.write("-" * 30 + "\n")
            
            service_traffic = {
                'Web (10.0.1.x)': 0,
                'Video (10.0.2.x)': 0,
                'IoT (10.0.3.x)': 0
            }
            
            for result in results:
                for host, traffic in result['host_traffic'].items():
                    total = traffic['sent'] + traffic['received']
                    if host.startswith('10.0.1.'):
                        service_traffic['Web (10.0.1.x)'] += total
                    elif host.startswith('10.0.2.'):
                        service_traffic['Video (10.0.2.x)'] += total
                    elif host.startswith('10.0.3.'):
                        service_traffic['IoT (10.0.3.x)'] += total
            
            for service, traffic in service_traffic.items():
                f.write(f"{service}: {traffic} packets\n")
            
            f.write("\n\nAnalysis complete. Charts saved in results directory.\n")
        
        print(f"Analysis report saved to {report_file}")
    
    def run_full_analysis(self):
        """Run complete analysis pipeline"""
        print("\n=== Starting Traffic Analysis ===")
        
        # Analyze all pcap files
        results = self.analyze_all_pcaps()
        
        if not results:
            print("No data to analyze!")
            return
        
        # Generate visualizations
        print("\nGenerating visualizations...")
        self.generate_protocol_chart(results)
        self.generate_traffic_by_switch(results)
        self.generate_host_traffic_matrix(results)
        
        # Generate report
        print("\nGenerating report...")
        self.generate_report(results)
        
        print("\n=== Analysis Complete ===")
        print(f"Results saved in {self.results_dir}/")

def main():
    """Main function for standalone execution"""
    analyzer = TrafficAnalyzer()
    analyzer.run_full_analysis()

if __name__ == '__main__':
    main()
