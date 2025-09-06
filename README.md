# Multi-Service Network with SDN and QoS

A comprehensive demonstration of Software-Defined Networking (SDN) principles with Quality of Service (QoS) implementation for multi-service networks.

## Overview

This project implements a multi-service network topology using Mininet, featuring:
- Web servers (High priority traffic)
- Video streaming servers (Medium priority traffic)
- IoT devices (Low priority traffic)
- QoS policies for traffic differentiation
- Static routing configuration
- Comprehensive traffic analysis

## Architecture

    Web Servers     Video Servers    IoT Devices
      h1 - h2         h3 - h4          h5 - h6
       |   |           |   |            |   |
       +---+           +---+            +---+
          |               |                |
         S1 ------------ S2 ------------- S3
    (Switch 1)      (Switch 2)       (Switch 3)


### Network Details

- **Web Subnet (10.0.1.0/24)**: High-priority HTTP traffic
- **Video Subnet (10.0.2.0/24)**: Medium-priority streaming traffic
- **IoT Subnet (10.0.3.0/24)**: Low-priority sensor data

### Link Specifications

| Link Type | Bandwidth | Delay | Loss |
|-----------|-----------|-------|------|
| Host-Switch (Web) | 100 Mbps | 1ms | 0% |
| Host-Switch (Video) | 1 Gbps | 2ms | 0% |
| Host-Switch (IoT) | 100 Mbps | 5ms | 0% |
| S1-S2 | 1 Gbps | 1ms | 0% |
| S2-S3 | 100 Mbps | 10ms | 0.1% |
| S1-S3 | 10 Mbps | 20ms | 0.5% |

## Installation

### Prerequisites

- Ubuntu 20.04 or later
- Python 3.8+
- Mininet 2.3.0+
- Open vSwitch

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/multi-service-network-sdn.git
cd multi-service-network-sdn
```

2. Install dependencies:
```bash
sudo apt-get update
sudo apt-get install -y mininet openvswitch-switch python3-pip tcpdump iperf wireshark
sudo pip3 install -r requirements.txt
```

3. Make scripts executable:
```bash
chmod +x run_demo.sh
chmod +x debug_setup.sh
```

## Usage

### Quick Start

Run the interactive demo:
```bash
sudo ./run_demo.sh
```

Choose from:
1. Simple connectivity test
2. Quick QoS demonstration (30 seconds)
3. Full experiment suite (5 minutes)

### Manual Experiments

Run specific experiments:
```bash
# Baseline (no QoS, no routing)
sudo python3 run_experiment.py --duration 60

# With QoS enabled
sudo python3 run_experiment.py --qos --duration 60

# With static routing
sudo python3 run_experiment.py --routing static --duration 60

# Full configuration
sudo python3 run_experiment.py --qos --routing static --duration 60
```

## Project Structure

multi-service-network-sdn/
├── src/
│   ├── network_topology.py    # Core network topology
│   ├── traffic_generator.py   # Traffic generation patterns
│   └── traffic_analyzer.py    # Analysis and visualization
├── logs/                      # Traffic generation logs
├── pcaps/                     # Packet capture files
├── results/                   # Analysis results and graphs
├── run_demo.sh               # Interactive demo script
├── run_experiment.py         # Main experiment runner
├── debug_setup.sh            # Setup verification script
├── requirements.txt          # Python dependencies
└── README.md                 # This file


## Results

### Traffic Analysis

The system generates comprehensive analysis including:
- Protocol distribution charts
- Traffic volume by switch
- Per-host traffic patterns
- Service-type traffic breakdown

### QoS Performance

With QoS enabled:
- **Web traffic**: 80% guaranteed bandwidth, Priority 1
- **Video traffic**: 80% guaranteed bandwidth, Priority 2
- **IoT traffic**: 50% guaranteed bandwidth, Priority 3

## Troubleshooting

### Common Issues

1. **Controller not found**: The system runs without an SDN controller using standalone OVS switches.

2. **Permission denied**: Always run with `sudo`.

3. **Module not found**: Install missing modules with `pip3 install <module>`.

4. **Cleanup needed**: Run `sudo mn -c` to clean up previous instances.

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Network Specialist - 2025-09-05

## Acknowledgments

- Mininet project for the network emulation platform
- Open vSwitch for virtual switching capabilities
