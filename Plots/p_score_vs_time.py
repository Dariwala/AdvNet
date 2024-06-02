import argparse
import pickle
import matplotlib.pyplot as plt

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--type', type=str, default="advnet")
    parser.add_argument('--alg', type=str, default="GA")
    parser.add_argument('--timesteps', type=int, default=6)
    parser.add_argument('--fuzzing', action='store_true', help='Whether to enable link fuzzing of cc-fuzz or not')
    parser.add_argument('--ref', type=str, default="cubic", help='Reference algorithm')
    args = parser.parse_args()

    plt.figure(figsize=(10, 5))

    for seed in range(1, 4):
        file = "score_across_time_"+args.alg+"_"+args.ref+"_"+str(seed)+"_"+str(args.timesteps)+"_timesteps_"+args.type
        with open("../results/"+file, 'rb') as f:
            score_acorss_time = pickle.load(f)
            x_values = [point[0] for point in score_acorss_time]
            y_values = [point[1] for point in score_acorss_time]

            plt.plot(x_values, y_values)
    # Add title and labels
    plt.title('Plot of Two Sets of (x, y) Pairs')
    plt.xlabel('x-axis')
    plt.ylabel('y-axis')
    plt.show()