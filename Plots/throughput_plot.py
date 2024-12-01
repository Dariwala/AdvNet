import matplotlib.pyplot as plt

def find(x, y, value):
    for i, d in enumerate(x):
        if value <= x[i]:
            return y[i] + 0.1
    else:
        return y[-1] + 0.1
    
def plot_lia_balia(xs, ys_list, latencies_list, ref, tar, timesteps):
    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    
    for i in range(4):
        y1, y2 = ys_list[i][0], ys_list[i][1]
        ax = axes[i//2][i%2]

        ax.plot(xs[i], y1, color="#4285f4", label='Available Bandwidth')
        if i == 0:
            ax.plot(xs[i], y2, color="#ea4335", label='Throughput by '+ref+' Link 1')
        elif i == 1:
            ax.plot(xs[i], y2, color="#ea4335", label='Throughput by '+ref+' Link 2')
        elif i == 2:
            ax.plot(xs[i], y2, color="#ea4335", label='Throughput by '+tar+' Link 1')
        elif i == 3:
            ax.plot(xs[i], y2, color="#ea4335", label='Throughput by '+tar+' Link 2')

        prev_vuj = 0
        if True:
            for j, data in enumerate(latencies_list[i]):
                koti, vuj = data[0], data[1] / 1000
                if i == 0:
                    arrow_pos = 10 if j == 0 else 7.6
                    text_pos = 10.5 if j == 0 else 8.1
                elif i == 1:
                    arrow_pos = 5.1 if j == 0 else 4.5
                    text_pos = 5.3 if j == 0 else 4.8
                elif i == 2:
                    arrow_pos = 10 if j == 0 else 8.1
                    text_pos = 10.5 if j == 0 else 8.6
                elif i == 3:
                    arrow_pos = 5.1 if j == 0 else 4.5
                    text_pos = 5.3 if j == 0 else 4.8
                ax.plot([prev_vuj, prev_vuj + vuj], [find(xs[i], y1, prev_vuj + vuj / 2)+arrow_pos, find(xs[i], y1, prev_vuj + vuj / 2)+arrow_pos], color='#34a853', linestyle='--')
                
                # Add an arrow on the left side
                ax.annotate(
                    '', xy=(prev_vuj, find(xs[i], y1, prev_vuj + vuj / 2)+arrow_pos), xytext=(prev_vuj + 0.1, find(xs[i], y1, prev_vuj + vuj / 2)+arrow_pos),
                    arrowprops=dict(facecolor='#34a853', edgecolor='#34a853', arrowstyle='-|>')
                )

                # Add an arrow on the right side
                ax.annotate(
                    '', xy=(prev_vuj + vuj, find(xs[i], y1, prev_vuj + vuj / 2)+arrow_pos), xytext=(prev_vuj + vuj - 0.1, find(xs[i], y1, prev_vuj + vuj / 2)+arrow_pos),
                    arrowprops=dict(facecolor='#34a853', edgecolor='#34a853', arrowstyle='-|>')
                )
                ax.text(prev_vuj + vuj / 2, find(xs[i], y1, prev_vuj + vuj / 2) + text_pos, str(koti), fontsize=12, color='#34a853')
                prev_vuj += vuj
            
        ax.set_xlabel('Time (seconds)', fontdict={"fontsize":18})
        ax.set_ylabel('Bandwidth/Throughput (Mbps)', fontdict={"fontsize":18})
        
        ax.fill_between(xs[i], y1, color="#4285f4", alpha=0.2)
        ax.fill_between(xs[i], y2, color="#ea4335", alpha=0.1)

        ax.grid(color='gray', linestyle='--', linewidth=0.2)

        ax.plot([], [], color='#34a853', linestyle='--', label='Latency (ms) as text')
        ax.legend()

        # Add subfigure labels
        # ax.text(.1, 1.05, f"({chr(97 + i)})", transform=ax.transAxes, size=16, weight='bold')

    # Set the y-axis to start from 0
    axes[0][0].set_ylim(bottom=0, top = 16)
    axes[0][1].set_ylim(bottom=0, top = 60)
    axes[1][0].set_ylim(bottom=0, top = 16)
    axes[1][1].set_ylim(bottom=0, top = 60)

    axes[0][0].set_xlim(left=0, right = 4.2)
    axes[0][1].set_xlim(left=0, right = 4.2)
    axes[1][0].set_xlim(left=0, right = 4.2)
    axes[1][1].set_xlim(left=0, right = 4.2)
    
    # Automatically adjust subplot parameters to give more space
    plt.tight_layout()

    # Adjust spacing manually if needed
    # plt.subplots_adjust(hspace=0.5)  # Add space between plots
    # Add a common title or caption
    # plt.suptitle("Comparison of Available Bandwidth and Throughput Across Different Configurations", fontsize=16)

    # Save the combined plot to a PDF file
    plt.savefig("Plots/mptcp_"+ref +"_"+tar+"_"+ str(timesteps) + "_timesteps.pdf", format='pdf', bbox_inches='tight')

    # Display the plot
    plt.show()

def plot_olia(xs, ys_list, latencies_list, ref, timesteps):
    fig, axes = plt.subplots(3, 1, figsize=(9, 8.5))  # Create 3 subplots vertically
    
    for i in range(3):
        y1, y2 = ys_list[i][0], ys_list[i][1]
        ax = axes[i]

        ax.plot(xs[i], y1, color="#4285f4", label='Available Bandwidth')
        if i == 0:
            ax.plot(xs[i], y2, color="#ea4335", label='Throughput by '+ref+' Link 1')
        elif i == 1:
            ax.plot(xs[i], y2, color="#ea4335", label='Throughput by '+ref+' Link 2')
        elif i == 2:
            ax.plot(xs[i], y2, color="#ea4335", label='Throughput by '+ref+' with only Link 1')

        prev_vuj = 0
        if True:
            for data in latencies_list[i]:
                koti, vuj = data[0], data[1] / 1000
                if i == 0:
                    arrow_pos = 2
                    text_pos = 3
                elif i == 1:
                    arrow_pos = 0.5
                    text_pos = 1
                elif i == 2:
                    arrow_pos = 2
                    text_pos = 3
                ax.plot([prev_vuj, prev_vuj + vuj], [find(xs[i], y1, prev_vuj + vuj / 2)+arrow_pos, find(xs[i], y1, prev_vuj + vuj / 2)+arrow_pos], color='#34a853', linestyle='--')
                
                # Add an arrow on the left side
                ax.annotate(
                    '', xy=(prev_vuj, find(xs[i], y1, prev_vuj + vuj / 2)+arrow_pos), xytext=(prev_vuj + 0.1, find(xs[i], y1, prev_vuj + vuj / 2)+arrow_pos),
                    arrowprops=dict(facecolor='#34a853', edgecolor='#34a853', arrowstyle='-|>')
                )

                # Add an arrow on the right side
                ax.annotate(
                    '', xy=(prev_vuj + vuj, find(xs[i], y1, prev_vuj + vuj / 2)+arrow_pos), xytext=(prev_vuj + vuj - 0.1, find(xs[i], y1, prev_vuj + vuj / 2)+arrow_pos),
                    arrowprops=dict(facecolor='#34a853', edgecolor='#34a853', arrowstyle='-|>')
                )
                ax.text(prev_vuj + vuj / 2, find(xs[i], y1, prev_vuj + vuj / 2) + text_pos, str(koti), fontsize=12, color='#34a853')
                prev_vuj += vuj
            
        ax.set_xlabel('Time (seconds)')
        ax.set_ylabel('Bandwidth/Throughput (Mbps)')
        
        ax.fill_between(xs[i], y1, color="#4285f4", alpha=0.2)
        ax.fill_between(xs[i], y2, color="#ea4335", alpha=0.1)

        ax.grid(color='gray', linestyle='--', linewidth=0.2)

        ax.plot([], [], color='#34a853', linestyle='--', label='Latency (ms) as text')
        ax.legend()

        # Add subfigure labels
        # ax.text(.1, 1.05, f"({chr(97 + i)})", transform=ax.transAxes, size=16, weight='bold')

    # Set the y-axis to start from 0
    axes[0].set_ylim(bottom=0, top = 58)
    axes[1].set_ylim(bottom=0, top = 8)
    axes[2].set_ylim(bottom=0, top = 58)
    # Automatically adjust subplot parameters to give more space
    plt.tight_layout()

    # Adjust spacing manually if needed
    plt.subplots_adjust(hspace=0.5)  # Add space between plots
    # Add a common title or caption
    # plt.suptitle("Comparison of Available Bandwidth and Throughput Across Different Configurations", fontsize=16)

    # Save the combined plot to a PDF file
    plt.savefig("Plots/mptcp_"+ref +"_"+ str(timesteps) + "_timesteps.pdf", format='pdf', bbox_inches='tight')

    # Display the plot
    plt.show()

def plot_quic(xs, ys_list, latencies_list, ref, timesteps):
    fig, axes = plt.subplots(3, 1, figsize=(9, 8.5))  # Create 3 subplots vertically
    
    for i in range(3):
        y1, y2 = ys_list[i][0], ys_list[i][1]
        ax = axes[i]

        ax.plot(xs[i], y1, color="#4285f4", label='Available Bandwidth')
        if i == 0:
            ax.plot(xs[i], y2, color="#ea4335", label='Throughput by '+ref+' Link 1')
        elif i == 1:
            ax.plot(xs[i], y2, color="#ea4335", label='Throughput by '+ref+' Link 2')
        elif i == 2:
            ax.plot(xs[i], y2, color="#ea4335", label='Throughput by '+ref+' with only Link 1')

        prev_vuj = 0
        if True:
            for data in latencies_list[i]:
                koti, vuj = data[0], data[1] / 1000
                if i == 0:
                    arrow_pos = 2
                    text_pos = 3
                elif i == 1:
                    arrow_pos = 5.5
                    text_pos = 7
                elif i == 2:
                    arrow_pos = 2
                    text_pos = 3
                ax.plot([prev_vuj, prev_vuj + vuj], [find(xs[i], y1, prev_vuj + vuj / 2)+arrow_pos, find(xs[i], y1, prev_vuj + vuj / 2)+arrow_pos], color='#34a853', linestyle='--')
                
                # Add an arrow on the left side
                ax.annotate(
                    '', xy=(prev_vuj, find(xs[i], y1, prev_vuj + vuj / 2)+arrow_pos), xytext=(prev_vuj + 0.1, find(xs[i], y1, prev_vuj + vuj / 2)+arrow_pos),
                    arrowprops=dict(facecolor='#34a853', edgecolor='#34a853', arrowstyle='-|>')
                )

                # Add an arrow on the right side
                ax.annotate(
                    '', xy=(prev_vuj + vuj, find(xs[i], y1, prev_vuj + vuj / 2)+arrow_pos), xytext=(prev_vuj + vuj - 0.1, find(xs[i], y1, prev_vuj + vuj / 2)+arrow_pos),
                    arrowprops=dict(facecolor='#34a853', edgecolor='#34a853', arrowstyle='-|>')
                )
                ax.text(prev_vuj + vuj / 2, find(xs[i], y1, prev_vuj + vuj / 2) + text_pos, str(koti), fontsize=12, color='#34a853')
                prev_vuj += vuj
            
        ax.set_xlabel('Time (seconds)')
        ax.set_ylabel('Bandwidth/Throughput (Mbps)')
        
        ax.fill_between(xs[i], y1, color="#4285f4", alpha=0.2)
        ax.fill_between(xs[i], y2, color="#ea4335", alpha=0.1)

        ax.grid(color='gray', linestyle='--', linewidth=0.2)

        ax.plot([], [], color='#34a853', linestyle='--', label='Latency (ms) as text')
        ax.legend()

        # Add subfigure labels
        # ax.text(.1, 1.05, f"({chr(97 + i)})", transform=ax.transAxes, size=16, weight='bold')

    # Set the y-axis to start from 0
    axes[0].set_ylim(bottom=0, top = 58)
    axes[1].set_ylim(bottom=0, top = 138)
    axes[2].set_ylim(bottom=0, top = 58)
    # Automatically adjust subplot parameters to give more space
    plt.tight_layout()

    # Adjust spacing manually if needed
    plt.subplots_adjust(hspace=0.5)  # Add space between plots
    # Add a common title or caption
    # plt.suptitle("Comparison of Available Bandwidth and Throughput Across Different Configurations", fontsize=16)

    # Save the combined plot to a PDF file
    plt.savefig("Plots/mptcp_"+ref +"_"+ str(timesteps) + "_timesteps.pdf", format='pdf', bbox_inches='tight')

    # Display the plot
    plt.show()


def plot_reno_cubic(xs, ys_list, latencies_list, ref, tar, timesteps):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    
    for i in range(2):
        y1, y2 = ys_list[i][0], ys_list[i][1]
        ax = axes[i]

        ax.plot(xs[i], y1, color="#4285f4", label='Available Bandwidth')
        if i == 0:
            ax.plot(xs[i], y2, color="#ea4335", label='Throughput by '+ref)
        elif i == 1:
            ax.plot(xs[i], y2, color="#ea4335", label='Throughput by '+tar)

        prev_vuj = 0
        if True:
            for j, data in enumerate(latencies_list[i]):
                koti, vuj = data[0], data[1] / 1000
                if i == 0:
                    arrow_pos = 0.5 if j == 0 else 0.6
                    text_pos = 1 if j == 0 else 1.1
                elif i == 1:
                    arrow_pos = 0.5 if j == 0 else 0.6
                    text_pos = 1 if j == 0 else 1.1
                
                ax.plot([prev_vuj, prev_vuj + vuj], [find(xs[i], y1, prev_vuj + vuj / 2)+arrow_pos, find(xs[i], y1, prev_vuj + vuj / 2)+arrow_pos], color='#34a853', linestyle='--')
                
                # Add an arrow on the left side
                ax.annotate(
                    '', xy=(prev_vuj, find(xs[i], y1, prev_vuj + vuj / 2)+arrow_pos), xytext=(prev_vuj + 0.1, find(xs[i], y1, prev_vuj + vuj / 2)+arrow_pos),
                    arrowprops=dict(facecolor='#34a853', edgecolor='#34a853', arrowstyle='-|>')
                )

                # Add an arrow on the right side
                ax.annotate(
                    '', xy=(prev_vuj + vuj, find(xs[i], y1, prev_vuj + vuj / 2)+arrow_pos), xytext=(prev_vuj + vuj - 0.1, find(xs[i], y1, prev_vuj + vuj / 2)+arrow_pos),
                    arrowprops=dict(facecolor='#34a853', edgecolor='#34a853', arrowstyle='-|>')
                )
                ax.text(prev_vuj + vuj / 2, find(xs[i], y1, prev_vuj + vuj / 2) + text_pos, str(koti), fontsize=12, color='#34a853')
                prev_vuj += vuj
            
        ax.set_xlabel('Time (seconds)', fontdict={"fontsize":18})
        ax.set_ylabel('Bandwidth/Throughput (Mbps)', fontdict={"fontsize":18})

        ax.tick_params(axis='x', labelsize=16)
        ax.tick_params(axis='y', labelsize=16)
        
        ax.fill_between(xs[i], y1, color="#4285f4", alpha=0.2)
        ax.fill_between(xs[i], y2, color="#ea4335", alpha=0.1)

        ax.grid(color='gray', linestyle='--', linewidth=0.2)

        ax.plot([], [], color='#34a853', linestyle='--', label='Latency (ms) as text')
        ax.legend(fontsize=14)

        # Add subfigure labels
        # ax.text(.1, 1.05, f"({chr(97 + i)})", transform=ax.transAxes, size=16, weight='bold')

    # Set the y-axis to start from 0
    axes[0].set_xlim(left=0, right = 3.2)
    axes[1].set_xlim(left=0, right = 3.2)
    
    # Automatically adjust subplot parameters to give more space
    plt.tight_layout()

    # Adjust spacing manually if needed
    # plt.subplots_adjust(hspace=0.5)  # Add space between plots
    # Add a common title or caption
    # plt.suptitle("Comparison of Available Bandwidth and Throughput Across Different Configurations", fontsize=16)

    # Save the combined plot to a PDF file
    plt.savefig("Plots/sptcp_"+ref +"_"+tar+"_"+ str(timesteps) + "_timesteps.pdf", format='pdf', bbox_inches='tight')

    # Display the plot
    plt.show()

def plot_ns3_bbr(x, ys, latencies, ref, timesteps):
    y1, y2 = ys[0], ys[1]

    plt.figure(figsize=(10,6))

    plt.plot(x, y1, color = "#4285f4",label='Available Bandwidth')  # Plot the first y array
    plt.plot(x, y2, color = "#ea4335", label='Throughput by ' + ref)  # Plot the second y array

    # plt.axhline(y=10, color='#34a853', linestyle='--', label='Latencies (ms)')
    prev_vuj = 0
    for data in latencies:
        koti, vuj = data[0], data[1] / 1000
        # print(koti, vuj, prev_vuj, (prev_vuj + vuj) / 2)
        plt.plot([prev_vuj, prev_vuj + vuj], [find(x, y1, prev_vuj + vuj / 2)+0.25, find(x, y1, prev_vuj + vuj / 2)+0.25], color='#34a853', linestyle = '--')
        # Add an arrow on the left side
        plt.annotate(
            '', xy=(prev_vuj, find(x, y1, prev_vuj + vuj / 2)+0.25), xytext=(prev_vuj + 0.1, find(x, y1, prev_vuj + vuj / 2)+0.25),
            arrowprops=dict(facecolor='#34a853', edgecolor='#34a853', arrowstyle='-|>')
        )

        # Add an arrow on the right side
        plt.annotate(
            '', xy=(prev_vuj + vuj, find(x, y1, prev_vuj + vuj / 2)+0.25), xytext=(prev_vuj + vuj - 0.1, find(x, y1, prev_vuj + vuj / 2)+0.25),
            arrowprops=dict(facecolor='#34a853', edgecolor='#34a853', arrowstyle='-|>')
        )
        plt.text(prev_vuj + vuj / 2 - 0.1, find(x, y1, prev_vuj + vuj / 2) + 0.35, str(koti), fontsize=18, color='#34a853')
        prev_vuj += vuj
    plt.axvline(x = 0.751345, c = 'grey', ls = '--')
    plt.ylim(bottom=0, top = 11)

    # Add labels and title
    plt.xlabel('Time (seconds)', fontdict={"fontsize":22})
    plt.ylabel('Bandwidth/Throughput (Mbps)', fontdict={"fontsize":22})

    plt.tick_params(axis='x', labelsize=18)
    plt.tick_params(axis='y', labelsize=18)
    
    # Add shading between the y1 line and the x-axis
    plt.fill_between(x, y1, color="#4285f4", alpha=0.2)

    # Add shading between the y2 line and the x-axis
    plt.fill_between(x, y2, color="#ea4335", alpha=0.1)

    plt.grid(color='gray', linestyle='--', linewidth=0.2)

    # Manually add a single legend entry for the latency lines
    plt.plot([], [], color='#34a853', linestyle='--', label='Latency (ms) as text')

    # Add a legend to differentiate between y1 and y2
    plt.legend(loc='center right', fontsize=18)

    # Save the plot to a PDF file
    plt.savefig("Plots/"+ref+"_"+str(timesteps)+"_timesteps.pdf", format='pdf', bbox_inches='tight')

    # Display the plot
    plt.show()

def plot_bbr(x, ys, latencies, ref, timesteps):
    y1, y2 = ys[0], ys[1]

    plt.figure(figsize=(10,6))

    plt.plot(x, y1, color = "#4285f4",label='Available Bandwidth')  # Plot the first y array
    plt.plot(x, y2, color = "#ea4335", label='Throughput by ' + ref)  # Plot the second y array

    # plt.axhline(y=10, color='#34a853', linestyle='--', label='Latencies (ms)')
    prev_vuj = 0
    for data in latencies:
        koti, vuj = data[0], data[1] / 1000
        # print(koti, vuj, prev_vuj, (prev_vuj + vuj) / 2)
        plt.plot([prev_vuj, prev_vuj + vuj], [find(x, y1, prev_vuj + vuj / 2)+0.35, find(x, y1, prev_vuj + vuj / 2)+0.35], color='#34a853', linestyle = '--')
        # Add an arrow on the left side
        plt.annotate(
            '', xy=(prev_vuj, find(x, y1, prev_vuj + vuj / 2)+0.35), xytext=(prev_vuj + 0.1, find(x, y1, prev_vuj + vuj / 2)+0.35),
            arrowprops=dict(facecolor='#34a853', edgecolor='#34a853', arrowstyle='-|>')
        )

        # Add an arrow on the right side
        plt.annotate(
            '', xy=(prev_vuj + vuj, find(x, y1, prev_vuj + vuj / 2)+0.35), xytext=(prev_vuj + vuj - 0.1, find(x, y1, prev_vuj + vuj / 2)+0.35),
            arrowprops=dict(facecolor='#34a853', edgecolor='#34a853', arrowstyle='-|>')
        )
        plt.text(prev_vuj + vuj / 2 - 0.1, find(x, y1, prev_vuj + vuj / 2) + 0.45, str(koti), fontsize=18, color='#34a853')
        prev_vuj += vuj

    plt.ylim(bottom=0, top = 11)

    # Add labels and title
    plt.xlabel('Time (seconds)', fontdict={"fontsize":22})
    plt.ylabel('Bandwidth/Throughput (Mbps)', fontdict={"fontsize":22})

    plt.tick_params(axis='x', labelsize=18)
    plt.tick_params(axis='y', labelsize=18)
    
    # Add shading between the y1 line and the x-axis
    plt.fill_between(x, y1, color="#4285f4", alpha=0.2)

    # Add shading between the y2 line and the x-axis
    plt.fill_between(x, y2, color="#ea4335", alpha=0.1)

    plt.grid(color='gray', linestyle='--', linewidth=0.2)

    # Manually add a single legend entry for the latency lines
    plt.plot([], [], color='#34a853', linestyle='--', label='Latency (ms) as text')

    # Add a legend to differentiate between y1 and y2
    plt.legend(loc='center right', fontsize=18)

    # Save the plot to a PDF file
    plt.savefig("Plots/"+ref+"_"+str(timesteps)+"_timesteps.pdf", format='pdf', bbox_inches='tight')

    # Display the plot
    plt.show()

def plot_vegas(x, ys, latencies, ref, timesteps):
    y1, y2 = ys[0], ys[1]

    plt.figure(figsize=(10,8))

    plt.plot(x, y1, color = "#4285f4",label='Available Bandwidth')  # Plot the first y array
    plt.plot(x, y2, color = "#ea4335", label='Throughput by ' + ref)  # Plot the second y array

    # plt.axhline(y=10, color='#34a853', linestyle='--', label='Latencies (ms)')
    prev_vuj = 0
    for data in latencies:
        koti, vuj = data[0], data[1] / 1000
        # print(koti, vuj, prev_vuj, (prev_vuj + vuj) / 2)
        plt.plot([prev_vuj, prev_vuj + vuj], [find(x, y1, prev_vuj + vuj / 2)+0.35, find(x, y1, prev_vuj + vuj / 2)+0.35], color='#34a853', linestyle = '--')
        # Add an arrow on the left side
        plt.annotate(
            '', xy=(prev_vuj, find(x, y1, prev_vuj + vuj / 2)+0.35), xytext=(prev_vuj + 0.1, find(x, y1, prev_vuj + vuj / 2)+0.35),
            arrowprops=dict(facecolor='#34a853', edgecolor='#34a853', arrowstyle='-|>')
        )

        # Add an arrow on the right side
        plt.annotate(
            '', xy=(prev_vuj + vuj, find(x, y1, prev_vuj + vuj / 2)+0.35), xytext=(prev_vuj + vuj - 0.1, find(x, y1, prev_vuj + vuj / 2)+0.35),
            arrowprops=dict(facecolor='#34a853', edgecolor='#34a853', arrowstyle='-|>')
        )
        plt.text(prev_vuj + vuj / 2 - 0.1, find(x, y1, prev_vuj + vuj / 2) + 0.45, str(koti), fontsize=18, color='#34a853')
        prev_vuj += vuj

    plt.ylim(bottom=0, top = 11)

    # Add labels and title
    plt.xlabel('Time (seconds)', fontdict={"fontsize":25})
    plt.ylabel('Bandwidth/Throughput (Mbps)', fontdict={"fontsize":25})

    plt.tick_params(axis='x', labelsize=18)
    plt.tick_params(axis='y', labelsize=18)
    
    # Add shading between the y1 line and the x-axis
    plt.fill_between(x, y1, color="#4285f4", alpha=0.2)

    # Add shading between the y2 line and the x-axis
    plt.fill_between(x, y2, color="#ea4335", alpha=0.1)

    plt.grid(color='gray', linestyle='--', linewidth=0.2)

    # Manually add a single legend entry for the latency lines
    plt.plot([], [], color='#34a853', linestyle='--', label='Latency (ms) as text')

    # Add a legend to differentiate between y1 and y2
    plt.legend(loc='best', fontsize=18)

    # Save the plot to a PDF file
    plt.savefig("Plots/"+ref+"_"+str(timesteps)+"_timesteps.pdf", format='pdf', bbox_inches='tight')

    # Display the plot
    plt.show()

def plot_ns3_vegas(x, ys, latencies, ref, timesteps):
    y1, y2 = ys[0], ys[1]

    plt.figure(figsize=(10,8))

    plt.plot(x, y1, color = "#4285f4",label='Available Bandwidth')  # Plot the first y array
    plt.plot(x, y2, color = "#ea4335", label='Throughput by ' + ref)  # Plot the second y array

    # plt.axhline(y=10, color='#34a853', linestyle='--', label='Latencies (ms)')
    prev_vuj = 0
    for data in latencies:
        koti, vuj = data[0], data[1] / 1000
        # print(koti, vuj, prev_vuj, (prev_vuj + vuj) / 2)
        plt.plot([prev_vuj, prev_vuj + vuj], [find(x, y1, prev_vuj + vuj / 2)+0.35, find(x, y1, prev_vuj + vuj / 2)+0.35], color='#34a853', linestyle = '--')
        # Add an arrow on the left side
        plt.annotate(
            '', xy=(prev_vuj, find(x, y1, prev_vuj + vuj / 2)+0.35), xytext=(prev_vuj + 0.1, find(x, y1, prev_vuj + vuj / 2)+0.35),
            arrowprops=dict(facecolor='#34a853', edgecolor='#34a853', arrowstyle='-|>')
        )

        # Add an arrow on the right side
        plt.annotate(
            '', xy=(prev_vuj + vuj, find(x, y1, prev_vuj + vuj / 2)+0.35), xytext=(prev_vuj + vuj - 0.1, find(x, y1, prev_vuj + vuj / 2)+0.35),
            arrowprops=dict(facecolor='#34a853', edgecolor='#34a853', arrowstyle='-|>')
        )
        plt.text(prev_vuj + vuj / 2 - 0.2, find(x, y1, prev_vuj + vuj / 2) + 0.55, str(koti), fontsize=18, color='#34a853')
        prev_vuj += vuj

    plt.ylim(bottom=0, top = 11.5)

    # Add labels and title
    plt.xlabel('Time (seconds)', fontdict={"fontsize":25})
    plt.ylabel('Bandwidth/Throughput (Mbps)', fontdict={"fontsize":25})

    plt.tick_params(axis='x', labelsize=18)
    plt.tick_params(axis='y', labelsize=18)
    
    # Add shading between the y1 line and the x-axis
    plt.fill_between(x, y1, color="#4285f4", alpha=0.2)

    # Add shading between the y2 line and the x-axis
    plt.fill_between(x, y2, color="#ea4335", alpha=0.1)

    plt.grid(color='gray', linestyle='--', linewidth=0.2)

    # Manually add a single legend entry for the latency lines
    plt.plot([], [], color='#34a853', linestyle='--', label='Latency (ms) as text')

    # Add a legend to differentiate between y1 and y2
    plt.legend(loc='best', fontsize=18)

    # Save the plot to a PDF file
    plt.savefig("Plots/"+ref+"_"+str(timesteps)+"_timesteps.pdf", format='pdf', bbox_inches='tight')

    # Display the plot
    plt.show()

if __name__ == "__main__":
    # plot_bbr([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.0],
    #       [[0.2294921875, 0.458984375, 0.458984375, 0.458984375, 0.458984375, 0.57373046875, 0.458984375, 0.458984375, 0.458984375, 0.458984375, 0.458984375, 0.57373046875, 0.458984375, 0.458984375, 0.458984375, 0.458984375, 4.47509765625, 8.14697265625, 8.0322265625, 8.14697265625, 8.14697265625, 8.14697265625, 8.14697265625, 8.14697265625, 8.0322265625, 4.130859375, 0.458984375, 0.458984375, 0.458984375, 0.458984375], [0.02197265625, 0.43853759765625, 0.426025390625, 0.426025390625, 0.53253173828125, 0.53253173828125, 0.426025390625, 0.53253173828125, 0.426025390625, 0.426025390625, 0.53253173828125, 0.53253173828125, 0.426025390625, 0.53863525390625, 0.426025390625, 0.426025390625, 1.7041015625, 0.426025390625, 0.53253173828125, 0.426025390625, 0.6390380859375, 0.6390380859375, 0.85205078125, 0.85205078125, 0.95855712890625, 0.6390380859375, 0.430908203125, 0.426025390625, 0.53253173828125, 0.426025390625]]
    #       , [[1, 1600], [29, 900]], "BBR", 2)
    # plot_vegas([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.0, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 4.0, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 5.0, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 6.0, 6.1, 6.2, 6.3],
    #       [[1.95068359375, 3.9013671875, 3.78662109375, 3.78662109375, 3.9013671875, 3.78662109375, 3.78662109375, 3.9013671875, 3.78662109375, 3.78662109375, 3.9013671875, 3.78662109375, 3.78662109375, 4.01611328125, 7.5732421875, 7.68798828125, 7.68798828125, 7.5732421875, 7.68798828125, 7.68798828125, 7.5732421875, 7.68798828125, 7.68798828125, 7.45849609375, 6.31103515625, 6.1962890625, 6.1962890625, 6.1962890625, 6.1962890625, 6.1962890625, 6.31103515625, 6.1962890625, 6.1962890625, 6.1962890625, 6.1962890625, 6.1962890625, 6.31103515625, 6.1962890625, 6.1962890625, 6.1962890625, 6.1962890625, 7.45849609375, 8.60595703125, 8.60595703125, 8.60595703125, 8.60595703125, 8.60595703125, 8.60595703125, 8.60595703125, 8.60595703125, 8.60595703125, 8.60595703125, 8.60595703125, 8.60595703125, 8.60595703125, 8.60595703125, 8.60595703125, 8.60595703125, 8.37646484375, 3.78662109375, 3.9013671875, 3.78662109375, 3.78662109375], [0.24139404296875, 3.84033203125, 3.834228515625, 3.72772216796875, 3.94073486328125, 3.72772216796875, 3.83758544921875, 3.94073486328125, 3.72772216796875, 3.834228515625, 3.84033203125, 3.834228515625, 3.72772216796875, 4.0472412109375, 4.15374755859375, 3.3050537109375, 2.7691650390625, 3.1951904296875, 2.66265869140625, 1.9171142578125, 2.130126953125, 2.02362060546875, 0.95855712890625, 1.38458251953125, 0.85205078125, 0.53253173828125, 0.85205078125, 0.53253173828125, 0.85205078125, 0.74554443359375, 0.6390380859375, 0.95855712890625, 0.426025390625, 0.53253173828125, 0.85205078125, 0.53253173828125, 0.85205078125, 0.74554443359375, 0.6390380859375, 0.95855712890625, 0.426025390625, 0.42999267578125, 0.6390380859375, 0.95855712890625, 0.95855712890625, 0.95855712890625, 0.85205078125, 1.17156982421875, 1.17156982421875, 0.95855712890625, 0.95855712890625, 1.278076171875, 0.95855712890625, 1.0650634765625, 0.85205078125, 0.85205078125, 0.95855712890625, 0.95855712890625, 0.95855712890625, 1.59759521484375, 2.66265869140625, 3.408203125, 3.72772216796875]]
    #       , [[12, 1350], [29, 1000], [30, 1750], [24, 1750]], "Vegas", 4)
    # plot([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.0, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 4.0, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 5.0, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 6.0, 6.1, 6.2, 6.3, 6.4]
    #     ,[[1.03271484375, 2.40966796875, 2.40966796875, 2.40966796875, 2.40966796875, 2.294921875, 2.40966796875, 2.40966796875, 2.40966796875, 2.40966796875, 2.40966796875, 2.294921875, 0.57373046875, 0.458984375, 0.458984375, 0.458984375, 0.458984375, 0.458984375, 0.57373046875, 0.458984375, 0.458984375, 0.458984375, 0.458984375, 0.458984375, 0.57373046875, 0.458984375, 0.458984375, 0.458984375, 0.458984375, 0.458984375, 0.57373046875, 0.458984375, 2.40966796875, 2.40966796875, 2.40966796875, 2.40966796875, 2.40966796875, 2.294921875, 2.40966796875, 2.40966796875, 2.40966796875, 2.40966796875, 2.40966796875, 1.26220703125, 0.458984375, 0.458984375, 0.458984375, 0.458984375, 0.57373046875, 0.458984375, 0.458984375, 0.458984375, 0.458984375, 0.458984375, 0.57373046875, 0.458984375, 0.458984375, 0.458984375, 0.458984375, 0.458984375, 0.57373046875, 0.458984375, 0.458984375, 1.72119140625], [0.02227783203125, 0.0, 0.0, 0.0, 0.006103515625, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.09796142578125, 0.0, 0.0, 0.09796142578125, 0.0, 0.0, 0.0, 0.0, 0.1044464111328125, 0.0604248046875, 0.0331878662109375, 0.02655029296875, 0.0730133056640625, 0.07965087890625, 0.07965087890625, 0.0862884521484375, 0.066375732421875, 0.0504302978515625, 0.0464630126953125, 0.0464630126953125, 0.0531005859375, 0.0531005859375, 0.0531005859375, 0.039825439453125, 0.02655029296875, 0.02655029296875, 0.02655029296875, 0.02655029296875, 0.0331878662109375, 0.02655029296875, 0.02655029296875, 0.02655029296875, 0.02655029296875, 0.02655029296875, 0.0331878662109375, 0.02655029296875, 0.02655029296875, 0.02655029296875, 0.02655029296875, 0.02655029296875, 0.0331878662109375, 0.02655029296875, 0.02655029296875, 0.039825439453125]]
    #     ,[[14, 1150], [13, 2000]], "BBR Picoquic", 2)
    # plot_ns3_bbr([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3]
    #     ,[[0.97, 0.97, 0.97, 0.97, 0.97, 0.97, 1.5, 9.96, 9.96, 9.96, 9.96, 9.96, 9.96, 9.96, 9.96, 9.96, 9.96, 9.96, 9.96, 9.96, 9.96, 9.96, 9.96],[0.24432, 0.48288, 0.60216, 0.673728, 0.72144, 0.909806, 1.29108, 1.32096, 1.33286, 1.35351, 1.35072, 1.33913, 1.33776, 1.32858, 1.32054, 1.30639, 1.28715, 1.27624, 1.26643, 1.25184, 1.23857, 1.22125, 1.20536]]
    #     ,[[5.95, 680], [1.74, 1814]], "BBR_NS3", 2) #Ns3 bbr
    # plot_ns3_vegas([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 4, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8]
    #     ,[[3.62, 3.62, 3.62, 3.62, 3.62, 9.85, 9.85, 9.85, 9.85, 9.85, 9.99, 9.99, 9.99, 9.99, 9.99, 9.99, 9.99, 9.99, 9.99, 9.99, 9.99, 9.99, 9.99, 9.99, 9.99, 9.99, 9.99, 9.99, 9.99, 9.96, 9.96, 9.96, 9.96, 9.96, 9.96, 9.96, 9.96, 9.96, 9.96, 9.96, 9.96, 9.96, 9.96, 9.96, 9.96, 9.96, 9.96, 9.96],[1.14432, 2.00288, 2.40216, 2.64173, 2.68144, 2.43552, 2.31108, 2.13429, 1.96886, 1.87715, 1.76072, 1.6622, 1.58633, 1.57658, 1.52304, 1.48286, 1.44048, 1.42782, 1.38043, 1.33755, 1.30403, 1.28385, 1.25536, 1.23395, 1.23264, 1.22699, 1.20888, 1.18788, 1.18429, 1.16157, 1.15527, 1.14572, 1.14731, 1.1591, 1.14691, 1.14834, 1.14339, 1.12638, 1.12222, 1.12119, 1.11735, 1.12764, 1.11838, 1.12019, 1.11671, 1.10316, 1.10268, 1.09977]]
    #     ,[[1.13, 560], [26.89, 500], [28.77, 1889.1], [19.89, 1981.64]], "Vegas_NS3", 4) #Ns3 vegas
    # plot_three([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9]
    #     ,[
    #         [[39.825439453125, 40.62652587890625, 40.5120849609375, 40.5120849609375, 40.5120849609375, 40.5120849609375, 40.5120849609375, 40.5120849609375, 40.62652587890625, 40.5120849609375, 40.5120849609375, 40.5120849609375, 40.5120849609375, 40.5120849609375, 40.5120849609375, 40.62652587890625, 40.5120849609375, 40.5120849609375, 40.5120849609375], [0.00396728515625, 0.0, 0.0, 0.00335693359375, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.00579833984375, 1.15631103515625, 2.3004150390625, 4.58984375, 10.2996826171875, 17.1661376953125, 0.57220458984375, 0.0, 0.34332275390625]]
    #         ,
    #         [[0.457763671875, 0.457763671875, 0.457763671875, 0.457763671875, 0.457763671875, 0.457763671875, 0.57220458984375, 0.457763671875, 0.457763671875, 0.457763671875, 0.457763671875, 0.457763671875, 0.57220458984375, 0.457763671875, 0.457763671875, 0.457763671875, 0.457763671875, 0.457763671875, 0], [0.00396728515625, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.03570556640625, 0.2288818359375, 0.457763671875, 0.457763671875, 0.457763671875, 0.457763671875, 0]]
    #         ,
    #         [[24.89990234375, 40.6201171875, 40.73486328125, 40.6201171875, 40.6201171875, 40.6201171875, 40.6201171875, 40.6201171875, 40.6201171875, 0,0,0,0,0,0,0,0,0,0], [0.02197265625, 0.0, 3.20770263671875, 4.05059814453125, 5.118408203125, 10.54412841796875, 17.99957275390625, 24.17694091796875, 26.94610595703125, 0,0,0,0,0,0,0,0,0,0]]
    #     ]
    #     ,[[5, 1900]], "Vegas", 1) #MPTCP vegas
    # plot_olia([
    #             [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8]
    #            ,
    #            [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8]
    #            ,
    #            [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8]
    #     ]   
    #     ,[
    #         [[46.234130859375, 46.234130859375, 46.234130859375, 46.34857177734375, 49.09515380859375, 49.09515380859375, 49.09515380859375, 49.09515380859375, 49.09515380859375, 49.2095947265625, 49.09515380859375, 49.09515380859375, 47.49298095703125, 49.09515380859375, 49.09515380859375, 49.09515380859375, 49.09515380859375, 49.09515380859375, 49.09515380859375, 49.09515380859375, 49.09515380859375, 49.09515380859375, 49.09515380859375, 49.09515380859375, 49.09515380859375, 46.234130859375, 46.34857177734375, 49.09515380859375], [25.11138916015625, 46.234130859375, 46.234130859375, 46.34857177734375, 0.91552734375, 11.55853271484375, 0.11444091796875, 10.87188720703125, 0.11444091796875, 10.41412353515625, 0.2288818359375, 10.07080078125, 6.866455078125, 44.407958984375, 46.0052490234375, 23.5748291015625, 0.11444091796875, 0.34332275390625, 0.457763671875, 0.57220458984375, 14.0869140625, 28.95355224609375, 0.457763671875, 0.57220458984375, 0.34332275390625, 0.34332275390625, 0.457763671875, 0.0]]
    #         ,
    #         [[0.91552734375, 0.91552734375, 0.91552734375, 1.02996826171875, 4.3487548828125, 4.23431396484375, 4.3487548828125, 4.23431396484375, 4.3487548828125, 4.23431396484375, 4.3487548828125, 4.23431396484375, 2.40325927734375, 1.02996826171875, 0.91552734375, 0.91552734375, 1.02996826171875, 0.91552734375, 0.91552734375, 1.02996826171875, 0.91552734375, 0.91552734375, 1.02996826171875, 0.91552734375, 0.91552734375, 1.02996826171875, 1.02996826171875, 4.23431396484375], [0.00396728515625, 0.01739501953125, 0.0, 0.018310546875, 0.0, 2.40325927734375, 2.40325927734375, 3.8909912109375, 4.3487548828125, 4.23431396484375, 4.3487548828125, 4.23431396484375, 2.40325927734375, 1.02996826171875, 0.91552734375, 0.91552734375, 1.02996826171875, 0.91552734375, 0.91552734375, 1.02996826171875, 0.91552734375, 0.91552734375, 1.02996826171875, 0.91552734375, 0.91552734375, 1.02996826171875, 1.02996826171875, 4.23431396484375]]
    #         ,
    #         [[46.234130859375, 46.234130859375, 46.234130859375, 46.34857177734375, 49.09515380859375, 49.09515380859375, 49.09515380859375, 49.09515380859375, 49.09515380859375, 49.2095947265625, 49.09515380859375, 49.09515380859375, 47.49298095703125, 49.09515380859375, 49.09515380859375, 49.09515380859375, 49.09515380859375, 49.09515380859375, 49.09515380859375, 49.09515380859375, 49.09515380859375, 49.09515380859375, 49.09515380859375, 49.09515380859375, 49.09515380859375, 46.234130859375, 46.34857177734375, 49.09515380859375], [0.00579833984375, 18.64501953125, 46.33026123046875, 46.33026123046875, 46.436767578125, 46.33026123046875, 46.436767578125, 46.40869140625, 46.33026123046875, 46.33026123046875, 46.4227294921875, 46.33026123046875, 46.456298828125, 46.387939453125, 46.33026123046875, 49.09942626953125, 49.26849365234375, 49.31243896484375, 49.2059326171875, 49.2120361328125, 49.3231201171875, 49.2059326171875, 49.2059326171875, 47.79632568359375, 0, 0, 0, 0]]
    #     ]
    #     ,[
    #         [[2*5, 29*50],[18*5, 17*50]],
    #         [[18*5, 29*50],[14*5, 17*50]],
    #         [[2*5, 29*50],[18*5, 17*50]],
    #      ], "Olia", 2) #MPTCP olia
    # plot_lia_balia([
    #     [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.0, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 4.0, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 5.0, 5.1, 5.2, 5.3]
    #     ,
    #     [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.0, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 4.0, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 5.0, 5.1, 5.2, 5.3]
    #     ,
    #     [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.0, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 4.0, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 5.0, 5.1, 5.2, 5.3]
    #     ,
    #     [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.0, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 4.0, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 5.0, 5.1, 5.2, 5.3]
    # ]
    #     ,[
    #         [[13.84735107421875, 13.84735107421875, 13.84735107421875, 13.84735107421875, 13.84735107421875, 13.73291015625, 13.84735107421875, 13.84735107421875, 6.866455078125, 4.23431396484375, 4.3487548828125, 4.23431396484375, 4.3487548828125, 4.23431396484375, 4.3487548828125, 4.23431396484375, 4.3487548828125, 4.23431396484375, 4.3487548828125, 4.23431396484375, 4.3487548828125, 4.23431396484375, 4.3487548828125, 4.23431396484375, 4.3487548828125, 4.23431396484375, 4.3487548828125, 4.23431396484375, 4.3487548828125, 4.23431396484375, 6.6375732421875, 13.84735107421875, 13.84735107421875, 13.84735107421875, 13.73291015625, 13.84735107421875, 13.84735107421875, 13.84735107421875, 13.84735107421875, 13.84735107421875, 13.73291015625, 13.84735107421875, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [8.746337890625, 13.84735107421875, 13.84735107421875, 13.84735107421875, 13.84735107421875, 13.73291015625, 13.84735107421875, 13.84735107421875, 6.866455078125, 4.23431396484375, 4.3536376953125, 4.23431396484375, 4.3487548828125, 4.23431396484375, 4.3487548828125, 4.23431396484375, 4.3487548828125, 4.23431396484375, 4.3487548828125, 4.23431396484375, 4.3487548828125, 4.23431396484375, 4.3487548828125, 4.23431396484375, 4.3487548828125, 4.23431396484375, 4.3487548828125, 4.23431396484375, 4.3487548828125, 4.23828125, 6.6375732421875, 13.84735107421875, 13.84735107421875, 13.84735107421875, 13.73291015625, 13.84735107421875, 13.84735107421875, 13.84735107421875, 13.84735107421875, 13.84735107421875, 13.73291015625, 13.84735107421875, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
    #         ,
    #         [[53.90167236328125, 53.90167236328125, 53.90167236328125, 53.90167236328125, 53.90167236328125, 53.7872314453125, 53.90167236328125, 53.90167236328125, 50.811767578125, 49.6673583984375, 49.55291748046875, 49.55291748046875, 49.6673583984375, 49.55291748046875, 49.55291748046875, 49.6673583984375, 49.55291748046875, 49.55291748046875, 49.6673583984375, 49.55291748046875, 49.55291748046875, 49.6673583984375, 49.55291748046875, 49.55291748046875, 49.6673583984375, 49.55291748046875, 49.55291748046875, 49.6673583984375, 49.55291748046875, 49.55291748046875, 50.46844482421875, 53.7872314453125, 53.90167236328125, 53.90167236328125, 53.90167236328125, 53.90167236328125, 53.90167236328125, 53.7872314453125, 53.90167236328125, 53.90167236328125, 53.90167236328125, 53.90167236328125, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0.00732421875, 0.01739501953125, 0.0, 0.018310546875, 0.0, 2.40325927734375, 0.0, 5.83648681640625, 0.0, 11.6729736328125, 25.8636474609375, 49.55291748046875, 49.6673583984375, 49.48699951171875, 49.55291748046875, 49.6673583984375, 49.55291748046875, 49.55291748046875, 49.6673583984375, 49.55291748046875, 49.55291748046875, 49.6673583984375, 49.55291748046875, 49.55291748046875, 49.6673583984375, 49.55291748046875, 49.55291748046875, 49.6673583984375, 49.556884765625, 49.55291748046875, 50.46844482421875, 53.7872314453125, 22.88818359375, 53.44390869140625, 23.46038818359375, 52.8717041015625, 24.0325927734375, 52.07061767578125, 24.0325927734375, 51.84173583984375, 24.261474609375, 51.4984130859375, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
    #         ,
    #         [[13.84735107421875, 13.84735107421875, 13.84735107421875, 13.84735107421875, 13.84735107421875, 13.73291015625, 13.84735107421875, 13.84735107421875, 7.32421875, 4.23431396484375, 4.3487548828125, 4.23431396484375, 4.3487548828125, 4.23431396484375, 4.3487548828125, 4.23431396484375, 4.3487548828125, 4.23431396484375, 4.3487548828125, 4.23431396484375, 4.3487548828125, 4.23431396484375, 4.3487548828125, 4.23431396484375, 4.3487548828125, 4.23431396484375, 4.3487548828125, 4.23431396484375, 4.3487548828125, 4.23431396484375, 6.1798095703125, 13.84735107421875, 13.84735107421875, 13.84735107421875, 13.73291015625, 13.84735107421875, 13.84735107421875, 13.84735107421875, 13.84735107421875, 13.84735107421875, 13.73291015625, 13.84735107421875, 13.84735107421875, 13.84735107421875, 13.84735107421875, 13.84735107421875, 13.73291015625, 13.84735107421875, 13.84735107421875, 11.90185546875, 4.23431396484375, 4.3487548828125, 4.23431396484375], [8.8641357421875, 13.84735107421875, 13.84735107421875, 13.84735107421875, 13.84735107421875, 13.73291015625, 13.84735107421875, 13.84735107421875, 7.32421875, 4.23431396484375, 4.3487548828125, 4.23431396484375, 4.3487548828125, 4.23431396484375, 4.3487548828125, 4.23431396484375, 4.3487548828125, 4.23431396484375, 4.3487548828125, 4.23431396484375, 4.3487548828125, 4.23431396484375, 4.3487548828125, 4.23431396484375, 3.8958740234375, 4.23431396484375, 4.3487548828125, 4.23431396484375, 4.3487548828125, 4.23431396484375, 6.1798095703125, 13.84735107421875, 13.84735107421875, 13.84735107421875, 13.73291015625, 13.81683349609375, 10.8758544921875, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]
    #         ,
    #         [[53.90167236328125, 53.90167236328125, 53.90167236328125, 53.90167236328125, 53.90167236328125, 53.90167236328125, 53.7872314453125, 53.90167236328125, 51.0406494140625, 49.55291748046875, 49.6673583984375, 49.55291748046875, 49.55291748046875, 49.6673583984375, 49.55291748046875, 49.55291748046875, 49.6673583984375, 49.55291748046875, 49.55291748046875, 49.6673583984375, 49.55291748046875, 49.55291748046875, 49.6673583984375, 49.55291748046875, 49.55291748046875, 49.6673583984375, 49.55291748046875, 49.55291748046875, 49.6673583984375, 49.55291748046875, 50.23956298828125, 53.90167236328125, 53.7872314453125, 53.90167236328125, 53.90167236328125, 53.90167236328125, 53.90167236328125, 53.90167236328125, 53.7872314453125, 53.90167236328125, 53.90167236328125, 53.90167236328125, 53.90167236328125, 53.90167236328125, 53.7872314453125, 53.90167236328125, 53.90167236328125, 53.90167236328125, 53.90167236328125, 53.1005859375, 49.6673583984375, 49.55291748046875, 49.55291748046875], [0.00732421875, 0.01739501953125, 0.0, 0.018310546875, 0.0, 2.74658203125, 0.0, 5.7220458984375, 2.9754638671875, 16.021728515625, 27.2369384765625, 25.8636474609375, 2.17437744140625, 2.17437744140625, 2.0599365234375, 43.73565673828125, 19.79827880859375, 2.17437744140625, 2.0599365234375, 2.86102294921875, 3.08990478515625, 2.0599365234375, 2.288818359375, 2.288818359375, 2.0599365234375, 38.94500732421875, 44.86083984375, 44.40704345703125, 0.0, 0.0, 0.0, 0.0, 11.2152099609375, 53.90167236328125, 8.81195068359375, 7.66754150390625, 6.866455078125, 0.0, 0.11444091796875, 0.0, 0.0, 0.11444091796875, 0.0, 0.0, 0.11444091796875, 0.0, 0.11444091796875, 0.0, 0.11444091796875, 0.0, 0.11444091796875, 0.11444091796875, 0.11444091796875]]
    #     ]
    #     ,[
    #         [[3*5, 38*50],[1*5, 45*50]],
    #         [[20*5, 38*50],[9*5, 45*50]],
    #         [[3*5, 38*50],[1*5, 45*50]],
    #         [[20*5, 38*50],[9*5, 45*50]],
    #      ], "Lia", "Balia", 2) #MPTCP lia vs balia 2
    plot_reno_cubic([
        [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.0, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 4.0]
        ,
        [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.0, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 4.0]
    ]
        ,[
            [[0.34423828125, 1.03271484375, 0.91796875, 0.91796875, 1.03271484375, 0.91796875, 0.91796875, 1.03271484375, 0.91796875, 0.91796875, 1.03271484375, 25.9326171875, 57.373046875, 57.373046875, 57.373046875, 57.373046875, 57.373046875, 57.373046875, 57.373046875, 57.373046875, 57.373046875, 57.373046875, 57.373046875, 57.373046875, 57.373046875, 57.373046875, 32.24365234375, 1.03271484375, 0.91796875, 0.91796875, 1.03271484375, 0.91796875, 0.91796875, 1.03271484375, 0.91796875, 0.91796875, 1.03271484375, 25.9326171875, 57.373046875, 57.373046875], [0.02197265625, 0.751953125, 0.95855712890625, 0.85205078125, 1.0650634765625, 0.95855712890625, 0.85205078125, 1.0711669921875, 0.85205078125, 0.95855712890625, 1.0650634765625, 5.33477783203125, 0.00335693359375, 5.1123046875, 0.0, 12.67425537109375, 0.0, 12.5677490234375, 0.10650634765625, 23.431396484375, 14.2718505859375, 23.53790283203125, 51.01654052734375, 22.89886474609375, 57.40692138671875, 56.661376953125, 32.20245361328125, 1.0650634765625, 0.85205078125, 0.95855712890625, 1.0650634765625, 0.85205078125, 0.95855712890625, 0.95855712890625, 0.95855712890625, 0.95855712890625, 0.95855712890625, 25.948486328125, 57.40692138671875, 25.35247802734375]]
            ,
            [[0.458984375, 1.03271484375, 0.91796875, 0.91796875, 1.03271484375, 0.91796875, 0.91796875, 1.03271484375, 0.91796875, 0.91796875, 1.03271484375, 32.70263671875, 57.373046875, 57.373046875, 57.373046875, 57.373046875, 57.373046875, 57.373046875, 57.373046875, 57.373046875, 57.373046875, 57.373046875, 57.373046875, 57.373046875, 57.373046875, 57.373046875, 25.4736328125, 1.03271484375, 0.91796875, 0.91796875, 1.03271484375, 0.91796875, 0, 0, 0, 0, 0, 0, 0, 0], [0.02197265625, 0.751953125, 0.95855712890625, 0.85205078125, 1.0650634765625, 0.858154296875, 0.95855712890625, 1.0650634765625, 0.858154296875, 0.95855712890625, 1.0650634765625, 3.092041015625, 0.2130126953125, 2.7691650390625, 0.31951904296875, 2.7691650390625, 0.426025390625, 2.7691650390625, 0.6390380859375, 2.87567138671875, 0.6390380859375, 3.08868408203125, 0.6390380859375, 3.08868408203125, 0.85205078125, 3.1951904296875, 0.74554443359375, 0.95855712890625, 0.95855712890625, 0.95855712890625, 0.96343994140625, 0.95855712890625, 0, 0, 0, 0, 0, 0, 0, 0]]
        ]
        ,[
            [[4*5, 22*50],[20*5, 30*50]],
            [[4*5, 22*50],[20*5, 30*50]]
         ], "Reno", "Cubic", 2) #SPTCP reno vs cubic 2
    #     plot_two([
    #     [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9]
    #     ,
    #     [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7]
    # ]
    #     ,[
    #         [[93.8623046875, 135.74462890625, 135.859375, 135.74462890625, 135.74462890625, 138.26904296875, 147.79296875, 135.74462890625, 135.74462890625, 135.859375, 135.74462890625, 150.20263671875, 135.74462890625, 135.859375, 135.74462890625, 135.74462890625, 138.26904296875, 147.79296875, 135.74462890625], [0.0665283203125, 0.0, 0.0, 0.04425048828125, 0.0, 0.0, 0.0, 0.0, 0.04425048828125, 0.006103515625, 0.0, 0.0, 0.0, 0.2591705322265625, 1.116943359375, 11.06964111328125, 60.05035400390625, 108.71391296386719, 80.72616577148438]]
    #         ,
    #         [[93.8623046875, 135.74462890625, 135.859375, 135.74462890625, 135.74462890625, 138.26904296875, 147.79296875, 135.74462890625, 135.74462890625, 135.859375, 135.74462890625, 150.20263671875, 135.74462890625, 135.859375, 135.74462890625, 135.74462890625, 138.26904296875, 147.79296875, 135.74462890625, 135.74462890625, 135.859375, 135.74462890625, 150.20263671875, 135.74462890625, 135.859375, 135.74462890625, 135.74462890625], [0.0604248046875, 0.006103515625, 0.0, 0.04425048828125, 0.0, 0.0, 0.006103515625, 0.0, 0.2591705322265625, 1.02081298828125, 4.3164825439453125, 18.92333984375, 19.813461303710938, 15.77178955078125, 19.49432373046875, 18.80859375, 18.90655517578125, 21.788177490234375, 15.974349975585938, 17.53509521484375, 18.90655517578125, 17.33917236328125, 22.449951171875, 16.477737426757812, 15.8697509765625, 18.031539916992188, 16.065673828125]]
    #     ]
    #     ,[
    #         [[12*1, 1*50],[26*1, 10*50], [12*1, 1*50],[26*1, 10*50], [12*1, 1*50],[26*1, 10*50], [12*1, 1*50],[26*1, 10*50]],
    #         [[12*1, 1*50],[26*1, 10*50], [12*1, 1*50],[26*1, 10*50], [12*1, 1*50],[26*1, 10*50], [12*1, 1*50],[26*1, 10*50]],
    #      ], "BBR v1", "BBR v3", 2) #Picoquic bbr v1 vs bbr v3 2
    # plot_quic([
    #             [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9]
    #            ,
    #            [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9]
    #            ,
    #            [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9]
    #     ]
    #     ,[
    #         [[25.244140625, 30.5224609375,  50.01068115234375, 50.01068115234375, 49.78179931640625, 50.01068115234375, 50.01068115234375, 49.896240234375, 50.01068115234375, 50.01068115234375, 49.78179931640625, 50.01068115234375, 50.01068115234375, 49.896240234375, 50.01068115234375, 49.896240234375, 49.896240234375, 50.01068115234375, 49.896240234375, 50.01068115234375, 50.01068115234375, 49.78179931640625, 50.01068115234375, 50.01068115234375, 49.896240234375, 50.01068115234375, 50.01068115234375, 49.78179931640625, 50.01068115234375], [0.0482177734375, 0.0, 0.04425048828125, 0.0, 0.0, 0.0, 0.0, 0.259857177734375, 0.0199127197265625, 0.1183319091796875, 0.0, 0.0, 0.0, 0.0, 0.88165283203125, 0.1959228515625, 1.27349853515625, 1.07757568359375, 1.27349853515625, 1.175537109375, 1.3714599609375, 1.46942138671875, 1.5673828125, 1.7633056640625, 1.959228515625, 2.05718994140625, 2.25311279296875, 1.678924560546875, 0.0754547119140625]]
    #         ,
    #         [[100.68292236328125, 116.38641357421875, 116.27197265625, 116.38641357421875, 116.27197265625, 116.27197265625, 116.38641357421875, 116.27197265625, 116.38641357421875, 116.27197265625, 116.38641357421875, 116.27197265625, 116.38641357421875, 116.27197265625, 116.38641357421875, 116.27197265625, 116.38641357421875, 116.27197265625, 116.38641357421875, 116.27197265625, 116.38641357421875, 116.27197265625, 116.27197265625, 116.38641357421875, 116.27197265625, 116.38641357421875, 116.27197265625, 116.38641357421875, 116.27197265625], [0.00396728515625, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.09796142578125, 0.0, 0.0, 0.09796142578125, 1.19232177734375, 0.09796142578125, 2.75665283203125, 4.21234130859375, 5.48583984375, 9.012451171875, 11.9512939453125, 16.065673828125, 22.1392822265625, 30.172119140625, 41.143798828125, 56.033935546875, 76.70379638671875, 103.055419921875]]
    #         ,
    #         [[25.244140625, 30.5224609375, 50.14404296875, 50.14404296875, 50.029296875, 50.029296875, 50.14404296875, 50.029296875, 50.14404296875, 50.14404296875, 50.029296875, 50.029296875, 50.14404296875, 50.029296875, 50.14404296875, 50.029296875, 50.14404296875, 50.029296875, 50.029296875, 50.029296875, 50.029296875, 50.029296875, 50.029296875, 50.029296875, 50.029296875, 50.029296875, 50.029296875, 50.029296875, 50.029296875], [0.0, 0.04425048828125, 0.0, 0.04425048828125, 0.0, 0.01617431640625, 0.0, 0.0, 0.2591705322265625, 0.0376129150390625, 1.2872314453125, 33.50975036621094, 44.96429443359375, 50.010528564453125, 50.16288757324219, 50.05828857421875, 50.15625, 49.9603271484375, 50.05828857421875, 50.029296875, 50.029296875, 50.029296875, 50.029296875, 50.029296875, 50.029296875, 50.029296875, 50.029296875, 50.029296875, 50.029296875]]
    #     ]
    #     ,[
    #         [[8*5, 17*170]],
    #         [[34*5, 17*170]],
    #         [[8*5, 17*110]]
    #      ], "MPQUIC", 1) #MPTCP quic 2