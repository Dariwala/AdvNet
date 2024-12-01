from sklearn import tree
from single_cc.convert import convert as convert_single_cc
from mptcp.convert import convert as mptcp_convert
from mptcp.split_trace import split_trace as split_trace_mptcp
from dchannel.convert import convert as convert_dchannel
import matplotlib.pyplot as plt
import numpy as np
import random
import math

dchannel_bad_hb_good = [
    [295, 164, 7, 2, 19, 14, 2, 11, 9, 2, 8],
[155, 276, 3, 3, 14, 13, 11, 5, 10, 5, 39],
[45, 115, 5, 4, 12, 9, 16, 7, 3, 2, 50],
[186, 180, 7, 7, 21, 3, 17, 19, 1, 3, 49],
[251, 41, 7, 9, 22, 12, 7, 20, 7, 4, 34],
[38, 142, 3, 10, 12, 9, 18, 3, 9, 4, 48],
[103, 298, 10, 9, 20, 17, 3, 17, 7, 5, 32],
[286, 250, 2, 9, 13, 19, 7, 8, 5, 5, 47],
[70, 92, 7, 8, 7, 20, 2, 19, 8, 2, 35],
[46, 215, 10, 4, 3, 16, 6, 20, 8, 2, 6],
[269, 109, 7, 2, 24, 3, 9, 8, 1, 4, 15],
[84, 262, 9, 6, 3, 20, 17, 17, 7, 2, 13],
[152, 72, 10, 7, 13, 12, 20, 4, 5, 5, 17],
[92, 267, 7, 6, 11, 23, 16, 7, 10, 3, 29],
[63, 265, 10, 8, 20, 19, 4, 1, 8, 3, 21],
[207, 231, 7, 6, 6, 13, 19, 18, 6, 2, 10],
[209, 195, 3, 8, 25, 22, 10, 17, 2, 4, 38],
[84, 158, 6, 6, 3, 19, 11, 19, 4, 6, 35],
[107, 53, 9, 10, 3, 11, 9, 20, 7, 4, 7],
[43, 33, 9, 2, 9, 4, 1, 18, 4, 3, 31],
[273, 142, 9, 9, 8, 15, 8, 19, 2, 3, 4],
[188, 81, 8, 9, 10, 8, 15, 19, 8, 4, 7],
[170, 273, 5, 3, 3, 23, 16, 9, 4, 6, 11],
[61, 208, 6, 7, 3, 24, 6, 12, 3, 4, 34],
[48, 83, 6, 7, 21, 23, 16, 9, 8, 6, 43],
[123, 264, 8, 2, 5, 6, 4, 9, 6, 3, 1],
[107, 263, 10, 10, 20, 17, 15, 17, 2, 2, 25],
[124, 71, 6, 5, 9, 17, 6, 2, 7, 2, 37],
[278, 120, 4, 9, 25, 16, 15, 3, 6, 6, 24],
[186, 298, 3, 3, 13, 23, 13, 20, 4, 5, 47],
[104, 239, 3, 7, 10, 23, 3, 14, 8, 2, 3],
[246, 174, 8, 4, 22, 20, 20, 14, 3, 6, 39],
[45, 158, 5, 5, 3, 4, 19, 9, 4, 6, 6],
[48, 189, 6, 6, 10, 5, 19, 7, 5, 4, 18],
[148, 231, 7, 7, 13, 4, 15, 8, 7, 3, 2],
[101, 274, 6, 9, 19, 4, 18, 16, 5, 4, 10],
[175, 284, 2, 8, 5, 5, 7, 6, 3, 2, 14],
[165, 52, 4, 10, 5, 15, 11, 18, 7, 2, 14],
[233, 126, 10, 2, 15, 15, 2, 7, 9, 2, 34],
[280, 97, 2, 6, 13, 21, 11, 7, 9, 5, 8],
[74, 125, 9, 8, 18, 17, 12, 12, 10, 5, 27],
[163, 112, 8, 5, 3, 16, 2, 6, 10, 5, 11],
[34, 92, 7, 7, 8, 5, 19, 10, 5, 4, 47],
[101, 276, 10, 5, 19, 8, 3, 3, 5, 3, 39],
[212, 107, 4, 10, 8, 20, 12, 5, 8, 3, 10],
[173, 78, 4, 5, 22, 20, 15, 11, 2, 3, 35],
[70, 92, 7, 8, 3, 24, 6, 19, 8, 2, 35],
[48, 189, 6, 9, 25, 16, 15, 3, 6, 6, 18],
[107, 53, 9, 10, 3, 11, 9, 20, 4, 4, 7],
[163, 112, 8, 5, 3, 16, 4, 6, 10, 5, 11],
[188, 81, 8, 9, 10, 8, 19, 18, 6, 2, 7],
[212, 107, 4, 9, 22, 12, 7, 20, 7, 4, 10],
[92, 267, 8, 6, 11, 23, 16, 7, 10, 3, 29],
[45, 158, 5, 5, 3, 4, 19, 9, 4, 2, 6],
[101, 284, 2, 8, 5, 5, 7, 6, 5, 4, 10],
[286, 273, 5, 9, 13, 19, 7, 8, 5, 5, 47],
[148, 231, 7, 7, 13, 4, 15, 8, 7, 5, 2],
[207, 231, 7, 6, 6, 13, 11, 5, 10, 2, 10],
[175, 284, 2, 8, 12, 9, 18, 3, 9, 2, 14],
[101, 215, 10, 4, 3, 16, 6, 3, 5, 3, 39],
[84, 262, 7, 7, 21, 3, 17, 17, 7, 2, 13],
[107, 33, 9, 2, 9, 4, 1, 18, 4, 3, 7],
[123, 264, 8, 2, 5, 6, 4, 9, 4, 6, 1],
[148, 231, 7, 7, 13, 4, 19, 9, 4, 3, 2],
[249, 142, 9, 9, 8, 4, 8, 6, 10, 3, 3],
[280, 97, 5, 10, 17, 15, 11, 6, 9, 5, 8],
[84, 158, 6, 6, 10, 8, 11, 19, 4, 6, 35],
[104, 239, 3, 7, 10, 5, 3, 14, 8, 2, 3],
[126, 107, 4, 8, 8, 16, 12, 5, 8, 3, 10],
[61, 208, 6, 7, 7, 20, 2, 12, 3, 4, 34],
[278, 120, 8, 8, 10, 16, 19, 7, 7, 4, 24],
[234, 72, 10, 7, 13, 11, 20, 1, 2, 5, 17],
[84, 158, 6, 6, 3, 19, 11, 19, 7, 6, 35],
[123, 264, 8, 2, 5, 6, 2, 9, 6, 3, 1],
[207, 231, 7, 6, 6, 13, 15, 19, 8, 4, 10],
[251, 280, 7, 6, 8, 20, 12, 5, 8, 3, 34],
[165, 52, 2, 10, 5, 15, 11, 18, 7, 2, 14],
[124, 71, 6, 5, 9, 17, 6, 2, 7, 6, 37],
[175, 274, 6, 9, 5, 4, 18, 16, 3, 5, 14]
]

