import argparse
from mptcp.evaluate import evaluate

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--mptcp_type', type=int, default=2, help='1 for mptcp vs tcp, 2 for mptcp vs baseline, 3 for mptcp one vs two links')
    parser.add_argument('--kernel', type=str, default=6, help='5/6 for kernel version 5/6.4.x')
    parser.add_argument('--trace', nargs='+', type=int, default=[4000,20,3000], help='Trace to evaluate')
    parser.add_argument('--ref', type=str, default="cubic", help='Reference algorithm')
    args = parser.parse_args()
    score = evaluate(args.trace, args.ref, 1, args.mptcp_type, args.kernel)
    print(score)