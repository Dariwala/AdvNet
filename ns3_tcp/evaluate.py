import subprocess
import re
from scoring.scoring import compute_score, SingleCCProtocolScore

def evaluate(trace, ref, tar, debug=False):
    """
    Evaluate two TCP congestion control algorithms on the same trace.
    
    Args:
        ref: String, reference TCP type (e.g., "TcpCubic")
        tar: String, target TCP type to compare (e.g., "TcpBbr")
        trace: Single list containing bandwidths, latencies, and durations
               Format: [b1, b2, ..., bn, l1, l2, ..., ln, d1, d2, ..., dn]
               where n is the number of segments
        debug: Boolean, whether to print debug information
    
    Returns:
        float: The computed score from scoring.compute_score()
    """
    
    # Configuration
    LATENCY_SCALE = 5  # 1 unit = 5 ms
    NS3_PATH = "/Users/shehaba2/Documents/PhD Research/Adversary/ns-3-dev"

    # Determine number of segments (n)
    # The trace should have 3*n elements
    total_length = len(trace)
    
    # Check if the length is divisible by 3
    if total_length % 3 != 0:
        raise ValueError(f"Trace length ({total_length}) must be divisible by 3. "
                        f"Format: [b1,b2,...,bn, l1,l2,...,ln, d1,d2,...,dn]")
    
    n = total_length // 3
    
    # Parse the trace into separate lists
    bandwidths_raw = trace[:n]                    # First n elements
    latencies_raw = trace[n:2*n]                  # Next n elements
    durations_raw = trace[2*n:]                    # Last n elements
    
    if debug:
        print("\n" + "="*60)
        print("PARSED TRACE")
        print("="*60)
        print(f"Number of segments: {n}")
        print(f"Bandwidths (Mbps): {bandwidths_raw}")
        print(f"Latencies (units): {latencies_raw}")
        print(f"Durations (s): {durations_raw}")
    
    # Convert to ns-3 arguments
    bandwidths = []
    latencies = []
    durations = []
    
    for i in range(n):
        bandwidths.append(str(bandwidths_raw[i]) + "Mbps")
        latencies.append(str(latencies_raw[i] * LATENCY_SCALE) + "ms")
        durations.append(str(durations_raw[i]))
    
    if debug:
        print("\n" + "="*60)
        print("NS-3 ARGUMENTS")
        print("="*60)
        print(f"Bandwidths: {bandwidths}")
        print(f"Latencies: {latencies}")
        print(f"Durations: {durations}")
    
    def run_with_tcp_type(tcp_type):
        """Run simulation with specific TCP type and return metrics"""
        
        # Build command with proper -- separator
        cmd = [
            "./ns3", "run",
            "scratch/tcp-dynamic-link",
            "--",
            f"--tcpTypeId={tcp_type}",
            f"--bandwidths={','.join(bandwidths)}",
            f"--latencies={','.join(latencies)}",
            f"--durations={','.join(durations)}"
        ]
        
        if debug:
            print(f"\n--- Running {tcp_type} ---")
            print(f"Command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=NS3_PATH,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            output = result.stdout + result.stderr
            
            if debug:
                print(f"{tcp_type} Output:")
                print(output)
            
            # Parse results using regex
            throughput_match = re.search(r'Overall Throughput:\s+([\d.]+)\s+Mbps', output)
            delay_match = re.search(r'Average Delay:\s+([\d.]+)\s+ms', output)
            
            if throughput_match and delay_match:
                throughput = float(throughput_match.group(1))
                delay = float(delay_match.group(1))
                
                if debug:
                    print(f"\n{tcp_type} Parsed Results:")
                    print(f"  Throughput: {throughput:.2f} Mbps")
                    print(f"  Delay: {delay:.2f} ms")
                
                return throughput, delay
            else:
                if debug:
                    print(f"Failed to parse {tcp_type} ns-3 output")
                return 0, float('inf')
                
        except subprocess.TimeoutExpired:
            if debug:
                print(f"{tcp_type} simulation timed out")
            return 0, float('inf')
        except Exception as e:
            if debug:
                print(f"Error running {tcp_type} simulation: {e}")
            return 0, float('inf')
    
    # Print trace details
    if debug:
        print("\n" + "="*60)
        print("EVALUATION TRACE DETAILS")
        print("="*60)
        print(f"{'Segment':<8} {'Bandwidth':<12} {'Latency':<12} {'Duration':<10}")
        print("-"*42)
        for i in range(n):
            print(f"{i+1:<8} {bandwidths_raw[i]} Mbps      {latencies_raw[i]*LATENCY_SCALE} ms       {durations_raw[i]} s")
        print("="*60)
    
    # Run simulations for both TCP types on the same trace
    ref_throughput, ref_delay = run_with_tcp_type(ref)
    tar_throughput, tar_delay = run_with_tcp_type(tar)
    
    if debug:
        print("\n" + "="*60)
        print(f"RAW RESULTS: {ref} vs {tar}")
        print("="*60)
        print(f"{'Metric':<20} {ref:<15} {tar:<15}")
        print("-"*50)
        print(f"{'Throughput (Mbps)':<20} {ref_throughput:<15.2f} {tar_throughput:<15.2f}")
        print(f"{'Delay (ms)':<20} {ref_delay:<15.2f} {tar_delay:<15.2f}")
        print("="*60)
    
    # Create score objects and compute individual scores
    # Using SingleCCProtocolScore with example weights (adjust as needed)
    scorer = SingleCCProtocolScore(
        wt=0.5,           # weight for throughput
        wl=0.5,           # weight for latency  
        t_ref=max(bandwidths_raw),  # reference throughput from raw values
        l_ref=min(latencies_raw) * LATENCY_SCALE   # reference latency from raw values
    )
    
    # Compute scores for both protocols
    ref_score = scorer.w_sum(ref_throughput, ref_delay)
    tar_score = scorer.w_sum(tar_throughput, tar_delay)
    
    if debug:
        print(f"\nIndividual Scores:")
        print(f"  {ref} score: {ref_score:.4f}")
        print(f"  {tar} score: {tar_score:.4f}")
    
    # Use the compute_score function from scoring.py
    final_score = compute_score([ref_score], [tar_score])
    
    if debug:
        print(f"\nFinal Score (from compute_score): {final_score:.4f}")
        print("="*60)
    
    return final_score

# Example usage
if __name__ == "__main__":
    # Define the trace (same for both TCP types)
    test_trace = [
        [10, 2, 30],  # 10 Mbps, 10 ms, 30s
        [5, 4, 30],   # 5 Mbps, 20 ms, 30s
        [15, 1, 40],  # 15 Mbps, 5 ms, 40s
    ]
    
    # Run with debug output
    score = evaluate(
        ref="TcpCubic",
        tar="TcpBbr", 
        trace=test_trace,
        debug=True
    )
    
    print(f"\nReturned score: {score}")
    
    # Run without debug
    score = evaluate(
        ref="TcpCubic",
        tar="TcpBbr",
        trace=test_trace,
        debug=False
    )
    
    print(f"Silent run score: {score}")