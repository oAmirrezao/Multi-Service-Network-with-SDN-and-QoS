#!/usr/bin/env python3
"""
Main experiment runner for Multi-Service Network with SDN
Author: Amirreza Inanloo
Date: 2025-06-05
"""

import sys
import os
import time
import argparse
from datetime import datetime

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from network_topology import MultiServiceNetwork, run_experiment
from traffic_generator import TrafficGenerator
from traffic_analyzer import TrafficAnalyzer
from mininet.log import setLogLevel, info, error
from mininet.clean import cleanup

class ExperimentRunner:
    def __init__(self):
        self.network = None
        self.traffic_gen = None
        self.results_dir = "results"
        self.logs_dir = "logs"
        self.pcaps_dir = "pcaps"
        
        # Create directories
        for dir_path in [self.results_dir, self.logs_dir, self.pcaps_dir]:
            os.makedirs(dir_path, exist_ok=True)
    
    def cleanup_previous(self):
        """Clean up any previous Mininet instances"""
        print("Cleaning up previous Mininet instances...")
        cleanup()
        os.system("sudo killall -9 iperf 2>/dev/null")
        os.system("sudo killall -9 tcpdump 2>/dev/null")
        
    def run_single_experiment(self, qos_enabled, routing_type, duration):
        """Run a single experiment with specified parameters"""
        experiment_name = f"{'qos' if qos_enabled else 'no_qos'}_{routing_type}"
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        print("\n" + "="*60)
        print(f"Running Experiment: {experiment_name}")
        print(f"QoS Enabled: {qos_enabled}")
        print(f"Routing Type: {routing_type}")
        print(f"Duration: {duration} seconds")
        print("="*60 + "\n")
        
        try:
            # Run the experiment
            run_experiment(qos_enabled=qos_enabled, routing=routing_type, duration=duration)
            
            # Wait a bit for files to be written
            time.sleep(2)
            
            # Analyze results
            print("\n=== Analyzing Results ===")
            analyzer = TrafficAnalyzer(pcap_dir=self.pcaps_dir, 
                                     results_dir=os.path.join(self.results_dir, experiment_name))
            analyzer.run_full_analysis()
            
        except Exception as e:
            error(f"Error during experiment: {str(e)}\n")
            return False
        
        return True
    
    def run_all_experiments(self, duration=60):
        """Run all experiment combinations"""
        experiments = [
            (False, 'none'),    # Baseline: No QoS, No routing
            (True, 'none'),     # QoS only
            (False, 'static'),  # Static routing only
            (True, 'static'),   # Both QoS and static routing
        ]
        
        print(f"\n=== Running Complete Experiment Suite ===")
        print(f"Total experiments: {len(experiments)}")
        print(f"Duration per experiment: {duration} seconds")
        print(f"Total estimated time: {len(experiments) * (duration + 30)} seconds\n")
        
        results_summary = []
        
        for i, (qos, routing) in enumerate(experiments, 1):
            print(f"\n>>> Experiment {i}/{len(experiments)}")
            
            # Clean up before each experiment
            self.cleanup_previous()
            time.sleep(2)
            
            # Run experiment
            success = self.run_single_experiment(qos, routing, duration)
            results_summary.append({
                'experiment': f"QoS={qos}, Routing={routing}",
                'success': success
            })
            
            # Wait between experiments
            if i < len(experiments):
                print("\nWaiting 10 seconds before next experiment...")
                time.sleep(10)
        
        # Generate summary report
        self.generate_summary_report(results_summary)
    
    def run_demo_experiment(self, duration=30):
        """Run a quick demo experiment"""
        print("\n=== Running Demo Experiment ===")
        print("This will run a single experiment with QoS enabled and static routing")
        print(f"Duration: {duration} seconds\n")
        
        self.cleanup_previous()
        time.sleep(2)
        
        return self.run_single_experiment(qos_enabled=True, 
                                        routing_type='static', 
                                        duration=duration)
    
    def generate_summary_report(self, results_summary):
        """Generate a summary report of all experiments"""
        report_file = os.path.join(self.results_dir, 'experiment_summary.txt')
        
        with open(report_file, 'w') as f:
            f.write("Multi-Service Network SDN Experiment Summary\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("Experiment Results:\n")
            f.write("-" * 30 + "\n")
            
            for result in results_summary:
                status = "SUCCESS" if result['success'] else "FAILED"
                f.write(f"{result['experiment']}: {status}\n")
            
            f.write("\n\nFor detailed results, check individual experiment folders in results/\n")
        
        print(f"\nSummary report saved to {report_file}")

def main():
    parser = argparse.ArgumentParser(description='Run Multi-Service Network SDN Experiments')
    parser.add_argument('--qos', action='store_true', help='Enable QoS policies')
    parser.add_argument('--routing', choices=['none', 'static'], default='none',
                       help='Routing configuration (default: none)')
    parser.add_argument('--duration', type=int, default=60,
                       help='Experiment duration in seconds (default: 60)')
    parser.add_argument('--all', action='store_true',
                       help='Run all experiment combinations')
    parser.add_argument('--demo', action='store_true',
                       help='Run quick demo (30 seconds with QoS and static routing)')
    
    args = parser.parse_args()
    
    # Set Mininet log level
    setLogLevel('info')
    
    # Create experiment runner
    runner = ExperimentRunner()
    
    try:
        if args.demo:
            # Run demo
            runner.run_demo_experiment(duration=30)
        elif args.all:
            # Run all experiments
            runner.run_all_experiments(duration=args.duration)
        else:
            # Run single experiment
            runner.cleanup_previous()
            runner.run_single_experiment(args.qos, args.routing, args.duration)
    
    except KeyboardInterrupt:
        print("\n\nExperiment interrupted by user")
    except Exception as e:
        error(f"\nFatal error: {str(e)}\n")
    finally:
        # Final cleanup
        print("\nPerforming final cleanup...")
        runner.cleanup_previous()
        print("Done!")

if __name__ == '__main__':
    main()
