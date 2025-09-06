#!/usr/bin/env python3
"""
Traffic Generator for Multi-Service Network
Author: Amirreza Inanloo
Date: 2025-06-05
"""

import time
import random
import subprocess
import threading
import os
from datetime import datetime

class TrafficGenerator:
    def __init__(self, net, hosts):
        self.net = net
        self.hosts = hosts
        self.traffic_threads = []
        self.stop_event = threading.Event()
        self.log_dir = "logs"
        os.makedirs(self.log_dir, exist_ok=True)
        
    def generate_web_traffic(self, src, dst, duration):
        """Generate HTTP-like traffic pattern"""
        log_file = f"{self.log_dir}/web_traffic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        with open(log_file, 'w') as f:
            f.write(f"Web Traffic Log - {src.name} to {dst.name}\n")
            f.write("=" * 50 + "\n")
            
            start_time = time.time()
            while time.time() - start_time < duration and not self.stop_event.is_set():
                # Simulate HTTP request/response pattern
                request_size = random.randint(100, 1000)  # bytes
                response_size = random.randint(1000, 100000)  # bytes
                
                # Send request
                cmd = f"ping -c 1 -s {request_size} {dst.IP()}"
                result = src.cmd(cmd)
                f.write(f"Request sent: {request_size} bytes\n")
                
                # Simulate processing delay
                time.sleep(random.uniform(0.01, 0.1))
                
                # Simulate response
                f.write(f"Response size: {response_size} bytes\n")
                
                # Think time between requests
                time.sleep(random.uniform(0.5, 2.0))
    
    def generate_video_traffic(self, src, dst, duration):
        """Generate video streaming traffic pattern"""
        log_file = f"{self.log_dir}/video_traffic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        with open(log_file, 'w') as f:
            f.write(f"Video Traffic Log - {src.name} to {dst.name}\n")
            f.write("=" * 50 + "\n")
            
            # Start iperf UDP stream to simulate video
            dst.cmd(f"iperf -s -u -p 5004 &")
            time.sleep(1)
            
            # Video bitrates (Mbps)
            bitrates = {
                '480p': 2.5,
                '720p': 5,
                '1080p': 8,
                '4k': 25
            }
            
            quality = '720p'
            bitrate = bitrates[quality]
            
            f.write(f"Starting video stream at {quality} ({bitrate} Mbps)\n")
            
            # Start streaming
            cmd = f"iperf -c {dst.IP()} -u -b {bitrate}M -t {duration} -p 5004"
            src.sendCmd(cmd)
            
            # Monitor and log
            start_time = time.time()
            while time.time() - start_time < duration and not self.stop_event.is_set():
                # Simulate adaptive bitrate changes
                if random.random() < 0.1:  # 10% chance to change quality
                    quality = random.choice(list(bitrates.keys()))
                    bitrate = bitrates[quality]
                    f.write(f"Quality changed to {quality} ({bitrate} Mbps)\n")
                
                time.sleep(1)
            
            # Stop streaming
            src.waitOutput()
            dst.cmd("killall iperf 2>/dev/null")
    
    def generate_iot_traffic(self, src, dst, duration):
        """Generate IoT sensor traffic pattern"""
        log_file = f"{self.log_dir}/iot_traffic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        with open(log_file, 'w') as f:
            f.write(f"IoT Traffic Log - {src.name} to {dst.name}\n")
            f.write("=" * 50 + "\n")
            
            start_time = time.time()
            packet_count = 0
            
            while time.time() - start_time < duration and not self.stop_event.is_set():
                # IoT devices send small periodic updates
                data_size = random.randint(50, 200)  # Small sensor data
                
                # Send sensor data
                cmd = f"ping -c 1 -s {data_size} {dst.IP()}"
                result = src.cmd(cmd)
                
                packet_count += 1
                f.write(f"Sensor update {packet_count}: {data_size} bytes\n")
                
                # Wait for next sensor reading (periodic pattern)
                interval = random.uniform(1, 5)  # 1-5 second intervals
                time.sleep(interval)
            
            f.write(f"\nTotal packets sent: {packet_count}\n")
            f.write(f"Average interval: {duration/packet_count:.2f} seconds\n")
    
    def start_all_traffic(self, duration):
        """Start all traffic patterns simultaneously"""
        print("Starting traffic generation...")
        
        # Web traffic
        web_thread = threading.Thread(
            target=self.generate_web_traffic,
            args=(self.hosts['h1'], self.hosts['h2'], duration)
        )
        web_thread.start()
        self.traffic_threads.append(web_thread)
        
        # Video traffic
        video_thread = threading.Thread(
            target=self.generate_video_traffic,
            args=(self.hosts['h3'], self.hosts['h4'], duration)
        )
        video_thread.start()
        self.traffic_threads.append(video_thread)
        
        # IoT traffic
        iot_thread = threading.Thread(
            target=self.generate_iot_traffic,
            args=(self.hosts['h5'], self.hosts['h6'], duration)
        )
        iot_thread.start()
        self.traffic_threads.append(iot_thread)
        
        # Cross-traffic for network stress
        # Web to Video
        cross_thread1 = threading.Thread(
            target=self.generate_cross_traffic,
            args=(self.hosts['h1'], self.hosts['h3'], duration, 'web-to-video')
        )
        cross_thread1.start()
        self.traffic_threads.append(cross_thread1)
        
        # Video to IoT
        cross_thread2 = threading.Thread(
            target=self.generate_cross_traffic,
            args=(self.hosts['h4'], self.hosts['h5'], duration, 'video-to-iot')
        )
        cross_thread2.start()
        self.traffic_threads.append(cross_thread2)
    
    def generate_cross_traffic(self, src, dst, duration, traffic_type):
        """Generate cross-service traffic"""
        log_file = f"{self.log_dir}/cross_traffic_{traffic_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        with open(log_file, 'w') as f:
            f.write(f"Cross Traffic Log - {traffic_type}\n")
            f.write(f"{src.name} to {dst.name}\n")
            f.write("=" * 50 + "\n")
            
            start_time = time.time()
            
            # Use iperf for cross traffic
            port = 6000 + random.randint(1, 100)
            dst.cmd(f"iperf -s -p {port} &")
            time.sleep(1)
            
            # Generate traffic with varying patterns
            bandwidth = random.randint(1, 10)  # Mbps
            f.write(f"Starting cross traffic at {bandwidth} Mbps\n")
            
            cmd = f"iperf -c {dst.IP()} -b {bandwidth}M -t {duration} -p {port}"
            src.sendCmd(cmd)
            
            # Wait for completion
            src.waitOutput()
            dst.cmd("killall iperf 2>/dev/null")
            
            f.write("Cross traffic completed\n")
    
    def stop_all_traffic(self):
        """Stop all traffic generation"""
        print("Stopping traffic generation...")
        self.stop_event.set()
        
        # Wait for all threads to complete
        for thread in self.traffic_threads:
            thread.join(timeout=5)
        
        # Kill any remaining iperf processes
        for host in self.hosts.values():
            host.cmd("killall iperf 2>/dev/null")
            host.cmd("killall ping 2>/dev/null")

def test_traffic_generator():
    """Test traffic generation with a simple topology"""
    from mininet.net import Mininet
    from mininet.node import OVSSwitch
    from mininet.link import TCLink
    
    print("Creating test network...")
    net = Mininet(controller=None, switch=OVSSwitch, link=TCLink)
    
    # Simple topology for testing
    h1 = net.addHost('h1', ip='10.0.0.1/24')
    h2 = net.addHost('h2', ip='10.0.0.2/24')
    s1 = net.addSwitch('s1', failMode='standalone')
    
    net.addLink(h1, s1)
    net.addLink(h2, s1)
    
    net.start()
    
    # Test traffic generation
    hosts = {'h1': h1, 'h2': h2}
    traffic_gen = TrafficGenerator(net, hosts)
    
    print("Generating test traffic for 10 seconds...")
    traffic_gen.generate_web_traffic(h1, h2, 10)
    
    net.stop()
    print("Test completed!")

if __name__ == '__main__':
    test_traffic_generator()
