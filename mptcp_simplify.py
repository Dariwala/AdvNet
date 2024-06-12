import argparse
from Simplify.mptcp_simplify import MpTcpSimplify
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--trace', nargs='+', type=int, default=[4000,20,3000], help='Trace to simplify')
    parser.add_argument('--ref', type=str, default="cubic", help='Reference algorithm')
    parser.add_argument('--mpd', type=float, default=0.1, help='Maximum relative performance decrease')
    parser.add_argument('--pc', type=float, default=0.1, help='Minimum performance to complexity ratio')
    args = parser.parse_args()
    os.system("iperf -s &")
    
    simplify = MpTcpSimplify(args.trace, args.pc, args.mpd, args.ref, "5", 3)

    simplified_trace, p_score, c_score, initial_p_score, initial_c_score = simplify.simplify()
    with open("mptcp_simplification_results", "a") as f:
        print("Reference:", args.ref, file=f)
        print("Initial trace:", args.trace, file = f)
        print("Initial p_score:", initial_p_score, file=f)
        print("Initial c_score:", initial_c_score, file=f)
        print("Simplified trace:", simplified_trace, file=f)
        print("Simplified p_score:", p_score, file=f)
        print("Simplified c_score:", c_score, file=f)
    os.system("pkill -9 iperf")
    os.system("rm traces/*")
    
