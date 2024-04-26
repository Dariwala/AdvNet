import argparse
from single_cc.evaluate import evaluate

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--trace', nargs='+', type=int, default=[4000,20,3000], help='Trace to evaluate when alg=2')
    parser.add_argument('--ref', type=str, default="cubic", help='Reference algorithm')
    args = parser.parse_args()

    score = evaluate(args.trace, args.ref, 1, True)
    print(score)