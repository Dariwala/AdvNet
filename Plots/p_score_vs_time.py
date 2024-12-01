import argparse
import pickle
import matplotlib.pyplot as plt

number_of_algs = 2
file_names = [
    [
        "results/score_across_time_ga_olia_10_11_trace_length_mptcp_type_1",
        "results/score_across_time_ga_vegas_10_7_trace_length_advnet"
    ],
    [
        "results/score_across_time_random_olia_10_11_trace_length_mptcp_type_1",
        "results/score_across_time_random_vegas_10_7_trace_length_advnet"
    ]
]

def preprocess(score_across_time):
    print(score_acorss_time)
    i = 0
    while i < len(score_acorss_time):
        time = score_acorss_time[i][0]
        best_score = score_acorss_time[i][1]

        if time > 2 and i != 0:
            score_acorss_time.insert(i, [time - 1, score_acorss_time[i-1][1]])
            i += 1
        i += 1
    score_acorss_time.append([3600, score_acorss_time[-1][1]])
    print(score_acorss_time)

alg_names = ["GA", "RG"]
colors = ["#4285f4", "#ea4335"]
index = 1

if __name__ == "__main__":
    plt.figure(figsize=(14, 8.5))
    scores_across_time = []
    for i in range(number_of_algs):
        with open(file_names[i][index], 'rb') as f:
            score_acorss_time = pickle.load(f)
            preprocess(score_acorss_time)
            scores_across_time.append(score_acorss_time)
        x_values = [point[0] for point in score_acorss_time]
        y_values = [point[1] for point in score_acorss_time]
    # plt.subplot(2, 2, timesteps // 3 - 1)
        plt.plot(x_values, y_values, label=alg_names[i], color=colors[i])
    # plt.title('p_score vs time for '+args.ref+" with "+str(timesteps//3)+" timesteps")
    plt.xlabel('time (seconds)', fontdict={"fontsize":30})
    plt.ylabel('score', fontdict={"fontsize":30})

    plt.tick_params(axis='x', labelsize=28)
    plt.tick_params(axis='y', labelsize=28)

    plt.legend(fontsize = 28)
    plt.tight_layout()
    plt.grid(True, which='both', linestyle='--', linewidth=0.2, color='gray')
    # plt.savefig('Plots/score_comparison_through_time_olia_1_vs_2_links.pdf', format='pdf', bbox_inches='tight')
    plt.savefig('Plots/score_comparison_through_time_vegas_sub_optimality.pdf', format='pdf', bbox_inches='tight')
    plt.show()