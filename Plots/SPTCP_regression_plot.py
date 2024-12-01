import matplotlib.pyplot as plt

protocols = ["cubic",	"reno",	"bbr",	"bic",	"cdg",	"dctcp",	"highspeed",	"htcp",	"hybla",	"illinois",	"lp",	"nv",	"scalable",	"vegas", "veno", "westwood", "yeah"]
mean_score_as_ref = [0.58375,	0.66,	0.4925,	0.70125,	0.524375,	0.668125,	0.6575,	0.693125,	0.853125,	0.68,	0.6875,	0.355625,	0.710625,	0.613125,	0.62875,	0.62,	0.645]
mean_score_as_tar = [0.7946153846,	0.5,	0.9284615385,	0.4638461538,	0.96,	0.5184615385,	0.4723076923,	0.5015384615,	0.2530769231,	0.4807692308,	0.6876923077,	0.9038461538,	0.4869230769,	0.92,	0.4828571429,	0.7164285714,	0.7121428571]


# Plotting
plt.figure(figsize=(10, 6))
plt.scatter(mean_score_as_ref, mean_score_as_tar, color="#ea4335")

# Adding labels
for i, protocol in enumerate(protocols):
    plt.text(mean_score_as_ref[i], mean_score_as_tar[i]-0.02, protocol, fontsize=9, color='#00796b')

# Labels and title
plt.xlabel("Mean Score as reference")
plt.ylabel("Mean Score as target")

plt.grid(color='gray', linestyle='--', linewidth=0.2)
plt.show()