hb_bad_dchannel_good = [
    [153, 264, 8, 5, 25, 10, 16, 4, 1, 2, 23],
[230, 75, 3, 2, 16, 20, 1, 3, 2, 2, 19],
[171, 44, 9, 3, 18, 14, 5, 1, 1, 3, 8],
[119, 109, 2, 3, 23, 18, 4, 9, 1, 5, 14],
[153, 142, 9, 5, 25, 10, 16, 4, 1, 2, 23],
[246, 44, 9, 3, 18, 14, 5, 1, 1, 3, 39],
[119, 109, 2, 3, 20, 19, 4, 9, 1, 5, 14],
[234, 109, 7, 2, 24, 11, 9, 1, 2, 4, 15],
[171, 44, 9, 3, 18, 14, 5, 1, 1, 5, 8],
[152, 75, 3, 2, 16, 20, 1, 4, 5, 5, 17],
[269, 109, 7, 2, 19, 14, 9, 8, 1, 4, 15],
[233, 126, 10, 2, 15, 15, 2, 7, 1, 2, 34],
[173, 78, 4, 5, 22, 20, 4, 9, 1, 3, 35]
]

def preprocess_single_cc(trace):
    a, b, c, d = convert_single_cc(trace)
    return a + b + c + [d]

def preprocess_mptcp_trace(trace):
    bandwidths_1, latencies_1, durations, bandwidths_2, latencies_2, queue_length = split_trace_mptcp(trace)
    return bandwidths_1 + latencies_1 + bandwidths_2 + latencies_2 + durations + [queue_length]

