"""ns-3 evaluation backend.

Runs the ``scratch/tcp-dynamic-link`` ns-3 scenario for two congestion-control
algorithms over the same time-varying link trace and returns an adversarial
score comparing them. The ns-3 source tree location is read from the
``ADVNET_NS3_PATH`` environment variable (see ``NS3_PATH`` below).
"""

import os
import re
import subprocess

from scoring.scoring import compute_score, SingleCCProtocolScore

# Location of the ns-3 source tree. Override with the ADVNET_NS3_PATH env var.
NS3_PATH = os.environ.get(
    "ADVNET_NS3_PATH",
    "/Users/shehaba2/Documents/PhD Research/Adversary/ns-3-dev",
)


def extract_metric(pattern: str, text: str, cast=float):
    """Return the first regex capture group in ``text`` cast via ``cast``, else None."""
    match = re.search(pattern, text)
    return cast(match.group(1)) if match else None


def evaluate(trace, ref: str, tar: str, debug: bool = False) -> float:
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
    
    # Unit conversions from the integer trace encoding to ns-3 units.
    LATENCY_SCALE = 5   # 1 latency unit = 5 ms
    QUEUE_SCALE = 10    # 1 queue unit = 10 packets

    total_length = len(trace) - 1
    
    # Check if the length is divisible by 3
    if total_length % 3 != 0:
        raise ValueError(f"Trace length ({total_length}) must be divisible by 3. "
                        f"Format: [b1,b2,...,bn, l1,l2,...,ln, d1,d2,...,dn]")
    
    n = total_length // 3
    
    # Parse the trace into separate lists
    bandwidths_raw = trace[:n]                    # First n elements
    latencies_raw = trace[n:2*n]                  # Next n elements
    durations_raw = trace[2*n:]                    # Last n elements
    queue_size_raw = trace[-1]
    
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
    queue_size = str(queue_size_raw * QUEUE_SCALE) + "p"
    
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
            f"--durations={','.join(durations)}",
            f"--queueSize={queue_size}"
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
            
            # Parse results
            throughput = extract_metric(r'Overall Throughput:\s+([\d.]+)', output)
            delay = extract_metric(r'Average Delay:\s+([\d.]+)', output)

            # New metrics
            jitter = extract_metric(r'Average Jitter:\s+([\d.]+)', output)
            loss_rate = extract_metric(r'Loss Rate:\s+([\d.]+)', output)
            
            if throughput is not None and delay is not None:
                if debug:
                    print(f"\n{tcp_type} Parsed Results:")
                    print(f"  Throughput: {throughput:.2f} Mbps")
                    print(f"  Delay: {delay:.2f} ms")
                    print(f"  Jitter: {jitter:.2f} ms" if jitter is not None else "  Jitter: N/A")
                    print(f"  Loss Rate: {loss_rate:.2f}%" if loss_rate is not None else "  Loss Rate: N/A")
                
                return throughput, delay, jitter, loss_rate
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
    ref_throughput, ref_delay, ref_jitter, ref_loss_rate = run_with_tcp_type(ref)
    tar_throughput, tar_delay, tar_jitter, tar_loss_rate = run_with_tcp_type(tar)
    
    if debug:
        print("\n" + "="*60)
        print(f"RAW RESULTS: {ref} vs {tar}")
        print("="*60)
        print(f"{'Metric':<20} {ref:<15} {tar:<15}")
        print("-"*50)
        print(f"{'Throughput (Mbps)':<20} {ref_throughput:<15.2f} {tar_throughput:<15.2f}")
        print(f"{'Delay (ms)':<20} {ref_delay:<15.2f} {tar_delay:<15.2f}")
        print(f"{'Jitter (ms)':<20} {ref_jitter:<15.2f} {tar_jitter:<15.2f}")
        print(f"{'Loss Rate (%)':<20} {ref_loss_rate:<15.2f} {tar_loss_rate:<15.2f}")
        print("="*60)
    
    # Create score objects and compute individual scores
    # Using SingleCCProtocolScore with example weights (adjust as needed)
    scorer = SingleCCProtocolScore(
        wt=0.4,           # weight for throughput
        wl=0.4,           # weight for latency  
        t_ref=50,  
        l_ref=5,
        loss_ref=1
    )
    
    # Compute scores for both protocols
    ref_score = scorer.w_sum(ref_throughput, ref_delay, ref_loss_rate)
    tar_score = scorer.w_sum(tar_throughput, tar_delay, tar_loss_rate)
    # ref_score = 0.4 * (ref_throughput / 50) - 0.4 * (ref_delay / 100) - 0.2 * (ref_loss_rate / 5.0)
    # tar_score = 0.4 * (tar_throughput / 50) - 0.4 * (tar_delay / 100) - 0.2 * (tar_loss_rate / 5.0)
    
    if debug:
        print(f"\nIndividual Scores:")
        print(f"  {ref} score: {ref_score:.4f}")
        print(f"  {tar} score: {tar_score:.4f}")
    
    # Use the compute_score function from scoring.py
    final_score = compute_score([ref_score], [tar_score])
    # final_score = (ref_score - tar_score) / (abs(ref_score) + abs(tar_score) + 1e-6)  # Avoid division by zero
    
    if debug:
        print(f"\nFinal Score (from compute_score): {final_score:.4f}")
        print("="*60)
    
    return final_score

# Example usage
if __name__ == "__main__":
    # Define the trace (same for both TCP types)
    trace_0 = [
        47,9,  # 10 Mbps, 10 ms, 30s
        18,16,   # 5 Mbps, 20 ms, 30s
        6,16,  # 15 Mbps, 5 ms, 40s
        9
    ]

    trace_1 = [
        44,2,  # 10 Mbps, 10 ms, 30s
        17,16,   # 5 Mbps, 20 ms, 30s
        4,8,  # 15 Mbps, 5 ms, 40s
        9
    ]

    trace_2 = [
        24,5,  # 10 Mbps, 10 ms, 30s
        19,13,   # 5 Mbps, 20 ms, 30s
        2,12,  # 15 Mbps, 5 ms, 40s
        1
    ]

    trace_3 = [
        34,47,  # 10 Mbps, 10 ms, 30s
        11,14,   # 5 Mbps, 20 ms, 30s
        1,19,  # 15 Mbps, 5 ms, 40s
        9
    ]

    trace_4 = [
        42,38,  # 10 Mbps, 10 ms, 30s
        11,17,   # 5 Mbps, 20 ms, 30s
        1,22,  # 15 Mbps, 5 ms, 40s
        8
    ]

    trace_5 = [
        34,48,  # 10 Mbps, 10 ms, 30s
        11,13,   # 5 Mbps, 20 ms, 30s
        2,25,  # 15 Mbps, 5 ms, 40s
        7
    ]

    traces = [trace_0, trace_1, trace_2, trace_3, trace_4, trace_5]
    scores = []
    
    for trace in traces:
        score = evaluate(
            ref="TcpNewReno",
            tar="MyTcp", 
            trace=trace,
            debug=True
        )
        scores.append(score)
        print(f"\nReturned score: {score}")
    
    score = max(scores)
    robustness = 1 - score
    print(f"\nFinal robustness score across all traces: {robustness:.4f}")
    
    # Run without debug
    # score = evaluate(
    #     ref="TcpCubic",
    #     tar="TcpBbr",
    #     trace=test_trace,
    #     debug=False
    # )
    
    # print(f"Silent run score: {score}")