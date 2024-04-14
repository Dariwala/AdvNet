import argparse
from single_cc.evaluate import evaluate
import os, subprocess

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--type', type=int, default=0, help="0 for single_cc")
    args = parser.parse_args()

    trace = [1000,1200,10,8,1000,1000]
    if args.type == 0:
        # server_process = subprocess.Popen(['iperf', '-s'], stdout=subprocess.PIPE, text=True)
        os.system("iperf -s &")
        evaluate(trace, "cubic", "reno")
    
    os.system("rm traces/*")
    os.system("rm temp")
    os.system("pkill -9 iperf")