def analyze_tree(tree, threshold, feature_names):
    current_node = 0 #0 is the root
    total = tree.tree_.value[current_node][0][0]
    feature_indices = []
    operations = []
    thresholds = []
    while True:
        samples = tree.tree_.value[current_node][0]
        feature = tree.tree_.feature[current_node]
        thresh = tree.tree_.threshold[current_node]
        feature_indices.append(feature)
        thresholds.append(thresh)
        left_child = tree.tree_.children_left[current_node]
        right_child = tree.tree_.children_right[current_node]

        if left_child != -1 and tree.tree_.value[left_child][0][0] / total > threshold:
            current_node = left_child
            operations.append("le")
            print(samples[0], feature, feature_names[feature], thresh, "le")
            thresholds[-1] = int(thresholds[-1])
        elif right_child != -1 and tree.tree_.value[right_child][0][0] / total > threshold:
            current_node = right_child
            operations.append("g")
            print(samples[0], feature, feature_names[feature], thresh, "g")
            thresholds[-1] = math.ceil(thresholds[-1])
        else:
            break
    # print(operations)
    return operations, feature_indices[:-1], thresholds[:-1]

def plot(x_org, x_scaled, y, feature_names, important_feature_indices, scale_factor):
    clf = tree.DecisionTreeClassifier()
    clf = clf.fit(x_scaled, y)
    operations, feature_indices, thresholds = analyze_tree(clf, 0.5, feature_names)
    # Apply the replacement
    replace_scaled_thresholds(clf, x_np, x_scaled, important_feature_indices, scale_factor)
    plt.figure(figsize=(15,16))
    tree.plot_tree(clf, feature_names=feature_names, fontsize=10, max_depth=5)
    # Adjust the spacing
    plt.subplots_adjust(bottom=0.4)  # Increase the bottom space (adjust the value as needed)
    # Save the combined plot to a PDF file
    # plt.savefig("Plots/pattern_bbr_2_timesteps_1.pdf", format='pdf', bbox_inches='tight')
    # plt.show()
    return feature_indices, operations, thresholds

# Replace the scaled values with original values in the tree's decision thresholds
def replace_scaled_thresholds(tree, original_data, scaled_data, feature_indices, scale_factor):
    for i in range(tree.tree_.node_count):
        feature = tree.tree_.feature[i]
        if feature in feature_indices:
            # Find the original value corresponding to the scaled threshold
            scaled_threshold = tree.tree_.threshold[i]
            original_threshold = scaled_threshold / scale_factor
            tree.tree_.threshold[i] = original_threshold

def generate_random_traces_from_extracted_pattern(feature_indices, operations, thresholds, lower_bound, upper_bound, use_pattern):
    random.seed(1)
    if use_pattern:
        for i in range(len(feature_indices)):
            if operations[i] == 'g':
                lower_bound[feature_indices[i]] = thresholds[i]
            elif operations[i] == 'le':
                upper_bound[feature_indices[i]] = thresholds[i]
    print(lower_bound, upper_bound)
    traces = []
    for _ in range(100):
        trace = []
        for i in range(len(lower_bound)):
            trace.append(random.randint(lower_bound[i], upper_bound[i]))
        traces.append(trace)
    return traces

