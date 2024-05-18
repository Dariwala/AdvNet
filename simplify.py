import argparse
from Simplify.single_cc_simplify import SingleCCSimplify
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--trace', nargs='+', type=int, default=[4000,20,3000], help='Trace to simplify')
    parser.add_argument('--ref', type=str, default="cubic", help='Reference algorithm')
    parser.add_argument('--mpd', type=float, default=0.1, help='Maximum relative performance decrease')
    parser.add_argument('--pc', type=float, default=0.1, help='Minimum performance to complexity ratio')
    args = parser.parse_args()
    os.system("iperf -s &")
    
    simplify = SingleCCSimplify(args.trace, args.pc, args.mpd, args.ref)

    simplified_trace, p_score, c_score = simplify.simplify()
    print(simplified_trace, p_score, c_score)
    
