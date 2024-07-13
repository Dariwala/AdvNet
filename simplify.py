import argparse
from Simplify.single_cc_simplify import SingleCCSimplify
from Simplify.mptcp_simplify import MpTcpSimplify
import os
from mptcp.convert import convert

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--type', type=int, default=1, help="0 for single_cc, 1 for mptcp")
    parser.add_argument('--trace', nargs='+', type=int, default=[4000,20,3000], help='Trace to simplify')
    parser.add_argument('--ref', type=str, default="cubic", help='Reference algorithm')
    parser.add_argument('--mpd', type=float, default=0.1, help='Maximum relative performance decrease')
    parser.add_argument('--pc', type=float, default=0.1, help='Minimum performance to complexity ratio')
    parser.add_argument('--convert', action='store_true', help='Whether to convert the trace to actual values')
    parser.add_argument('--mptcp_type', type=int, default=2, help='1 for mptcp vs tcp, 2 for mptcp vs baseline, 3 for mptcp one vs two links')
    parser.add_argument('--kernel', type=str, default=6, help='5/6 for kernel version 5/6.4.x')
    args = parser.parse_args()
    os.system("iperf -s &")
    if args.type == 0:
        simplify = SingleCCSimplify(args.trace, args.pc, args.mpd, args.ref)
    elif args.type == 1:
        if args.convert:
            args.trace = convert(args.trace, True)
        simplify = MpTcpSimplify(args.trace, args.pc, args.mpd, args.ref, args.kernel, args.mptcp_type)

    simplified_trace, p_score, c_score, initial_p_score, initial_c_score = simplify.simplify()
    with open("simplification_results", "a") as f:
        print("Reference:", args.ref, file=f)
        print("Initial trace:", args.trace, file = f)
        print("Initial p_score:", initial_p_score, file=f)
        print("Initial c_score:", initial_c_score, file=f)
        print("Simplified trace:", simplified_trace, file=f)
        print("Simplified p_score:", p_score, file=f)
        print("Simplified c_score:", c_score, file=f)
    os.system("pkill -9 iperf")
    os.system("rm traces/*")
    