if __name__ == "__main__":
    # x, y = preprocess()
    # plot(x, y)
    x = []
    y = []
    zeros = []
    ones = []
    file = "sptcp_reno_vs_cubic_2"
    use_pattern = True
    with open("patterns/"+file) as f:
        lines = f.readlines()
        for line in lines:
            line = line.replace(" ", "")[1:-1]
            trace = line.split("]")[0].split(",")
            score = float(line.split("]")[1])
            trace = [int(t) for t in trace]

            if score < 0:
                # x.append(preprocess_single_cc(trace))
                x.append(preprocess_mptcp_trace(mptcp_convert(trace)))
                # x.append(convert_dchannel(trace))
                y.append(1)
                zeros.append(0)
            elif score > 0.4:
                # x.append(preprocess_single_cc(trace))
                x.append(preprocess_mptcp_trace(mptcp_convert(trace)))
                # x.append(convert_dchannel(trace))
                # if x[-1][0] > 750:
                print(x[-1])
                y.append(0)
                ones.append(1)
    print(len(zeros), len(ones))
    # feature_names = [
    #     "bandwidth_1",
    #     "bandwidth_2",
    #     "latency_1",
    #     "latency_2",
    #     "duration_1",
    #     "duration_2",
    #     "queue_length"
    # ]
    feature_names = [
        # "bandwidth_1_1",
        "bandwidth_1_2",
        "latency_1_1",
        "latency_1_2",
        "bandwidth_2_1",
        "bandwidth_2_2",
        "latency_2_1",
        "latency_2_2",
        "duration_1",
        "duration_2",
        "queue_length"
    ]
    # feature_names = [
    #     "bandwidth_1_1",
    #     "bandwidth_1_2",
    #     "bandwidth_2_1",
    #     "bandwidth_2_2",
    #     "latency_1",
    #     "latency_2",
    #     "duration_1",
    #     "duration_2",
    #     "data_size",
    #     "ll_latency",
    #     "queue_length"
    # ]    # Scale important features
    important_feature_indices = [1, 2]  # Indices of important features
    scale_factor = 1

    x_np = np.array(x)
    # x_np = np.delete(x_np, 10, axis=1)
    # x_np = np.delete(x_np, 8, axis=1)
    # x_np = np.delete(x_np, 7, axis=1)
    # x_np = np.delete(x_np, 6, axis=1)
    # x_np = np.delete(x_np, 5, axis=1)
    # x_np = np.delete(x_np, 4, axis=1)
    x_np = np.delete(x_np, 0, axis=1)

    # Scale the important features
    x_scaled = x_np.copy()
    # x_scaled[:, important_feature_indices] *= scale_factor
    feature_indices, operations, thresholds = plot(x_np, x_scaled, y, feature_names, important_feature_indices, scale_factor)

    # traces = generate_random_traces_from_extracted_pattern(feature_indices, operations, thresholds, [500, 500, 1, 1, 500, 500, 100], [10000, 10000, 30, 30, 2000, 2000, 10000], use_pattern)
    # traces = generate_random_traces_from_extracted_pattern(feature_indices, operations, thresholds, [500, 500, 5, 5, 500, 500, 5, 5, 500, 500, 100], [60000, 60000, 100, 100, 60000, 60000, 100, 100, 2500, 2500, 5000], use_pattern)
    # traces = generate_random_traces_from_extracted_pattern(feature_indices, operations, thresholds, [500, 500, 5, 5, 1, 1, 1, 1, 500, 500, 100], [60000, 60000, 100, 100, 1, 1, 1, 1, 2500, 2500, 5000], use_pattern)
    # traces = generate_random_traces_from_extracted_pattern(feature_indices, operations, thresholds, [15000, 15000, 1000, 1000, 5, 5, 5, 5, 50, 2, 100], [150000, 150000, 5000, 5000, 125, 125, 5, 5, 500, 10, 5000])

    # with open("patterns/"+file+"_random_traces", "w") as f:
    #     for trace in traces:
    #         print(trace, file = f)